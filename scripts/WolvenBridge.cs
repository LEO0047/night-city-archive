// SPDX-License-Identifier: GPL-3.0-or-later
// Thin read-only adapter over WolvenKit 9.1.0; no archive format reimplementation.
using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Collections.Generic;
using System.IO.Compression;
using System.Text;
using WolvenKit.Common.Conversion;
using WolvenKit.RED4.CR2W.JSON;
using WolvenKit.Common.Services;
using WolvenKit.RED4.Archive;
using WolvenKit.RED4.Archive.IO;

public static class WolvenBridge {
    static void Guard(string game, string output) {
        var source = Path.GetFullPath(game).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        var target = Path.GetFullPath(output);
        if (target.Equals(source.TrimEnd(Path.DirectorySeparatorChar),StringComparison.OrdinalIgnoreCase) || target.StartsWith(source, StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Output inside source installation is forbidden");
    }
    public static void Index(string game, string output) {
        Guard(game, output);
        Directory.CreateDirectory(output);
        WolvenKit.Core.Compression.Oodle.Load();
        var hashes = new HashService();
        var reader = new ArchiveReader();
        using var target = new StreamWriter(Path.Combine(output,"archive-index.jsonl"));
        using var summary = new StreamWriter(Path.Combine(output,"archives.jsonl"));
        long total = 0, links = 0;
        foreach (var path in Directory.GetFiles(Path.Combine(game,"archive","pc"),"*.archive", SearchOption.AllDirectories).OrderBy(x=>x,StringComparer.Ordinal)) {
            var error = reader.ReadArchive(path, hashes, out var archive);
            if ((int)error != 0) throw new InvalidDataException(path + ": " + error);
            var relative = Path.GetRelativePath(game, path).Replace('\\','/');
            summary.WriteLine(JsonSerializer.Serialize(new {path=relative, entries=archive.Files.Count, dependencies=archive.Index.Dependencies.Count, size=new FileInfo(path).Length}));
            foreach (var file in archive.Index.FileEntries.Values) {
                var dependencies = new List<string>();
                for (uint i=file.ResourceDependenciesStart; i<file.ResourceDependenciesEnd; i++) dependencies.Add(archive.Index.Dependencies[(int)i].Hash.ToString());
                target.WriteLine(JsonSerializer.Serialize(new {archive=relative, hash=file.Key.ToString(), path=file.Name, extension=file.Extension, size=file.Size, compressed=file.ZSize, sha1=Convert.ToHexString(file.SHA1Hash).ToLowerInvariant(), dependencies}));
                total++; links += dependencies.Count;
            }
            archive.ReleaseFileHandle(); target.Flush(); summary.Flush();
            Console.WriteLine($"{Path.GetFileName(path)}: {archive.Files.Count} entries; cumulative {total} assets / {links} links");
        }
    }
    public static void Extract(string game, string requestFile, string output, long maxBytes) {
        Guard(game, output); Directory.CreateDirectory(output);
        WolvenKit.Core.Compression.Oodle.Load();
        var hashes = new HashService(); var reader = new ArchiveReader();
        var requests = JsonSerializer.Deserialize<List<Request>>(File.ReadAllText(requestFile));
        long written=Directory.EnumerateFiles(output,"*",SearchOption.AllDirectories).Sum(f=>new FileInfo(f).Length);
        using var ledger = new StreamWriter(Path.Combine(output,"extraction.jsonl"),true);
        foreach(var group in requests.GroupBy(x=>x.archive)) {
            var full = Path.GetFullPath(Path.Combine(game,group.Key));
            if (!full.StartsWith(Path.GetFullPath(game)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Invalid archive path");
            reader.ReadArchive(full,hashes,out var archive);
            foreach(var request in group) {
                var entry=archive.Index.FileEntries[ulong.Parse(request.hash)];
                var dest=Path.Combine(output,request.hash+entry.Extension);
                if(File.Exists(dest)) continue;
                if(written+entry.Size>maxBytes) throw new IOException("Extraction storage budget exceeded");
                using(var stream=File.Create(dest)) entry.Extract(stream);
                written+=new FileInfo(dest).Length;
                ledger.WriteLine(JsonSerializer.Serialize(new{request.archive,request.hash,path=entry.Name,file=Path.GetFileName(dest),size=new FileInfo(dest).Length})); ledger.Flush();
            }
            archive.ReleaseFileHandle();
            Console.WriteLine($"Extracted {group.Count()} resources from {group.Key}");
        }
    }
    public class Request { public string archive {get;set;} public string hash {get;set;} }
    public static void Decode(string game, string requestFile, string output, long maxBytes) {
        Guard(game,output); Directory.CreateDirectory(output);
        WolvenKit.Core.Compression.Oodle.Load();
        var hashes=new HashService();var reader=new ArchiveReader();
        var requests=JsonSerializer.Deserialize<List<Request>>(File.ReadAllText(requestFile));
        using var errors=new StreamWriter(Path.Combine(output,"errors.jsonl"),true);
        foreach(var group in requests.GroupBy(x=>x.archive)) {
            var name=group.Key.Replace('/','_').Replace('\\','_')+".jsonl.gz";
            var dest=Path.Combine(output,name);
            if(File.Exists(dest)) {Console.WriteLine("Cached "+name);continue;}
            if(Directory.EnumerateFiles(output,"*",SearchOption.AllDirectories).Sum(f=>new FileInfo(f).Length)>maxBytes) throw new IOException("Decoded data budget exceeded");
            var full=Path.GetFullPath(Path.Combine(game,group.Key));
            if (!full.StartsWith(Path.GetFullPath(game)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("Invalid archive path");
            reader.ReadArchive(full,hashes,out var archive);
            int count=0,fail=0;
            using(var disk=File.Create(dest+".partial"))
            using(var zipped=new GZipStream(disk,CompressionLevel.Fastest))
            using(var writer=new StreamWriter(zipped,new UTF8Encoding(false))) {
                foreach(var request in group) {
                    try {
                        var entry=archive.Index.FileEntries[ulong.Parse(request.hash)];
                        using var bytes=new MemoryStream(); entry.Extract(bytes);bytes.Position=0;
                        string json;
                        if(bytes.Length>=4 && Encoding.ASCII.GetString(bytes.GetBuffer(),0,4)=="CR2W") {
                            using var cr=new CR2WReader(bytes);
                            // Preserve explicitly serialized default values; do not skip the field.
                            // WolvenKit reports these as parse events even though the value was read.
                            cr.ParsingError += e => e.GetType().Name == "InvalidDefaultValueEventArgs";
                            var status=cr.ReadFile(out var file);
                            if((int)status!=0 || file==null) throw new InvalidDataException("CR2W read status "+status);
                            json=RedJsonSerializer.Serialize(new RedFileDto(file));
                        } else { json=Encoding.UTF8.GetString(bytes.ToArray()); if(entry.Extension==".csv") json=JsonSerializer.Serialize(new{text=json}); }
                        using var parsed=JsonDocument.Parse(json,new JsonDocumentOptions{MaxDepth=2048});
                        writer.WriteLine(JsonSerializer.Serialize(new {request.archive,request.hash,path=entry.Name,data=parsed.RootElement},new JsonSerializerOptions{MaxDepth=2048}));
                        count++;
                        if(count%1000==0)Console.WriteLine($"{Path.GetFileName(group.Key)}: decoded {count}");
                    }catch(Exception ex){fail++;errors.WriteLine(JsonSerializer.Serialize(new{request.archive,request.hash,error=ex.ToString()}));errors.Flush();}
                }
            }
            File.Move(dest+".partial",dest);
            archive.ReleaseFileHandle();Console.WriteLine($"{group.Key}: {count} decoded, {fail} failures");
        }
    }
}
