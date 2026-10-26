# 第二階段研究檔案

遊戲 2.5 · GOG 60152385347545148 · 5,151 檔案 前後校驗一致

## MQ027 / Living on the Edge

`NCA-AB6DD4DA3FB3` · 疑似刪除內容 · rule

新聞團隊、危險特技與失去工作的駕駛：192 個資產保留故事，但正式場景缺件，現行任務入口未連通。

系統：DETACHED_WITH_MISSING_SCENES：正式流程可達 0 個核心資源；7 條場景路徑沒有對應資產。

研究判讀：目前版本的 MQ027 特技任務流程殘缺且不接正式流程，支持「疑似刪除內容」。尚不足以聲稱這組所有角色、共用模型、世界標記或錄音都完全未使用。

### 一份缺了正式場景的特技任務

原始日誌標題鍵 LocKey#10390 對應 Living on the Edge。日誌、角色定義、錄音與任務節點共同描述：V 遇到 N54 新聞團隊，在原駕駛出事後接替特技工作。這是本機內容的研究重述，並非已恢復可玩的任務。

現存 6 個 questphase、1 個 quest、1 個獨立 gamedef，以及 2 個 chickentest 場景。主階段頂層有 28 個節點；其他巢狀圖、訊息與收尾階段也保留。

### 角色與關係

Character.mq027_director 的顯示名稱為 Jessy；原始文字鍵還給出 Jessica Yu。Character.mq027_driver 為 Suicide Stan／Stanley Carlson；Character.mq027_recorder 為 Kikil／Kikil Ivakin。角色名稱取自 TweakDB 與本機文字，沒有採信機器轉錄對人名的猜測。

Jessy 負責拍攝與報酬，Stan 是被 V 接替的駕駛，Kikil 是團隊成員。角色用途來自記錄名稱、文字與語音的交叉判讀；模型目前是代理外觀，不代表最終人物造型。

### 原本要玩到什麼

原始日誌與指令保留裝上錄影設備、騎機車進入 AV、沿建築／檢查點完成限時特技等步驟。可見的分支涉及報酬與名氣，以及是否替 Stan 支付醫療費。

後續訊息分支包括 Jessy 告知影片成果、機車禮物，以及 Stan 對工作被搶走的不滿或對醫療協助的感謝。這證明作者寫過這些後續，不證明目前能觸發獎勵。逐段原始日誌只在私人聽讀室顯示。

### 原本可能接在哪裡

獨立 gamedef 使用夜城的 streamingworld，出生標記為 mq027_spwn_kiroshi；社群與節點參照另有 Arroyo、downhill 等線索。因此可提出與 Kiroshi／Arroyo 周邊特技路線相關的假說。

本次沒有把這些標籤解算成經遊戲驗證的座標，也沒有證明上市版曾在該處出現任務入口。確切街口與觸發時機仍待世界節點定位。

### 現在為什麼走不到

從本體與 EP1 兩個正式 gamedef 出發，沿 gamedef／quest／questphase／scene 引用，沒有到達 MQ027 的正式流程。主階段仍指向 mq027_01_stunt_00、03_stunt_02、04_stunt_03、05_stunt_04、06_owstunt01、07_owstunt02 六個 scene；目前全資產索引均找不到這些精確路徑。

第七條缺失引用指向 scenes\mq025_00_chickentest.scene。同名檔只存在 test 與 test\versions\gold，這是路徑不符；不能用兩份測試場景宣稱已找回六個正式場景。

以上是結構性的中斷證據。它不等同於執行所有存檔狀態後證明整組資產永遠不會載入。

### 能聽到多少，不能聽出什麼

保留 145 個英文語音檔，合計約 10.81 分鐘，映射到 117 個 voice string ID。每段附 WEM 路徑、封存檔、voiceovermap 的 JSON 指標與轉換後 WAV 校驗值。

搜尋 en-us 與 zh-tw 字幕索引沒有找到這 117 個 ID 的字幕。私人版提供原音與離線機器轉錄；轉錄標記為未校對，不能冒充遊戲原始字幕。

### 反證

- Johnny 的 mq027_ws_johnny_final／stunt 標記仍出現在 always_loaded 世界資料；某些共用部分可能仍被載入。
- Vehicle.mq027_news_av 指向共用 av_zetatech_atlus_basic_01.ent；不能把整台 AV 模型說成廢棄載具。
- test 與 gold 資料夾有兩份 chickentest；測試場景的存在削弱「整組完全被刪除」說法，但沒有補上正式場景。
- 沒有舊版本比對，無法確認何時移除，也不能把歷史 prophet 的稱呼直接當作本次 stunts 流程。

### 證據與重跑

**MQ-01 原始日誌** — 任務標題、目標與分支訊息的原始定位。

