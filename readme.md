# AI Chatbot 🤖💬

## 小組：第9組

### 組員：

- 呂紹銘
- 曹世杰
- 林楷祐

## 專案簡介

本專案是一個基於 **FastAPI**、**SQLite** 以及 **Google Gemini API** (`gemini-2.5-flash`) 搭建的 AI 聊天機器人應用程式。它不僅支援純文字對話，更具備強大的**多模態處理能力**（能夠上傳圖片與文件供 AI 讀取與分析），並內建一個簡單直觀的網頁前端介面。

## 目前功能

- **⚡ 現代化後端框架**：使用 FastAPI 構建，支援生成 Swagger UI (`/docs`) API 文件。
- **🧠 整合 Google Gemini AI**：使用 Google GenAI SDK 介接強大的 `gemini-2.5-flash` 模型。
- **📂 多模態檔案支援**：支援上傳圖片、文件等附件，可由 AI 進行視覺與文件內容分析。
- **🗄️ 歷史對話紀錄儲存**：結合 SQLAlchemy 與 SQLite 自動記錄每個 Session 的完整歷史軌跡。
- **🎭 System Prompts**：建立 Session 時支援自訂 System Prompt，讓 AI 扮演特定角色。
- **🌐 內建網頁介面**：開啟網址即可直接瀏覽內建的聊天 UI。

## 執行方式

1. 下載專案並切換到專案目錄。
2. 建立並啟動虛擬環境 (Virtual Environment)。
3. 安裝必要的依賴套件。
4. 設定環境變數 (`.env`)。
5. 啟動 FastAPI 伺服器並開啟瀏覽器。

詳細指令範例：

```bash
# 1. 建立並啟動虛擬環境 (Windows)
python -m venv venv
.\venv\Scripts\activate

# 2. 安裝必要的依賴套件
pip install fastapi uvicorn sqlalchemy python-dotenv "google-genai" python-multipart

# 3. 啟動伺服器 (開發模式)
python -m uvicorn main:app --reload
```

_伺服器啟動後，請開啟瀏覽器前往 http://127.0.0.1:8000 即可看到網頁介面。_

---

## 環境變數說明

請確保專案根目錄下有一個 `.env` 檔案，並填入你的 Google Gemini API key。

範例：

```env
GEMINI_API_KEY=your_api_key_here
```

## 遇到的問題與解法

### 問題 1

問題：執行 `uvicorn main:app --reload` 時出現 `Fatal error in launcher: Unable to create process using...` 錯誤。
解法：這通常發生在 Windows 環境下，虛擬環境 (`venv`) 資料夾被移動過或路徑錯誤所導致。改用 `python -m uvicorn main:app --reload` 透過 Python 模組方式啟動即可解決，或刪除 `venv` 資料夾重新建立。

### 問題 2

問題：組員之間作業系統不同，導致venv無法直接通用
解法：在另一個系統重新製作一份venv，並安裝相同的套件，或是使用 `requirements.txt` 來管理依賴套件，讓其他組員可以透過 `pip install -r requirements.txt` 快速安裝相同的環境。

---

## 學習心得

呂紹銘： 這次在重新開啟專案時，因為忘記了啟動的指令與流程，所以借助了 AI 的幫忙來還原。過程中遇到了 `venv` 虛擬環境因為路徑跑掉或相容性問題導致無法啟動伺服器（Fatal error in launcher）。透過與 AI 的對話與除錯，我學到了可以改用 `python -m uvicorn` 的方式來避免執行檔路徑綁定的問題，同時也複習了如何砍掉重練、重新建立乾淨的 Python 虛擬環境並安裝依賴套件。這讓我對 Python 專案的環境配置有更深的認識。

曹世杰：GitHub 上的專案管理與版本控制是非常重要的技能，這次作業讓我更熟悉了如何使用 Git 來管理專案的不同版本，並且學會了如何在團隊中協作開發。

---

## GitHub 專案連結

請填入小組各組員 GitHub repository 網址。

- 曹世杰 https://github.com/Grayidea-bit/AIAGENT
- 林楷祐 https://github.com/KyleLin0501/AI-Agent-ChatBot.git
