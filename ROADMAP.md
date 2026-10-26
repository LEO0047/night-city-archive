# 後續擴充計畫

## 1. 先提高「未使用」判斷的證據品質

加入 TweakDB、redscript／原生動態載入可辨認的引用，以及世界 streaming sector → entity → appearance → mesh 的完整鏈。圖上的每條邊應保留來源變體、欄位位置與解析器版本。先處理 MQ009、MQ027 與無名 Chevillon UI，維持支持／反對證據並列。

驗收：現有 Q000、MQ008、EP1 MQ301 反例不得被誤判成刪除；動態引用尚未覆蓋時，分類不能自動提升到「確認遊戲內未使用」。目前 29 組開發入口可再分成演出、效能、玩法及工具流程，不以 `test` 名稱代替結構證據。

## 2. 擴大獨立社群回歸集

目前僅涵蓋兩個已記錄家族、三個資源目標。加入至少 10 個互相獨立、附原始路徑的歷史案例，另記「現版已移除」「改名」「現版仍使用」等結果。TCRF 可存取後逐條核對；不繞過登入或存取控制。不得把測試 fixture 的 ID 加入發現演算法。

輸出依遊戲版本分列的命中、漏失與誤判，不把測試召回率當成全遊戲廢案發現率。舊版遊戲比較需另行取得使用者同意。

## 3. 還原更完整的視覺與語音關係

沿用 WolvenKit 官方 Blender add-on，固定版本、保留授權及匯出設定，重建材質、骨架、appearance 和 animation。先做 3 個端到端樣本，再擴充批次匯出。現在的中性 GLB 繼續保留，作幾何鑑識基準。

UI 先將庫項目、handle 範圍與父子關係正規化，再結合 atlas parts、字型及本地化文字。以 authored resolution、anchors、transform 計算版面；目前簡化排列草圖不冒充像素精準的遊戲 UI。

用已解析的 voiceovermap 把字幕識別碼、男女版本與 WEM 連起來，支援在對白旁直接播放對應語音。目前可以分別搜尋文字與語音並循引用追查。對多聲道、音效 bank 與特殊 codecs 分別建立格式測試。

## 4. 版本化與研究編輯

為每次 scan 建立 immutable scan ID，將路徑 hash 與 archive variant 分離；掃描結果以來源檔案 SHA-256、工具 SHA-256、設定及解析版本辨識。保留所有版本差異，避免將新版工具輸出預設值誤當遊戲版本。

新增可匯出的人工註記層，與可再生的自動發現分開存放。候選 ID 採穩定語意 slug 的 SHA-256 前 12 碼；如果跨版本改名，新增 alias／redirect，不重新分配舊 ID。資產維持 `NCA-ASSET-<uint64 hash>`；跨版本判斷必須同時帶 scan ID 與 archive SHA-256。

## 5. ENGRAM 的唯讀介接

現有 `exports/engram-findings.jsonl` 是 v1 匯出契約，包含候選 ID、來源版本、資產定位、觀察到的事實、解讀、反證及重現指令。ENGRAM 可以引用這些 ID，但不能把推測自動升格成官方設定或遊戲內事實。

下一步建立獨立的 reconstruction workspace：原始觀察標 `OBSERVED`，社群解讀標 `COMMUNITY_REPORTED`，重建內容標 `RECONSTRUCTED`，缺失標 `MISSING`。重建出的對白、任務與模型另分配派生 ID，連回證據及所採假設。這次沒有改動 ENGRAM 的程式、服務或資料。

若需實際遊戲修改、額外大量空間、下載舊版、帳號登入或對外發布，先提出具體變更及容量估算，再請使用者決定。
