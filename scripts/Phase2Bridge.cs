// SPDX-License-Identifier: GPL-3.0-or-later
// Read-only TweakDB extraction using the installed WolvenKit parser.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Globalization;
using System.IO.Compression;
using WolvenKit.Common.Services;
using WolvenKit.Common.Conversion;
using WolvenKit.RED4.TweakDB;
using WolvenKit.RED4.CR2W.JSON;
using WolvenKit.RED4.Types;
using WolvenKit.RED4.Archive.IO;
using System.Collections.Generic;

// WolvenKit ReadCHandle<T> casts a dynamic class before CHandle.SetValue can
// preserve it. Use its existing DynamicChunk support instead. No invented RTTI.
// Based on WolvenKit.RED4/Types/IO/Red4Reader.cs (GPL-3.0-or-later).
public sealed class NcaResourceReader : CR2WReader {
    public NcaResourceReader(Stream input):base(input) {}
    public override IRedHandle ReadCHandle<T>() {
        var pointer=BaseReader.ReadInt32()-1;
        RedBaseClass instance=null;
        if(pointer>=0){instance=_chunks[pointer].Instance;_chunks[pointer].IsUsed=true;}
        return new CHandle<T>(instance);
    }
}

// JSON cannot represent IEEE non-finite numbers. Preserve their symbolic value
// as a string rather than replacing it with a fabricated numeric coordinate.
public sealed class NcaFloatConverter : JsonConverter<CFloat> {
    public static int NonFiniteCount;
    public override CFloat Read(ref Utf8JsonReader reader,Type type,JsonSerializerOptions options) => throw new NotSupportedException("Read-only export converter");
    public override void Write(Utf8JsonWriter writer,CFloat value,JsonSerializerOptions options) {
        float f=value;
        if(float.IsFinite(f))writer.WriteNumberValue(f);
        else {writer.WriteStringValue(f.ToString(CultureInfo.InvariantCulture));NonFiniteCount++;}
    }
}

