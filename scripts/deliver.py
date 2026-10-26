"""Produce local research handoff files; no uploads or ENGRAM writes."""
import hashlib,json,time
from pathlib import Path
from catalog import ROOT,connect

def main():
    db=connect();config=json.loads((ROOT/'config.json').read_text());out=ROOT/'exports';out.mkdir(exist_ok=True)
    baseline=ROOT/'reports/game-before.jsonl';scan='NCA-SCAN-'+hashlib.sha256(baseline.read_bytes()).hexdigest()[:16].upper()
    classification={'確認遊戲內未使用':'confirmed_unused','疑似刪除內容':'suspected_cut','測試或開發殘留':'test_or_dev_remnant','證據不足':'insufficient_evidence'}
    rows=[dict(r) for r in db.execute('SELECT * FROM findings ORDER BY score DESC,id')];records=[]
    table=['# 研究候選清單','',f'掃描：`{scan}` · 遊戲 {config["game_product_version"]} · GOG build {config["gog_build"]}','', '所有候選均需連同支持證據與反證閱讀。「可能的新研究線索」沒有宣稱新穎性。','', '| 穩定 ID | 內容群 | 分類 | 資產數 | 社群 |','|---|---|---|---:|---|']
    for row in rows:
        detail=json.loads(row['details']);assets=[]
        for a in db.execute('SELECT a.*,f.role FROM finding_assets f JOIN assets a ON a.hash=f.hash WHERE f.finding_id=? ORDER BY a.hash',(row['id'],)):
            variants=[dict(v) for v in db.execute('SELECT r.path archive,r.sha256 archive_sha256,e.sha1 entry_sha1 FROM entries e JOIN archives r ON r.id=e.archive_id WHERE e.hash=? ORDER BY r.path',(a['hash'],))]
            assets.append(dict(asset_id='NCA-ASSET-'+a['hash'],path=a['path'],extension=a['extension'],role=a['role'],variants=variants))
        record=dict(schema='nca.engram.finding/v1',id=row['id'],scan_id=scan,title=row['title'],category=row['category'],classification=classification[row['confidence']],community_status='documented' if row['community']=='社群已記錄' else 'unmatched_in_searched_sources',game={k:config[k] for k in ('game_product_version','game_file_version','gog_version','gog_build')},source_manifest_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),assets=assets,interpretation=row['summary'],support=detail['support'],counterevidence=detail['counter'],structural_evidence=detail['structural_evidence'],sources=detail['sources'],reproduce={'command':detail['command'],'sql':detail['sql']},reconstruction_status='NOT_RECONSTRUCTED',canonical_status='RESEARCH_NOT_CANON',local_only=True)
        records.append(record);table.append(f"| `{row['id']}` | {row['title']} | {row['confidence']} | {detail['asset_count']} | {row['community']} |")
    (out/'engram-findings.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in records),encoding='utf-8')
    table+=['','## 查證一組候選','','```powershell','python -X utf8 scripts/query.py --finding NCA-59EB3E275366','```','','完整觀察、反證及機器可讀資料見 `data/findings.json` 與 `exports/engram-findings.jsonl`。']
    (ROOT/'FINDINGS.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    files=list((ROOT/'tools').glob('*.zip'))+[ROOT/'tools/NCA.Bridge.dll',ROOT/'tools/wolvenkit-9.1.0/appsettings.json',ROOT/'scripts/ink_paths.py']+list((ROOT/'web/vendor').glob('*'))
    tool_rows=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files if p.is_file()]
    (ROOT/'research/tool-files.json').write_text(json.dumps(tool_rows,indent=2),encoding='utf-8')
    report=dict(completed_at_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scan_id=scan,url=f'http://127.0.0.1:{config["port"]}',project=str(ROOT),storage_bytes=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file()),limit_bytes=config['storage_limit_bytes'],findings=len(rows),classification_counts=dict(db.execute('SELECT confidence,count(*) FROM findings GROUP BY confidence')),engram_export_records=len(records),game_version=config['game_product_version'],gog_build=config['gog_build'])
    (ROOT/'reports/delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
