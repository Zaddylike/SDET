# TestPilot 測試框架

## 1. 介紹

TestPilot 是一套由YAML 驅動的 API／WebSocket、UI Web、App自動化測試工具，支援API的同步/非同步、限流、重試，介面操作以及報表輸出。

## 2. 安裝

3. 快速開始

4. CLI 參數
--yaml: 指定 YAML 路徑或資料夾

*測試腳本路徑不用加tests

--override-type: 強制指定測試類型 (api、websocket …)

--concurrency: 最大併發數 (需搭配 Semaphore)

5. YAML 規範
type：測試類型（api、websocket、stress…）

meta.name：案例名稱

cases[].params：

url、method、headers…

cases[].expect：

field、value、comparator

6. 報表輸出
CSV / XLSX 自動生成於 reports/

檔名格式：YYYYMMDD_<case_name>_<type>.csv

7. 自訂錯誤
errors.py 定義：

TestPilotError、NetworkError、ValidationError

8. 擴充指南
整合 UI 測試：新增 ui_web_handler.py / ui_app_handler.py，並在 runner.py 加入 dispatch

壓力測試：見下方「進階章節」

9. 進階
使用 asyncio.Semaphore 控制併發

建議搭配 aiohttp.ClientSession 進行非同步 HTTP

報表可用 aiofiles 非同步寫檔