public static class Phase2Bridge {
    public class Request {public string archive{get;set;} public string hash{get;set;}}
    static void Collect(JsonElement node,string pointer,List<object> fields,Dictionary<string,int> types) {
        if(node.ValueKind==JsonValueKind.Object) {
            bool typedValue=false;
            if(node.TryGetProperty("$type",out var type)) {
                var name=type.GetString();if(name!=null)types[name]=types.GetValueOrDefault(name)+1;
                if(name is "TweakDBID" or "ResourcePath" or "CName" or "NodeRef") {
                    if(node.TryGetProperty("$value",out var value) && value.ValueKind==JsonValueKind.String){fields.Add(new{pointer=pointer+"/$value",value=value.GetString(),red_type=name});typedValue=true;}
                }
            }
            foreach(var property in node.EnumerateObject()) {
                if(property.Name is "$type" or "$storage" or "HandleId" or "HandleRefId" or "BufferId" or "Flags")continue;
                if(typedValue&&property.Name=="$value")continue;
                Collect(property.Value,pointer+"/"+property.Name.Replace("~","~0").Replace("/","~1"),fields,types);
            }
        } else if(node.ValueKind==JsonValueKind.Array) {
            int index=0;foreach(var item in node.EnumerateArray())Collect(item,pointer+"/"+(index++),fields,types);
        } else if(node.ValueKind==JsonValueKind.String) {
            var value=node.GetString();
            if(!string.IsNullOrWhiteSpace(value)&&value!="None"&&value!="PLATFORM_PC"&&value.Length<=4096)
                fields.Add(new{pointer,value});
        }
    }
    public static void ScanResources(string game,string requestFile,string output,long maxOutputBytes,bool parseBuffers=true) {
        var fullGame=Path.GetFullPath(game).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;
        if(Path.GetFullPath(output).StartsWith(fullGame,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("Output in source game is forbidden");
        Directory.CreateDirectory(output);WolvenKit.Core.Compression.Oodle.Load();
        RedJsonSerializer.Options.Converters.Insert(0,new NcaFloatConverter());
        var hashes=new HashService();hashes.Loaded.GetAwaiter().GetResult();
        var reader=new ArchiveReader();var requests=JsonSerializer.Deserialize<List<Request>>(File.ReadAllText(requestFile));
        using var errors=new StreamWriter(Path.Combine(output,"errors.jsonl"),true);
        foreach(var group in requests.GroupBy(x=>x.archive)) {
            var dest=Path.Combine(output,group.Key.Replace('/','_').Replace('\\','_')+".jsonl.gz");
            if(File.Exists(dest)){Console.WriteLine("Cached "+group.Key);continue;}
            var input=Path.GetFullPath(Path.Combine(game,group.Key));
            if(!input.StartsWith(fullGame,StringComparison.OrdinalIgnoreCase))throw new InvalidOperationException("Invalid archive path");
            var result=reader.ReadArchive(input,hashes,out var archive);if((int)result!=0)throw new InvalidDataException("Archive read error");
            int count=0,failed=0;
            using(var disk=File.Create(dest+".partial"))
            using(var zipped=new GZipStream(disk,CompressionLevel.Fastest))
            using(var writer=new StreamWriter(zipped,new UTF8Encoding(false))) {
                foreach(var request in group) {
                    try {
                        var entry=archive.Index.FileEntries[ulong.Parse(request.hash)];
                        if(entry.Size>100000000)throw new InvalidDataException("Resource exceeds bounded 100 MB parser input");
                        using var bytes=new MemoryStream();entry.Extract(bytes);bytes.Position=0;
                        var adjustments=new List<string>();
                        using var cr=new NcaResourceReader(bytes);
                        cr.ParsingError+=e=>{
                            // Use upstream compatibility conversions, but never
                            // replace an unknown enum with its default value.
                            if(e is InvalidEnumValueEventArgs)return false;
                            var handled=TypeGlobal.OnParsingError(e);
                            if(handled && e is InvalidRTTIEventArgs r)adjustments.Add(r.PropertyName+": "+r.ActualType+" -> "+r.ExpectedType);
                            return handled;
                        };
                        var status=cr.ReadFile(out var file,parseBuffers);if((int)status!=0||file==null)throw new InvalidDataException("CR2W status "+status);
                        NcaFloatConverter.NonFiniteCount=0;
                        using var json=JsonDocument.Parse(RedJsonSerializer.Serialize(new RedFileDto(file)),new JsonDocumentOptions{MaxDepth=2048});
                        var fields=new List<object>();var types=new Dictionary<string,int>();Collect(json.RootElement,"",fields,types);
                        writer.WriteLine(JsonSerializer.Serialize(new{request.archive,request.hash,path=entry.Name,parse_buffers=parseBuffers,nonfinite_floats=NcaFloatConverter.NonFiniteCount,compatibility_adjustments=adjustments,fields,types}));count++;
                        if(count%250==0){writer.Flush();Console.WriteLine(group.Key+": "+count);}
                    }catch(Exception ex){failed++;errors.WriteLine(JsonSerializer.Serialize(new{request.archive,request.hash,error=ex.Message}));errors.Flush();if(failed==1)Console.WriteLine(ex.ToString());}
                    if(count%100==0 && Directory.EnumerateFiles(output).Sum(x=>new FileInfo(x).Length)>maxOutputBytes)throw new IOException("Phase 2 compact extraction budget exceeded");
                }
            }
            File.Move(dest+".partial",dest);archive.ReleaseFileHandle();
            Console.WriteLine(JsonSerializer.Serialize(new{archive=group.Key,decoded=count,failed}));
        }
    }
    public static void Tweaks(string source, string output) {
        if(Path.GetFullPath(output).StartsWith(Path.GetDirectoryName(Path.GetFullPath(source))+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Output cannot be inside the source directory");
        var hashes=new HashService();hashes.Loaded.GetAwaiter().GetResult();
        using var stream=File.OpenRead(source);
        using var reader=new TweakDBReader(stream);
        var status=reader.ReadFile(out var db);
        if((int)status!=0 || db==null)throw new InvalidDataException("TweakDB read status "+status);
        using var disk=File.Create(output);
        using var compressed=new GZipStream(disk,CompressionLevel.Fastest);
        using var writer=new StreamWriter(compressed,new UTF8Encoding(false));
        int records=0,flats=0;
        foreach(var (id,type) in db.Records) {
            writer.WriteLine(JsonSerializer.Serialize(new{kind="record",id=((ulong)id).ToString(),name=id.ResolvedText,type=type.Name}));records++;
        }
        foreach(var (id,value) in db.Flats) {
            // LocKeyWrapper stores Key in a public field; the default JSON
            // serializer omits it and would silently produce an empty object.
            string serialized=value is gamedataLocKeyWrapper key
                ? JsonSerializer.Serialize(new{type="gamedataLocKeyWrapper",key=key.Key.ToString()})
                : RedJsonSerializer.Serialize(value);
            using var json=JsonDocument.Parse(serialized);
            writer.WriteLine(JsonSerializer.Serialize(new{kind="flat",id=((ulong)id).ToString(),name=id.ResolvedText,type=value.GetType().Name,value=json.RootElement}));flats++;
        }
        foreach(var id in db.GetQueries()) {
            var values=db.Queries.GetQuery((ulong)id);
            writer.WriteLine(JsonSerializer.Serialize(new{kind="query",id=((ulong)id).ToString(),name=id.ResolvedText,values=values.Select(x=>new{id=((ulong)x).ToString(),name=x.ResolvedText})}));
        }
        Console.WriteLine(JsonSerializer.Serialize(new{source=Path.GetFileName(source),records,flats}));
    }
}
