# NTHU_Python
國立清華大學 - Python 程式語言入門作業

## 說明
1. 此專案使用 MongoDB 作為資料庫
2. 支援 .env 檔案設定資料庫連線資訊
3. 支援帳號系統，在開始使用前必須先註冊帳號
   - 輸入密碼時不會顯示輸入的字元
   - 註冊帳號時需要先輸入原始餘額
4. 成功登入後，可以透過以下指令操作記帳系統
   - `add`: 新增一筆記帳資料（會自動加入時間戳記）
   - `list`: 列出所有記帳資料
   - `delete`: 刪除一筆記帳資料
   - `update`: 更新一筆記帳資料
   - `balance`: 計算目前餘額
## 安裝
- `pip install pymongo`
- `pip install python-dotenv`

## 執行
- `python3 pymoney.py`
