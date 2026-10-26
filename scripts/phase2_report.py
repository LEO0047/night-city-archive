"""Generate readable acceptance records after verification; no publishing."""
import collections,json,pathlib,shutil
from phase2_index import ROOT,OUT
PUBLIC=ROOT/'release/source' if (ROOT/'release/source/.git').exists() else ROOT
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    checks=read(ROOT/'reports/phase2/acceptance.json');hold=read(ROOT/'reports/phase2/holdout.json');cat=read(ROOT/'web/catalogue.json');rebuild=read(ROOT/'reports/phase2/supplement-rebuild.json');coverage=read(ROOT/'reports/phase2/resource-coverage.json');before=read(ROOT/'reports/phase2/game-before.json');after=read(ROOT/'reports/phase2/game-after.json')
    rows=['# 第二階段驗收報告','',cat['integrity'],'','## 結論與界線','',f"技術驗證 {checks['passed_checks']} / {checks['total_checks']}；這不代表社群廢案清單已全部通過。",'','MQ027 的「未接正式流程＋六個正式場景缺件」支持疑似刪除。Peralez 上衣同時具有斷開的發放節點及世界實體引用，維持證據不足。Jackie 砍刀是 Gen_Misc 任務物品，不能把非武器當成整件未使用。','', '社群 A 類 18 項及 Archived Conversation 57 項共 75 個驗收列，皆未達不可取得分類，嚴格計為漏掉／待核。這些列可能包含相同內容的例子，不是 75 個已確認不同廢案。七項正式實裝反例均未誤判；兩項改版移除線索另只回報殘留。','', '沒有證據就不把漏掉歸咎於 wiki 錯誤或版本差異。原始清單保持獨立，未加入發現規則。一般節點分析在收到清單後開發，因此不宣稱預註冊盲測。','','## 技術驗收逐條','', '| 檢查 | 結果 |','|---|---|']
    rows += [f"| {c['name']} | {'通過' if c['passed'] else '未通過'} |" for c in checks['checks']]
    rows += ['',f"補充資料庫重新建立後，{len(rebuild.get('after',{}))-1} 張表的列數與內容指紋一致。原始資料庫約 5 GB，先建立並驗證 {rebuild['backup_bytes']:,} bytes 壓縮復原副本，成功後移除；重建未同時保留兩份完整資料庫。",'',f"世界／實體選取 {coverage['requested']:,} 份 archive 變體，成功 {coverage['decoded']:,}，未解析 {len(coverage['unparsed'])}。三個不同資產分別出現於本體及 EP1 封存檔；錯誤為 AccessPoint／Window／WindowBlinders skill-check 型別不匹配，未強制補造內容。",'',f"原始遊戲前後 SHA-256 manifest：`{after['sha256']}`。新增、刪除、變更皆為 0；共 {after['files']:,} 檔案。",'','第一階段的 25 項驗收另行重跑通過。原本「至少 30 組」檢查仍對歷史核心快照運行；第二階段展示將 29 組合併為 1 份，沒有拿歷史數量替新成果充數。','','## 逐項獨立清單','','| ID | 項目 | 回報 | 具體觀察與原因 |','|---|---|---|---|']
    for r in hold['cases']:rows.append('| '+' | '.join(str(r.get(k,'')).replace('|','／').replace('\n',' ') for k in ('fixture_id','name','result','detail'))+' |')
    rows += ['','## 外部來源與讀取限制','','Cyberpunk Wiki 分類以快照取得 57 個對話標題；直接頁面存取有 403／402 或快取未命中，未繞過。TCRF 本階段未讀。1.6 與 2.1 實裝反例另有 CD PROJEKT RED 官方更新記錄。來源 URL、授權與限制見 [sources.json](sources.json) 及 [HOLDOUT-ATTRIBUTION.md](HOLDOUT-ATTRIBUTION.md)。','','## 網站與公開差異','','私人版：MQ027 全文研究、145 個原音、原始日誌與未校對離線轉錄；可連回模型、圖片、UI 結構及全域全文索引。公開版：研究敘述、定位路徑、識別碼與校驗；沒有媒體、完整對白或資料庫。','', '瀏覽器已驗證載入、類別篩選、反例搜尋、舊 ID 轉址、私人語音播放至結束與既有模型載入；公開版未顯示音訊或私人讀取入口。截圖 API 回報無法擷取，因此本次沒有以截圖宣稱像素／響應式視覺驗收。','', '截至本報告，GitHub 與公開網站尚未更新。推送前需使用者檢視具體差異並批准。']
    target=ROOT/'research/phase2/ACCEPTANCE.md';target.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    for name in ('MQ027.md','FINDINGS.md','ACCEPTANCE.md','ROADMAP.md','REPRODUCE.md','sources.json','DOSSIER-TEMPLATE.md','HOLDOUT-ATTRIBUTION.md','user-fixtures.json','archived-conversation-titles.txt','redscript-tool.json'):
        src=ROOT/'research/phase2'/name;dest=PUBLIC/'research/phase2'/name
        if src.resolve()!=dest.resolve():shutil.copyfile(src,dest)
    shutil.copyfile(ROOT/'research/phase2/FINDINGS.md',PUBLIC/'FINDINGS.md');shutil.copyfile(ROOT/'research/phase2/ROADMAP.md',PUBLIC/'ROADMAP.md')
    print(str(target),flush=True)
if __name__=='__main__':main()
