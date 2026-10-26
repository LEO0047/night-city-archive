"""Add interpretation and citations AFTER generic discovery; keep evidence separate."""
import json,re,zlib
from catalog import ROOT,connect

def main():
    db=connect();report=json.loads((ROOT/'data/discovery.json').read_text(encoding='utf-8'))
    db.execute('DELETE FROM finding_assets');db.execute('DELETE FROM findings')
    source_ink=dict(title='spuddeh / cp2077-ink-archive',url='https://github.com/spuddeh/cp2077-ink-archive',note='來源記錄 2.31 的兩個無名 UI 資源；此處證據重新取自本機 2.5。')
    source_mq=dict(title='libSpace / Untranslated quests (2021)',url='https://www.reddit.com/r/LowSodiumCyberpunk/comments/lsc5p1/',note='歷史敘述含未翻譯與角色推論；本機英文翻譯狀態已有變化。')
    titles={'q000':'人生起點與教學','q001':'救援、住處與導覽','q005':'紺碧大廈與演出效能','q110':'太平洲與賽博空間','q115':'中庭與場景錄製','q101':'演唱會效能','q112':'遊行與 Oda','q108':'Johnny 演出效能','q113':'戰鬥與 Takemura','q004':'超夢與俱樂部','q116':'神輿戰鬥','q304':'Phantom Liberty Q304','q306':'Phantom Liberty Q306','q302':'Phantom Liberty Q302','q305':'Phantom Liberty Q305'}
    for g in report['candidates']:
        title=g['title'];sources=[];community='可能的新研究線索';confidence=g['confidence']
        code=re.search(r'\\(q\d+)\\',g['prefix'])
        if code and g['category']=='開發場景':title=code[1].upper()+'／'+titles.get(code[1],code[1])+'測試入口群'
        if g['slug']=='quest-base-quest-minor_quests-mq009':title='Ken Lee／MQ009 的三次會面';community='社群已記錄';sources=[source_mq];confidence='疑似刪除內容';g['score']=110
        if g['slug']=='unresolved-unreferenced-ink':community='社群已記錄';sources=[source_ink]
        if g['prefix'].rstrip('\\')==r'base\mechanical\prototypes':title='機械原型／可組裝的實體與模型'
        support=[g['reason'],f"這組包含 {g['asset_count']} 個資產，類型："+'、'.join(f'{k} × {v}' for k,v in sorted(g['extensions'].items())),
            f"群內已索引引用 {g['internal_edges']} 條；群外對核心資源的引用 {g['external_incoming']} 條；指定流程入口可達的核心資源 {g['flow_reachable_count']} 個。"]
        for edge in g['edge_examples'][:2]:support.append('可重查引用：'+edge['source']+' → '+edge['target'])
        counter=['靜態引用圖不是遊戲執行時追蹤。腳本、TweakDB、原生程式及動態載入未完整納入；沒有引用不能證明未使用。','保留內容可能是測試、備份、替代版本或仍被條件分支使用；名稱不作定案依據。']
        if g['flow_reachable_count']:counter.insert(0,f"已有 {g['flow_reachable_count']} 個核心資源可由指定正式／EP1 入口靜態到達，不能把整組判為刪除內容。")
        if g['incoming_examples']:
            e=g['incoming_examples'][0];counter.append('存在群外引用：'+e['source']+' → '+e['target'])
        if not sources:counter.append('尚未在此次檢索的社群來源中匹配；「可能的新研究線索」不表示已證明新穎性。')
        if g['slug']=='quest-base-quest-minor_quests-mq009':
            support.append('本機有 hook、second_meeting、execution 三個場景、任務階段、Ken Lee 代理模型與多語字幕。')
            counter.insert(0,'2021 社群稱未翻譯，但本機 2.5 的 en-us 字幕已是英文；歷史敘述不能視為當前版本事實。')
            counter.append('以 mq009 名稱搜尋的語音為零，只代表這種命名查詢未命中，不能排除改名或其他語音映射。')
        structural=[]
        for h in g['core']:
            row=db.execute("SELECT a.path,r.json_zlib FROM assets a JOIN resources r ON r.hash=a.hash WHERE a.hash=? AND a.extension='.gamedef' ORDER BY r.archive_id LIMIT 1",(h,)).fetchone()
            if row:
                root=json.loads(zlib.decompress(row['json_zlib']))['Data']['RootChunk']
                tags=[x.get('$value',x.get('$v','')) for x in root.get('spawnPointTags',{}).get('tags',[])]
                structural.append(dict(hash=h,path=row['path'],root_class=root.get('$type'),json_pointer='/Data/RootChunk/spawnPointTags/tags',observed=tags,resource_endpoint='/api/resource/'+h))
        for fact in structural[:2]:support.append('結構欄位：'+fact['path']+' → '+fact['json_pointer']+' = '+json.dumps(fact['observed'],ensure_ascii=False))
        if g['slug']=='unresolved-unreferenced-ink':
            support.append('無名 Widget 10823073814826382310 的外部依賴指向 Chevillon 的 centurion_ui.inkatlas 與車內螢幕動畫庫，可循引用檢查圖集和介面結構。')
            counter.append('同一圖集也被多個具名 Chevillon 車內／方向盤 Widget 引用；共享資源仍被使用，不能把整組相依內容都判成廢案。')
        fid=g['id'];sql=f"SELECT a.hash,a.path,ar.path AS archive,e.sha1,ar.sha256 AS archive_sha256\nFROM finding_assets f JOIN assets a ON a.hash=f.hash\nJOIN entries e ON e.hash=a.hash JOIN archives ar ON ar.id=e.archive_id\nWHERE f.finding_id='{fid}' ORDER BY a.path;\n\nSELECT source_hash,target_hash,field FROM semantic_refs\nWHERE source_hash IN (SELECT hash FROM finding_assets WHERE finding_id='{fid}');"
        detail=dict(asset_count=g['asset_count'],support=support,counter=counter,sources=sources,command=f'python scripts/query.py --finding {fid}\npython scripts/discover.py',sql=sql,
            next_step='逐一核對欄位、場景入口及語音對照，再與社群當前版本研究交叉比對。若要確認遊戲內未使用，另行設計不改動原始安裝的執行時驗證。',
            prefix=g['prefix'],core_hashes=g['core'],structural_evidence=structural,internal_edges=g['internal_edges'],external_incoming=g['external_incoming'],flow_reachable_count=g['flow_reachable_count'],discovery_rule=g['slug'].split('-')[0])
        summary={'開發場景':'獨立遊戲入口與任務／場景彼此連結，保留可檢驗的開發流程。','模型與原型':'從實體定義追到幾何與附屬資源，研究原型如何被組裝。','任務與對白':'任務、場景與字幕仍在封存檔中；正式入口與實際使用狀態仍待核對。','介面與圖集':'可解析的無名 UI 與相依資源，追索路徑字典以外的介面遺跡。'}[g['category']]
        db.execute('INSERT INTO findings VALUES(?,?,?,?,?,?,?,?,?)',(fid,g['slug'],title,g['category'],confidence,community,summary,json.dumps(detail,ensure_ascii=False),g['score']))
        db.executemany('INSERT INTO finding_assets VALUES(?,?,?)',[(fid,h,'core' if h in g['core'] else 'related') for h in set(g['members'])])
    db.commit()
    export=[dict(r) for r in db.execute('SELECT * FROM findings ORDER BY score DESC')]
    for row in export:row['details']=json.loads(row['details'])
    (ROOT/'data/findings.json').write_text(json.dumps(export,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'findings':len(export),'classifications':dict(db.execute('SELECT confidence,count(*) FROM findings GROUP BY confidence'))},ensure_ascii=False))

if __name__=='__main__':main()
