# 獨立驗收資料的來源

`user-fixtures.json` 來自使用者於 2026-10-26 提供的清單，不是已驗證的遊戲事實。

`archived-conversation-titles.txt` 是 Cyberpunk Wiki contributors 所編輯的 [Cut Content 分類](https://cyberpunk.fandom.com/wiki/Category:Cyberpunk_2077_Cut_Content) 搜尋工具快照中的 57 個對話紀錄標題。整理變動：移除重複的 Archived Conversation 前綴，每行一個名稱；沒有複製完整對白。分類頁標示 CC-BY-SA，版本未核定；本衍生清單沿用該來源的 CC-BY-SA 條件，不把遊戲原文重新授權為專案程式碼。

搜尋快照顯示 130 頁，使用者提供的觀察為 128 頁，兩者不是同一時點。直接 HTTP 存取分類遭到 403，沒有以其他通道繞過。個別頁面的 baseid 未從不可讀頁面猜造，僅以本機標題、LocKey、journal 路徑及 TweakDB 記錄進行有標記的對應。

發現與信心規則不讀取這些檔案。驗收器在規則輸出落盤並記錄 SHA-256 後才讀取清單。是否找到殘留、是否找到線索、是否證明玩家不可取得，是三個不同欄位。
