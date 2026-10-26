"""Offline MQ027 voice inventory, conversion and explicitly machine-labelled ASR."""
import argparse,hashlib,json,os,pathlib,re,sqlite3,subprocess,sys,time,wave,zlib
from runtime import find_pwsh
ROOT=pathlib.Path(__file__).resolve().parents[1]
DB=ROOT/'data/archive.db'
OUT=ROOT/'data/phase2/audio';OUT.mkdir(exist_ok=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--transcribe',action='store_true');args=parser.parse_args()
    db=sqlite3.connect('file:'+str(DB).replace('\\','/')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    assets=[dict(r) for r in db.execute("SELECT a.*,r.path archive,r.sha256 archive_sha256 FROM assets a JOIN archives r ON r.id=a.archive_id WHERE a.extension='.wem' AND a.path LIKE '%mq027%' ORDER BY a.path")]
    maps=[]
    query="SELECT DISTINCT a.hash,a.path,r.archive_id,r.json_zlib FROM semantic_refs s JOIN assets a ON a.hash=s.source_hash JOIN resources r ON r.hash=a.hash JOIN assets t ON t.hash=s.target_hash WHERE t.path LIKE '%mq027%' AND t.extension='.wem'"
    for row in db.execute(query):
        data=json.loads(zlib.decompress(row['json_zlib']))
        for index,entry in enumerate(data['Data']['RootChunk']['root']['Data']['entries']):
            if 'mq027' in str(entry):maps.append(dict(source_hash=row['hash'],source_path=row['path'],archive_id=row['archive_id'],pointer=f'/Data/RootChunk/root/Data/entries/{index}',entry=entry))
    (OUT/'voice-map.json').write_text(json.dumps(maps,ensure_ascii=False,indent=2),encoding='utf-8')
    req=OUT/'extract-request.json';req.write_text(json.dumps([{'hash':a['hash'],'archive':a['archive']} for a in assets]),encoding='utf-8')
    pwsh=find_pwsh()
    subprocess.run([pwsh,'-NoProfile','-File',str(ROOT/'scripts/bridge.ps1'),'-Mode','extract','-RequestFile',str(req),'-Output','data/phase2/audio/raw','-MaxBytes','15000000'],cwd=ROOT,check=True)
    entries=[]
    for asset in assets:
        source=OUT/'raw'/(asset['hash']+'.wem');dest=OUT/(asset['hash']+'.wav')
        if not dest.exists():subprocess.run([str(ROOT/'tools/vgmstream-r2168/vgmstream-cli.exe'),'-o',str(dest),str(source)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
        with wave.open(str(dest)) as audio:duration=audio.getnframes()/audio.getframerate()
        matches=[]
        for mapping in maps:
            for variant in ['femaleResPath','maleResPath']:
                if mapping['entry'].get(variant,{}).get('DepotPath',{}).get('$value')==asset['path']:
                    matches.append({'string_id':mapping['entry']['stringId'],'variant':variant,'map_hash':mapping['source_hash'],'map_path':mapping['source_path'],'pointer':mapping['pointer']+'/'+variant})
        entries.append(dict(asset,seconds=round(duration,4),file=dest.name,wav_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),voice_map=matches))
    (OUT/'inventory.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'voices':len(entries),'seconds':sum(e['seconds'] for e in entries),'voice_mappings':len(maps),'linked_voices':sum(bool(e['voice_map']) for e in entries)}),flush=True)
    if not args.transcribe:return
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    from faster_whisper import WhisperModel
    model_path=pathlib.Path.home()/'.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120'
    model=WhisperModel(str(model_path),device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
    for index,entry in enumerate(entries):
        output=OUT/(entry['hash']+'.asr.json')
        if output.exists():continue
        segments,info=model.transcribe(str(OUT/entry['file']),language='en',beam_size=5,condition_on_previous_text=False,vad_filter=False)
        data={'asset_hash':entry['hash'],'source_path':entry['path'],'wav_sha256':entry['wav_sha256'],'status':'MACHINE_TRANSCRIPTION_UNREVIEWED','model':'Systran/faster-whisper-small','model_revision':model_path.name,'language':'en','segments':[{'start':s.start,'end':s.end,'text':s.text,'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob} for s in segments]}
        output.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'Transcribed {index+1}/{len(entries)}',flush=True)

if __name__=='__main__':main()