```text
quests/minor_quest/mq027_stunts; contacts/jessy; LocKey#10390
python -X utf8 scripts/phase2_query.py --sql "SELECT hash,archive_id,pointer,path,type FROM journal_nodes WHERE path LIKE '%mq027%'"
```

**MQ-02 任務與獨立入口** — gamedef、主階段與獨立測試入口。

```text
base\quest\minor_quests\mq027\mq027.gamedef; mq027.questphase
python -X utf8 scripts/phase2_query.py --quest mq027
```

**MQ-03 角色與新聞 AV** — 5 個相關記錄；名稱與實體資源可重查。

```text
Character.mq027_director / driver / recorder; Vehicle.mq027_news_av
python -X utf8 scripts/phase2_query.py --record Character.mq027_director
python -X utf8 scripts/phase2_query.py --record Vehicle.mq027_news_av
```

**MQ-04 原音及映射** — 145 段 WAV 的來源與轉錄 provenance；完整內容只在私人版。

```text
data/phase2/audio/inventory.json; *.asr.json; base\localization\en-us\voiceovermap.json
python -X utf8 scripts/phase2_audio.py
python -X utf8 scripts/phase2_mq027.py
```

**MQ-05 收尾分支** —  finished 與 msg_return 圖保留後續訊息節點。

```text
base\quest\minor_quests\mq027\phases\mq027_finished.questphase; mq027_msg_return.questphase
python -X utf8 scripts/phase2_mq027.py
```

**MQ-06 世界殘留與具體反證** — 世界／實體索引中有 71 個相關欄位見證；完整集合留在私人證據庫。

```text
base\worlds\03_night_city\_compiled\default\always_loaded_1.streamingsector
python -X utf8 scripts/phase2_query.py --sql "SELECT hash,archive,pointer,value FROM resource_fields WHERE lower(value) LIKE '%mq027%'"
```

**MQ-07 精確缺件表** — 每條缺失引用都列出來源階段與欄位，無同名替代推論。

```text
base\quest\minor_quests\mq027\scenes\mq027_01_stunt_00.scene
base\quest\minor_quests\mq027\scenes\mq027_03_stunt_02.scene
base\quest\minor_quests\mq027\scenes\mq027_04_stunt_03.scene
base\quest\minor_quests\mq027\scenes\mq027_05_stunt_04.scene
base\quest\minor_quests\mq027\scenes\mq027_07_owstunt02.scene
base\quest\minor_quests\mq027\scenes\mq027_06_owstunt01.scene
base\quest\minor_quests\mq027\scenes\mq025_00_chickentest.scene
python -X utf8 scripts/phase2_query.py --quest mq027
```

規則採可重算條件：沒有正式流程入口 AND 有缺失場景 payload => 疑似刪除內容。這兩條均來自索引；沒有手寫分數。確認未使用還需要排除動態／原生／存檔入口，因此不升到最高級。

## 開發者後台總覽 / 29 個歷史入口

`NCA-8AEC330AA900` · 測試或開發殘留 · analyst

把分散的測試入口收成一張開發工作台地圖；舊連結仍可定位原來的內容群。

系統：沿用第一階段結構候選，沒有把 29 組各自計作新發現。

研究判讀：獨立啟動入口、測試流程與場景搭配支持開發用途；沒有推論所有相依模型未使用。

### 如何閱讀後台

每個舊 ID 轉到此總覽。原始候選成員仍保留在第一階段索引，ENGRAM 匯出保留同一 ID 並新增 superseded_by。名稱中的 test 只幫助定位，實際判讀還要求可解析的獨立入口與其任務／場景關係。

### 反證

- 後台入口引用的共用動畫、角色或材質可能同時服務正式任務；合併不改變其個別使用狀態。
- 部分測試流程未完整解析所有外部觸發，不能由後台位置推出玩家絕不會碰到相依資產。

### 證據與重跑

**DEV-01 原始群組與轉址** — 29 個舊 ID 對一個穩定總覽 ID。

```text
exports/phase2-aliases.json
python -X utf8 scripts/phase2_query.py --dossier NCA-8AEC330AA900
```

人工整理，依獨立啟動／測試流程結構判為開發用途；不是自動廢案分數。

## Ken Lee / MQ009：保留三次會面的孤立流程

`NCA-59EB3E275366` · 證據不足 · analyst

hook、second_meeting、execution 場景仍在；目前只能確認入口未連通，不能沿用舊版的高信心判定。

系統：DETACHED_FLOW；新規則分類 證據不足

研究判讀：證據不足；保留為有具體反證的研究檔案。

### 目前可下的結論

hook、second_meeting、execution 場景仍在；目前只能確認入口未連通，不能沿用舊版的高信心判定。

