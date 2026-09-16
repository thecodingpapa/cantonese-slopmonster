# v0.1 驗證記錄

日期：2026-09-17。呢份記錄分清工具驗證同語言評核。

## 已實際執行

- macOS、本地 Python 3.14.6：`python3 -m unittest discover -s tests -v`，35 項通過。
- Skill Creator 嘅 `quick_validate.py`：`Skill is valid!`。只為此驗證喺忽略嘅 `work/validation-deps/` 放置 PyYAML 6.0.3；交付工具本身冇第三方依賴。
- `examples/before.md`：4 個 register 提示、0 個 writing 提示，退出碼 1。
- `examples/after.md`：coverage checked、no_findings，退出碼 0。
- 前後稿 `preserve.py`，加 `Rain is here` 同 `10 分鐘` locks：anchors_unchanged，退出碼 0。
- Markdown 本地連結逐項檢查，冇失效目標。

## 測試覆蓋

自然廣東話、普通共通詞、英文技術詞、拗口／宣傳式稿、繁體及擴展漢字、簡體提示、空白／短文／純英文／混合語言、全部內容被排除、未結束標記、巢狀引文、引文內 code、程式碼圍欄、時間碼及拍攝提示、Markdown 連結標籤、準確行欄、句子重複、長句、UTF-8 BOM、無效編碼、stdin／檔案／直接輸入一致、CLI 不修改原稿、資料標記新增刪改及手動 locks。

有一項專門示範限制：兩個產品交換數值，但數字集合不變，字面對照可以通過；`meaning_verified` 必須仍然係 false。保留意思需要另外覆核。

## 未聲稱完成嘅評核

冇獨立母語編輯審稿、真實 Rain is here 稿件測試、語料庫頻率評測、模型訓練、第二模型呼叫、實際錄音計時或 AI 偵測效能測試。原創 sample 只展示流程。

GitHub Actions 設定會喺 Python 3.10 同 3.14 跑同一套測試。各次遠端執行結果以 repository 嘅 Actions 頁面為準；本地通過唔等於遠端已執行。
