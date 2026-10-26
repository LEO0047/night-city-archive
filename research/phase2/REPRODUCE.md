# 第二階段：重建與判讀

本流程使用自己的 Windows 遊戲安裝。所有輸出放在專案內；原始遊戲唯讀。參考安裝為 2.5 / GOG build 60152385347545148。不要覆寫其他版本的基準；使用獨立目錄。

## 已保存輸入的完整重建

核心資料庫沿用第一階段 `scripts/rebuild.py --from-cache`。補充資料庫用：

```powershell
python -X utf8 scripts/phase2_rebuild.py
```

補充重建先計算每表內容指紋，將自己的 `data/phase2/evidence.db` 壓縮備份並解壓核對 SHA-256，才暫時移除生成的資料庫。之後從保存的 TweakDB／CR2W 解碼輸入、核心資料庫與 redscript 字面引用建立空白資料庫。每表筆數、欄位、SHA-256 列雜湊的總和與 XOR 必須一致。失敗會還原已驗證備份。只有可重建副本使用記憶體 journal，避免暫存寫入突破容量上限。

這驗證的是「保存輸入 → 資料庫」，不是每次都重新執行全部 WolvenKit 解碼。壓縮內容包含非決定性的匯出時間，不能把 gzip bytes 相同當作唯一重現標準。

## 從安裝重新取材

先完成第一階段 Scan，具備 WolvenKit 9.1.0、vgmstream r2168、PowerShell 7.6、.NET 10 SDK。新增的 redscript CLI 固定為 v0.5.32、約 1.86 MB；來源與雜湊在 `redscript-tool.json`。自動轉錄為選用：只用已存在的 faster-whisper-small 離線快取，不會下載模型。

```powershell
python -X utf8 scripts/phase2_manifest.py before
python -X utf8 scripts/phase2_prepare.py --fetch-redscript --decompile
pwsh -NoProfile -File scripts/phase2_tweaks.ps1
pwsh -NoProfile -File scripts/phase2_tweaks.ps1 -ResourceRequest data/phase2/resource-request.json
pwsh -NoProfile -File scripts/phase2_tweaks.ps1 -ResourceRequest data/phase2/resource-extra-request.json -ResourceOutput resource-scans-extra
python -X utf8 scripts/phase2_index.py
python -X utf8 scripts/phase2_context.py
python -X utf8 scripts/phase2_enrich.py
python -X utf8 scripts/phase2_operations.py
python -X utf8 scripts/phase2_rules.py
python -X utf8 scripts/phase2_audio.py --transcribe
python -X utf8 scripts/phase2_mq027.py
python -X utf8 scripts/phase2_holdout.py
python -X utf8 scripts/phase2_manifest.py after
python -X utf8 scripts/phase2_publish_local.py
```

參考掃描經過相容性修復與重試，因此其保存輸入分散於 `resource-scans`、`resource-scans-retry`、`resource-scans-extra`、`resource-scans-recovery`。新掃描直接使用目前讀取器，不必模仿舊錯誤。索引只收完成的 `.jsonl.gz`；失敗項目保留在 `errors.jsonl`。重建前不能把同一 archive/hash 的成功列重複放入不同資料夾。

剩下 3 個不同資產、共 6 個 archive 變體仍有 WolvenKit 型別不匹配；未強制轉型、未補造欄位。NaN/Infinity 保存成明示字串；未知 worldNode 使用上游 DynamicChunk 機制。來源、相容性修補與限制列在 `sources.json` 及 `resource-coverage.json` 報告。

## 判讀順序與獨立驗收

先產生 `rules.json`，再由 `phase2_holdout.py` 讀使用者清單及 57 個社群標題。它記錄規則輸出 SHA-256，不能回寫規則。一般節點操作分析在清單提供後開發，但不讀取任何清單、名稱例外或預期答案；因此這是獨立資料流驗收，並非事先盲測的召回率研究。

`phase2_query.py --record` 顯示定義、來源 SHA-256 與所有已見使用鏈；`--operations` 顯示 Item 指令類型、玩家目標及逐層圖入口；`--route` 顯示正式資源入口鏈。這些是可能使用的靜態路徑，不是遊戲實際執行追蹤。

沒有憑空的信心分數。缺正式流程入口且缺場景內容，才為「疑似刪除」；其他孤立記錄維持「證據不足」。開發後台為明示人工整理。最高級「確認遊戲內未使用」尚無案例。

## 公開與私人

`web/`、`data/`、`exports/` 是私人站點與原始研究輸入。`docs/` 是公開研究文字的產物。完整對白、語音、圖片、模型、資料庫和個人連線設定不得加入 Git。公開檢查會同時檢查已追蹤與尚未追蹤但可加入 Git 的檔案。

`phase2_publish_local.py` 只產生本機檔案，不提交或推送。公開更新前必須先審閱差異並取得使用者批准。

## 相容性

ENGRAM 仍輸出 `nca.engram.finding/v1`，原有欄位保留；分類來源為新增欄位。29 個舊後台 ID 不重用，新增 `superseded_by` 指向 `NCA-8AEC330AA900`。原始第一階段匯出保存為 `engram-findings-phase1.jsonl`；既有 `engram-findings.jsonl` 路徑更新為第二階段內容，另存相同的 `engram-findings-phase2.jsonl`。