現存英文字幕已翻譯，與 2021 年「未翻譯」敘述不一致；場景 payload 本身仍完整，沒有 MQ027 那種正式場景缺件證據。

### 反證

- 現存英文字幕已翻譯，與 2021 年「未翻譯」敘述不一致；場景 payload 本身仍完整，沒有 MQ027 那種正式場景缺件證據。
- 按 mq009 檔名搜尋不到語音不代表語音不存在，下一步應追 voiceovermap ID。

### 證據與重跑

**LEGACY-01 原始成員與引用** — 保留原 ID，重新區分歷史分類與目前判讀。

```text
NCA-59EB3E275366
python -X utf8 scripts/query.py --finding NCA-59EB3E275366
```

人工重新評估：存在上述具體使用／完整性反證，沒有足以確認未使用的排除證據；不採用第一階段手寫 score。

## 無名 UI / Chevillon 介面依賴

`NCA-8616011BE6ED` · 證據不足 · analyst

未解析名稱的 widget 與 Chevillon 圖集形成一組可查的介面殘留；共享圖集本身仍有具名使用者。

系統：歷史候選保留；本階段沒有規則將它升為未使用。

研究判讀：證據不足；保留為有具體反證的研究檔案。

### 目前可下的結論

未解析名稱的 widget 與 Chevillon 圖集形成一組可查的介面殘留；共享圖集本身仍有具名使用者。

10823073814826382310 的依賴通往 Chevillon centurion_ui 圖集與車內動畫；具名方向盤／車內 widget 同時引用相同圖集。

### 反證

- 10823073814826382310 的依賴通往 Chevillon centurion_ui 圖集與車內動畫；具名方向盤／車內 widget 同時引用相同圖集。
- 補齊 hash 字典及原生介面載入入口後，才能區分替代面板與孤立 widget。

### 證據與重跑

**LEGACY-01 原始成員與引用** — 保留原 ID，重新區分歷史分類與目前判讀。

```text
NCA-8616011BE6ED
python -X utf8 scripts/query.py --finding NCA-8616011BE6ED
```

人工重新評估：存在上述具體使用／完整性反證，沒有足以確認未使用的排除證據；不採用第一階段手寫 score。

## Spiderbot / 原型名稱下的共用骨架

`NCA-E36DF3323A07` · 證據不足 · analyst

原型資料夾裡的機械零件與骨架仍被 Q005 動畫引用；資料夾名稱不足以定案。

系統：歷史候選保留；本階段沒有規則將它升為未使用。

研究判讀：證據不足；保留為有具體反證的研究檔案。

### 目前可下的結論

原型資料夾裡的機械零件與骨架仍被 Q005 動畫引用；資料夾名稱不足以定案。

Q005 的 sync_q005_06_spiderbot_room_01.anims 明確引用 prototype skeleton.rig；因此不能把這組 40 個相依資產整批當作廢案。

### 反證

- Q005 的 sync_q005_06_spiderbot_room_01.anims 明確引用 prototype skeleton.rig；因此不能把這組 40 個相依資產整批當作廢案。
- 需要區分未使用外殼與仍被動畫使用的骨架，並追正式實體的 appearance 選擇。

### 證據與重跑

**LEGACY-01 原始成員與引用** — 保留原 ID，重新區分歷史分類與目前判讀。

```text
NCA-E36DF3323A07
python -X utf8 scripts/query.py --finding NCA-E36DF3323A07
```

人工重新評估：存在上述具體使用／完整性反證，沒有足以確認未使用的排除證據；不採用第一階段手寫 score。

## SQ017 / Chickentest 與主 quest 的關係

`NCA-AF6CA4611B50` · 證據不足 · analyst

測試場景不是完全沒有來源：SQ017 的 quest 仍引用 chickentest 階段，是否能啟動要往上追入口。

系統：歷史候選保留；本階段沒有規則將它升為未使用。

研究判讀：證據不足；保留為有具體反證的研究檔案。

### 目前可下的結論

測試場景不是完全沒有來源：SQ017 的 quest 仍引用 chickentest 階段，是否能啟動要往上追入口。

base\quest\side_quests\sq017\sq017.quest 引用 test\sq017_chicken_test.questphase；只看 test 名稱會漏掉這條反證。

### 反證

- base\quest\side_quests\sq017\sq017.quest 引用 test\sq017_chicken_test.questphase；只看 test 名稱會漏掉這條反證。
- 必須區分整個 SQ017 流程的正式入口與它內部測試分支，不從路徑推測實際執行。

### 證據與重跑

**LEGACY-01 原始成員與引用** — 保留原 ID，重新區分歷史分類與目前判讀。

