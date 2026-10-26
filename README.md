# NIGHT CITY // ARCHIVE

Cyberpunk 2077 數位考古博物館：把出貨遊戲裡保留的任務、開發入口、原型與 UI 線索整理成可以查證的內容群。

**[開啟公開研究目錄](https://leo0047.github.io/night-city-archive/)** · **[下載原始碼發行包](https://github.com/LEO0047/night-city-archive/releases)** · [34 組候選](FINDINGS.md) · [擴充計畫](ROADMAP.md)

公開目錄可直接在 Mac、Windows 或手機瀏覽。它提供研究說明、資產路徑、識別碼、封存檔校驗值、支持／反對證據和重跑查詢。遊戲模型、貼圖、語音、完整字幕、完整資產索引資料庫及個人電腦設定**不包含在公開倉庫或 ZIP**。

## 兩種使用方式

| | 公開研究目錄 | 本機完整版 |
|---|---|---|
| 瀏覽器 | Mac / Windows / 手機 | 伺服器所在電腦 |
| 內容群、證據、查詢 | 34 組參考掃描候選 | 可從自己的安裝重新產生 |
| 搜尋 | 公開說明與相關資產定位 | 全封存檔路徑、已解析任務及對白 |
| 3D、圖片、UI、語音 | 不提供遊戲媒體 | GLB 旋轉縮放、PNG、UI 草圖、WAV |
| 原始資料 | `docs/catalogue.json` 的研究子集 | 自己的遊戲安裝，唯讀 |

`127.0.0.1` 永遠表示目前開啟瀏覽器的那台電腦，不能用它從 Mac 連到另一台 Windows。公開網址不需要連線到參考掃描的電腦。

## 研究原則

- 發現以相關內容群為單位，附路徑、封存檔、引用及可重跑 SQL。
- 檔名只能用來定位線索，不能單獨證明內容未使用。
- 支持與反證並列；靜態引用缺失不等於遊戲內未使用。
- 社群已記錄與尚未匹配分開；「可能的新研究線索」不代表已證明新穎性。
- 原始遊戲目錄唯讀，工具輸出與衍生資料均留在獨立專案目錄。
- 使用 WolvenKit 的封存檔與 CR2W API，沿用成熟工具；來源及授權見 [ATTRIBUTION.md](ATTRIBUTION.md)。

## 參考掃描的結果與邊界

參考版本為 Windows Cyberpunk 2077 **2.5**，含 Phantom Liberty。57 個封存檔、592,071 筆封存項目、553,470 個唯一資產、92,327 個已解析資源變體。12,979,628 筆全文紀錄包含識別碼和欄位，**不是對白句數**。

34 組候選分成 **29 組測試／開發殘留、1 組疑似刪除、4 組證據不足**。沒有任何一組被宣稱為「確認遊戲內未使用」。原始遊戲 5,151 個檔案的前後完整 SHA-256、大小及修改時間一致；25 項本機驗收與 11 項瀏覽器觀察通過。保存的解碼 JSON 曾重建到空白資料庫，索引、全文、引用及候選穩定欄位的逐表雜湊一致；封存清單也獨立重新掃描並比對一致。

社群回歸是 **兩個內容家族、三個資源目標**：MQ009 場景群、無名 UI Widget、無名 UI 動畫庫；另有 Q000、MQ008、EP1 MQ301 的正式流程反例。這不是所有廢案的召回率。TCRF 當時回應 403，未讀到的條目未列為證據。

完整材質、UI 執行時渲染、腳本、TweakDB 和動態載入引用尚未完整實作。模型用中性材質；UI 是結構草圖。所有封存變體均保留，預覽採第一筆變體，不主張已重建實際覆寫優先序。這些結果只描述參考掃描，不保證其他版本或安裝得到相同數量。

## 本機完整版

目前完整讀取／匯出管線以 **Windows** 為目標。需要自己的合法遊戲安裝、Python 3.11+、PowerShell 7.6+、.NET 10 runtime 及 .NET SDK（建議 .NET 10 SDK）。不會安裝或修改遊戲。Mac 原生抽取管線尚未驗證。

1. 下載 ZIP 或 clone，放在遊戲目錄外。
2. 在專案目錄執行以下命令，填入自己的遊戲位置及願意使用的空間上限：

```powershell
python scripts/initialize.py --game-root "C:\Games\Cyberpunk 2077" --storage-gb 20
python scripts/bootstrap_tools.py
pwsh -NoProfile -File .\Scan.ps1
python launch.py
```

如果 `pwsh` 不在 PATH，初始化可加上 `--pwsh "C:\Program Files\PowerShell\7\pwsh.exe"`。產生的 `config.json`、`data`、`reports`、`tools`、`exports` 都被 Git 忽略。

`bootstrap_tools.py` 只從官方 GitHub release 下載 WolvenKit CLI 9.1.0 與 vgmstream r2168，先驗證固定長度與 SHA-256 再解壓。下載約 50 MB，展開後另需空間；不下載遊戲、舊版遊戲或社群遊戲資料庫。可先用 `python scripts/bootstrap_tools.py --list` 檢視來源。

第一次完整索引需要時間與磁碟空間。參考掃描約 9.83 GB；核准 20 GB 後的暫存重建仍在上限內。不同安裝可能不同，接近上限會停止。此版本有應用層空間檢查，並非作業系統磁碟配額。

### 查證與重建

```powershell
python -X utf8 scripts/query.py --finding NCA-59EB3E275366
python -X utf8 scripts/query.py --asset 3817949997515060327
python -X utf8 scripts/discover.py
python -X utf8 scripts/curate.py
pwsh -NoProfile -File .\Rebuild.ps1 -FromCache
```

`Rebuild.ps1 -FromCache` 從保存清單與 JSON 建立空白驗證資料庫，逐表比對後清理副本。工作資料庫不覆寫。省略 `-FromCache` 會先重新驗證原始安裝及重新掃描封存清單，文字仍使用保存的 JSON。新版本請使用獨立掃描目錄；原始基準不符就停止。

`scripts/acceptance.py` 是針對參考 2.5 安裝與指定媒體樣本的驗收，不是所有版本通用的安裝測試。一般原始碼測試使用：

```powershell
python -m unittest discover -s tests -v
```

## 公開網頁與建置

GitHub Pages 從 `main` 分支的 `docs/` 提供靜態網頁，不執行 Windows Python 伺服器。公開頁無 CDN、分析追蹤或模型 API。

本機預覽公開目錄：

```sh
python -m http.server 18879 --bind 127.0.0.1 --directory docs
```

接著在同一台電腦開啟 `http://127.0.0.1:18879`。`docs/catalogue.json` 只含人工解讀與定位／校驗中繼資料；發行前以 `scripts/check_public.py` 檢查 tracked files 與公開資料契約。不要直接將私人工作目錄整包上傳。

## 穩定 ID 與 ENGRAM

內容群以 `NCA-` 加上語意 slug 的 SHA-256 前 12 碼識別；資產使用 `NCA-ASSET-<uint64 hash>`。引用時同時帶掃描版本與 archive SHA-256。`scripts/deliver.py` 可在本機產生 ENGRAM JSONL，研究判斷標為 `RESEARCH_NOT_CANON`，不把推測自動當成官方設定。

## 授權

專案新增程式採 GPL-3.0；第三方 MIT 檔案保留其授權，見 [LICENSE.txt](LICENSE.txt)、[ATTRIBUTION.md](ATTRIBUTION.md)。遊戲內容及商標屬各原權利人；本專案非官方，程式授權不授予遊戲資產的重散布權。
