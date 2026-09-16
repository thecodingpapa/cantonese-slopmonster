# Cantonese SlopMonster｜香港廣東話執稿工具

**用繁體字寫、讀出嚟自然嘅香港廣東話。** 包含可供 AI 助手使用嘅編輯 skill、離線 Python 檢查器、前後稿資料對照，同 Rain is here YouTube 寫稿指南。

👉 **先睇 [Rain is here 使用指南](RAIN-IS-HERE-GUIDE.md)**：有設定方法、brief、大綱／起稿／執稿提示、讀稿步驟同短例子。只確認頻道名；未校準頻道聲線。

## 即刻試

將整個資料夾交畀可以讀本地檔案嘅 AI 助手，講：

> 請讀 SKILL.md 同 references/editorial.md，幫我將以下稿執成自然香港廣東話，用繁體字，保留所有事實、數字、引文同拍攝提示。

有 Python 3.10+ 就可以跑，冇第三方依賴、網絡呼叫或 API key：

```sh
python3 tools/check.py examples/before.md
python3 tools/check.py examples/after.md
python3 tools/preserve.py examples/before.md examples/after.md --lock 'Rain is here' --lock '10 分鐘'
python3 -m unittest discover -s tests -v
```

第一個指令預期退出碼 **1**，因為有語體提示；修訂稿同字面對照預期 **0**。所有規則都係建議，唔應該為求零提示而犧牲意思。

## 做到乜

- **Skill**：按成句同上下文執口述稿，保留資料同作者意圖，唔機械轉換共通中文。
- **Checker**：10 類有限規則，分開語體／字形同空泛、重複、節奏；列原稿行、欄同覆核理由。
- **Preserve**：比較數字、網址、引文、code、時間碼、拍攝提示及自訂 lock 嘅字面變動。
- **可移植**：Markdown + Python 標準函式庫；無自動模型呼叫或隱藏服務。

原創例子：

> 今天我們會展示這個計時方法：先設定 10 分鐘，再按開始。
>
> → 今日我哋會示範呢個計時方法：先設定 10 分鐘，再撳開始。

例子唔係真實頻道實錄，未經獨立母語編輯評核。

## CLI

```sh
python3 tools/check.py your-script.md --json
python3 tools/check.py --text '我哋今日試下呢個方法，睇下啱唔啱用。'
python3 tools/check.py - < your-script.md
python3 tools/check.py dialogue.md --include-quotes
python3 tools/preserve.py original.md edited.md --lock '關鍵名稱' --json
```

輸入要係 UTF-8 `.md`／`.txt`；先將 DOCX／PDF／HTML 匯出口述文字。`--format plain` 關閉 Markdown 特有排除。冇輸出改稿功能；AI 助手按 skill 編輯，程式只讀取。

Check 退出碼：`0`＝可辨識旁白已套用規則而冇命中；`1`＝有提示／範圍未確定；`2`＝冇旁白／讀檔／編碼／用法錯誤。Preserve：`0`＝字面標記不變；`1`＝有變更或格式警告；`2`＝無效輸入。完整條件見 [規則及限制](references/rules.md)。

## 同原版嘅關係

受 [ItsssssJack/SlopMonster](https://github.com/ItsssssJack/SlopMonster) 啟發，保留「檢查 → 編輯 → 再檢查」概念。原版英文規則唔適用於廣東話，所以本項目另外編寫程式、規則同例子；唔沿用 5/5 分數或必須更換模型嘅要求。唔係原作者官方翻譯或認可版本。

本工具唔係 AI 作者偵測器，唔保證避過偵測；唔係繁簡轉換器、事實核查器或模型訓練。空白、短文、其他語言或者全部被排除嘅文字會顯示範圍問題，唔會因為冇命中就稱為完美。即使字面資料不變，都要覆核意思同親自讀稿。

## 檔案

| 檔案 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | AI 助手入口；整個資料夾係一個 skill |
| [RAIN-IS-HERE-GUIDE.md](RAIN-IS-HERE-GUIDE.md) | 非程式使用者寫稿指南及可複製提示 |
| [references/editorial.md](references/editorial.md) | 口語決策、保留意思、聲線校準 |
| [references/rules.md](references/rules.md) | 規則、排除範圍、退出碼 |
| [references/sources.md](references/sources.md) | 來源、授權、例子 provenance |
| [tools/check.py](tools/check.py) / [tools/preserve.py](tools/preserve.py) | 兩個離線 CLI |
| [examples/](examples/) / [tests/](tests/) | 原創前後稿、行為測試 |
| [prompts/second-review.md](prompts/second-review.md) | 可選人工轉交嘅第二輪覆核提示 |

私人稿件放 `work/`；佢同 `outputs/` 都唔會加入 Git。修改 checker 後跑 unittest。GitHub Actions 只跑程式測試，唔會要求所有文稿零提示。

## 授權

本項目新增內容採 [MIT](LICENSE)。保留 [SlopMonster 原版 MIT 告示](licenses/SlopMonster-MIT.txt) 及明確來源說明。無捆綁 HKCanCor 語料或粵典條目；外部資源維持各自條款，唔受本項目 MIT 授權涵蓋。