```text
NCA-AF6CA4611B50
python -X utf8 scripts/query.py --finding NCA-AF6CA4611B50
```

人工重新評估：存在上述具體使用／完整性反證，沒有足以確認未使用的排除證據；不採用第一階段手寫 score。

## Peralez 競選上衣 / 發放指令不等於取得途徑

`NCA-710358FF9EDE` · 證據不足 · analyst

mws_jim 裡的上衣發放節點與圖入口斷開，但 SQ006 的同一件上衣實體仍被世界區塊引用。一條死路，並不能代表整個道具不可取得。

系統：HAS_USE_LINK；規則分類 證據不足

研究判讀：證據不足；下面明確區分本機觀察與取得狀態。

### 一條斷開的發放路線

本機 Items.SQ012_Shirt_VoteForPeralez 共擷取 1 條任務操作見證。mws_jim 圖的節點 ID 151（handle 691）是 AddItem，數量 1，目標 refLocalPlayer=1。從該圖 input handle 1 沿所有輸出遍歷，沒有到達此節點。

這是局部圖的結構斷開，不是條件機率，也沒有用 wiki 的分類替它加分。外部事件或原生派送尚未完全解析，因此仍保留靜態分析的界線。

### 另一條不能忽略的世界引用

正式 EP1 gamedef 連到夜城 streamingworld，再到 blocks\all.streamingblock、exterior_-2_-2_1_0.streamingsector，最後引用 base\quest\side_quests\sq006\entities\sq006_peralez_shirt.ent。該實體的 itemTDBID 正是同一個上衣記錄。

因此可下的結論是：mws_jim 的那條發放路線斷開，但同一道具仍有世界實體引用。尚未驗證區塊啟動、可互動／可拾取狀態與存檔條件，不能裁定 wiki 必然錯誤，也不能確認玩家拿不到。

### 反證

- SQ006 上衣實體的 itemTDBID 引用相同記錄，且可沿正式世界資源鏈到達。
- 世界實體是否啟動及允許拾取仍未實測；斷開的單一發放節點不足以排除世界取得途徑。

### 證據與重跑

**REC-01 定義與所有已見途徑** — HAS_USE_LINK

```text
Items.SQ012_Shirt_VoteForPeralez
python -X utf8 scripts/phase2_query.py --record 141338021047
```

**REC-02 任務操作與逐層圖** — 1 條操作見證；無資料也照實顯示。

```text
data/phase2/quest-operations.json
python -X utf8 scripts/phase2_query.py --operations Items.SQ012_Shirt_VoteForPeralez
```

**REC-03 另一條世界使用鏈** — SQ006 實體指向相同上衣，不能因斷開發放節點而忽略。

```text
3285049569572177738 /Data/RootChunk/compiledData/Data/Chunks/0/itemTDBID/$value
python -X utf8 scripts/phase2_query.py --route 3285049569572177738
```

人工案例選擇、規則輸出未修改。只有定義缺入口／可能使用鏈，缺執行與動態證據，因此維持證據不足。

## Jackie 的砍刀 / 任務物品與武器的界線

`NCA-9D353621F5B8` · 證據不足 · analyst

本機把 sq018_jackie_machete 定義成 Gen_Misc 任務物品，並非可裝備武器。不能把「不是武器」擴張成「整個物品未使用」。

系統：DEFINITION_ONLY；規則分類 證據不足

研究判讀：證據不足；下面明確區分本機觀察與取得狀態。

### 同一個名稱，兩種不同命題

Items.sq018_jackie_machete 的記錄型別是 gamedataItem_Record，itemType 為 Gen_Misc。這與一般 WeaponItem 記錄不同，支持「它不是一把可當普通武器使用的砍刀」這個較窄結論。

自動規則在所掃途徑中未觀察到取得鏈，將它列為定義線索。但它是否充當任務展示、檢查條件或動態生成物，仍未被排除；社群的不可取得說法不能因此自動成立。

### 反證

- Gen_Misc 仍可能是有效任務物品；缺少武器型別不是未使用證明。
- 沒有觀察到 shop／loot／reward 鏈，只界定本次靜態掃描結果，不能排除原生或動態記錄建立。

### 證據與重跑

**REC-01 定義與所有已見途徑** — DEFINITION_ONLY

```text
Items.sq018_jackie_machete
python -X utf8 scripts/phase2_query.py --record 112581855609
```

**REC-02 任務操作與逐層圖** — 0 條操作見證；無資料也照實顯示。

```text
data/phase2/quest-operations.json
python -X utf8 scripts/phase2_query.py --operations Items.sq018_jackie_machete
```

人工案例選擇、規則輸出未修改。只有定義缺入口／可能使用鏈，缺執行與動態證據，因此維持證據不足。
