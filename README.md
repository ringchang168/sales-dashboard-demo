# 業績互動分析儀表板（公開模擬資料）

## 線上互動展示

[點此開啟業績互動分析儀表板](https://sales-dashboard-demo-occwwx2xvfz3ofm4cuinba.streamlit.app/)
 (若出現「Zzzz／休眠」畫面，請點選「Yes, get this app back up!」並稍候載入。儀表板的靜態畫面也可在 Notion 作品集預覽。)

第三階段作品 3-1。以 [2-2 業績資料報表自動化](https://github.com/ringchang168/sales-report-automation-demo) 的公開模擬銷售資料，建立獨立的 Streamlit 互動儀表板；**不修改原作品**。資料來源是該專案的 `data/sales.csv`，本專案保留一份相同的資料供本機執行。

## 可以看什麼

- 依銷售日期、業務單位、產品篩選，所有指標與圖表同步更新。
- 日期可用「日曆」選取，或切換至「手動」輸入模式；手動輸入無效日期會顯示錯誤原因。鍵入後需按 Enter 或點到欄位外。
- 銷售總額、交易筆數、銷售數量、平均每筆金額。
- 月度銷售趨勢、業務單位與產品銷售排名，以及篩選後明細下載。

計算口徑：交易筆數是 CSV 的資料列數；平均每筆金額＝銷售總額 ÷ 交易筆數。月度與分類圖表均加總 `銷售金額`。資料沒有業績目標欄位，因此不顯示達成率。所有人名與金額均屬教學用模擬資料，不是實際業績。

## 在 Windows／VS Code 執行

在 VS Code 開啟本資料夾，於終端機建立虛擬環境、安裝套件並啟動：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

如果電腦沒有 Python 3.12，可將第一行改成 `py -m venv .venv`（需 Python 3.10 以上）。執行後打開終端機顯示的本機網址，通常是 `http://127.0.0.1:8501`。按 `Ctrl+C` 停止。

測試：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

資料檔 `data/sales.csv` 共 896 筆，未篩選時銷售總額為 NT$ 81,374,300；這兩個數字可以用來核對畫面。CSV 為 UTF-8 with BOM。
