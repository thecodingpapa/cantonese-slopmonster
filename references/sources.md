# 來源與製作記錄

核對日期：2026-09-17。呢份係來源記錄，唔代表外部作者審核或認可本工具。

## SlopMonster

- 項目：[ItsssssJack/SlopMonster](https://github.com/ItsssssJack/SlopMonster)
- 檢視版本：[`f261dbf11c2a206ecd8780c070a46dae64edd8be`](https://github.com/ItsssssJack/SlopMonster/tree/f261dbf11c2a206ecd8780c070a46dae64edd8be)
- 已檢視 README、SKILL.md、tools/deslop.py、tools/cleanse.sh、[LICENSE](https://github.com/ItsssssJack/SlopMonster/blob/f261dbf11c2a206ecd8780c070a46dae64edd8be/LICENSE)。授權 MIT，Copyright (c) 2026 Jack Roberts。
- 採用嘅設計概念：將 agent 編輯指引同可執行檢查分開，修改前後都覆核。
- 本項目程式、廣東話規則同例子另外編寫，未搬用原版英文詞庫或案例；保留原版 MIT 告示作清楚歸屬。
- 原版 README 表明規則只針對英文。呢個版本移除品質分數，改為提示同檢查範圍；冇自動第二模型呼叫。

## HKCanCor：未捆綁，只作語言資源指引

[Hong Kong Cantonese Corpus](https://github.com/fcbond/hkcancor) 記錄 1997–1998 年談話及廣播語料，有切詞、粵拼同詞性資料。倉庫列 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。

參考書目：K. K. Luke and May L. Y. Wong (2015), *The Hong Kong Cantonese Corpus: Design and Uses*, Journal of Chinese Linguistics Monograph Series 25, 312–333。

v1 只核對資源說明同授權，**未下載、抽樣分析、訓練或複製語料**；唔聲稱規則有語料頻率驗證。將來可以研究語法同節奏，唔應該當成當代 YouTube 頻道聲線。日後如果加入摘錄，要另外標來源、授權、改動及適用範圍。

## 粵典：未捆綁，只提供查閱線索

[粵典 words.hk](https://words.hk/) 可作詞語查閱線索。其[開放資料條款](https://words.hk/base/hoifong/) 指部分標示條目使用 Non-Commercial Open Data License，含商業限制及例外；唔可一概當作無限制商用資料。本項目冇複製條目、例句或釋義，亦冇依賴任何豁免。

## 本項目原創內容

所有廣東話範例、規則說明、提示同 sample script 都係呢次製作由 AI 原創，未經獨立母語編輯評核。啟發式規則屬人工設計而非從 corpus 訓練。Python 測試驗證工具行為，唔證明語言品質或內容真實。

「Rain is here」係用戶提供嘅唯一頻道品牌資料。冇收集真實稿、channel URL、觀眾資訊或主持背景；未做頻道聲線校準。示例數字、情境、畫面同 example.com 網址純屬示範。

Codex 載入方法核對 [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills)。本項目只使用普通 skill 檔案；冇更改全域 agent 設定。
