# Smart Spreadsheet Automation Agent

> An autonomous AI agent that understands natural-language spreadsheet tasks and uses real tools to execute them across CSV, Excel, Google Sheets, and ODS.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-1C3C3C)](https://www.langchain.com/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/Groq-LLM-F55036)](https://groq.com/)
[![Mistral](https://img.shields.io/badge/Mistral-LLM-FF7000)](https://mistral.ai/)

## 🚀 Overview

**Smart Spreadsheet Automation Agent** converts natural-language instructions into real spreadsheet operations.

Instead of simply responding with text, the agent decides which tools are required and executes them autonomously.

### Example

```text
"Create 20 sample employees and import them into Excel and Google Sheets."
```

The agent can automatically perform:

```text
User Request
     ↓
LLM Agent
     ↓
Generate CSV
     ↓
Import to Excel
     ↓
Import to Google Sheets
     ↓
Execution Report
```

---

## ✨ Features

* 🤖 Autonomous tool selection
* 🧠 LangGraph-based agent workflow
* 🔄 **Gemini → Groq → Mistral** provider fallback
* 📄 CSV generation
* 📊 Excel `.xlsx` creation
* ☁️ Google Sheets integration
* 📋 ODS spreadsheet support
* 🌐 Interactive web frontend
* ⚡ Live tool execution logs
* 🧵 Thread-based conversation memory
* 🔌 MCP server support
* 🐳 Docker support

---

## 🧠 How It Works

The core principle is:

> **The LLM decides. The tools execute.**

```text
Natural Language Request
          ↓
     Agent / LLM
          ↓
    Tool Selection
          ↓
     Tool Execution
          ↓
      Tool Result
          ↓
    More actions?
      ↙       ↘
    Yes        No
     ↓          ↓
   Tool      Final Report
```

The agent can dynamically select and chain multiple tools depending on the user's request.

---

## 🤖 LLM Fallback

The project supports multiple LLM providers for reliability:

```text
Gemini
   ↓ unavailable / quota exceeded
Groq
   ↓ unavailable
Mistral
```

This prevents the entire agent from stopping when one provider reaches its quota or becomes unavailable.

---

## 🛠️ Available Tools

| Tool                          | Purpose                           |
| ----------------------------- | --------------------------------- |
| `generate_employee_csv`       | Generate sample employee data     |
| `import_csv_to_excel`         | Create an Excel workbook          |
| `import_csv_to_google_sheets` | Create and populate Google Sheets |
| `import_csv_to_ods`           | Create an ODS spreadsheet         |

---

## 🎨 Frontend

The project includes a browser-based **Agent Console** built with:

* HTML
* CSS
* JavaScript

The frontend allows users to:

* Enter natural-language instructions
* Start agent executions
* View the live execution pipeline
* Monitor tool calls
* See success/failure states
* Download generated files
* Open generated Google Sheets

Example:

```text
┌─────────────────────────────────────────┐
│        Smart Spreadsheet Agent          │
│                                         │
│  Create 50 employees and put them      │
│  into Excel and Google Sheets.          │
│                                         │
│              [ Run Agent ]              │
│                                         │
│  ✓ Generate CSV                         │
│  ✓ Import to Excel                      │
│  ✓ Import to Google Sheets              │
└─────────────────────────────────────────┘
```

---

## 🏗️ Project Structure

```text
smart-spreadsheet-automation-agent/
│
├── agent.py              # LangGraph agent
├── server.py             # Backend server
├── app.py                # Streamlit interface
├── mcp_server.py         # MCP server
│
├── tools/                # Spreadsheet tools
├── utils/                # Utilities
├── tests/                # Tests
│
└── static/
    ├── index.html        # Frontend
    ├── app.js
    └── style.css
```

---

## ⚙️ Tech Stack

**AI & Agent**

* Python
* LangChain
* LangGraph
* Gemini
* Groq
* Mistral

**Spreadsheet**

* pandas
* Faker
* openpyxl
* Google Sheets API
* ODS

**Frontend**

* HTML
* CSS
* JavaScript
* Streamlit

**Integration**

* MCP
* Docker

---

## 🔧 Installation

```bash
git clone https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent.git
cd smart-spreadsheet-automation-agent

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
MISTRAL_API_KEY=your_key
```

Configure Google Sheets credentials if Google Sheets functionality is required.

---

## ▶️ Run

### Agent

```bash
python agent.py "Create 20 employees and import them into Excel."
```

### Web Frontend

Start the backend server and open the provided local address in your browser.

### Streamlit

```bash
streamlit run app.py
```

### MCP Server

```bash
python mcp_server.py
```

---

## 📌 Example Tasks

```text
Create 20 sample employees and save them as CSV.
```

```text
Generate employee data and import it into Excel.
```

```text
Create 50 employees and put the data into Excel and Google Sheets.
```

```text
Generate an employee dataset and export it as ODS.
```

The agent determines the required tool sequence automatically.

---

## 🔮 Future Improvements

* Spreadsheet analysis and visualization
* Automatic charts and formulas
* File upload through the frontend
* Google Drive / OneDrive integration
* More spreadsheet manipulation tools
* Persistent database-backed memory
* Advanced provider load balancing

---

## 👤 Author

**Shivam Singh Rajput**

GitHub: [@rajputshivamsingh510](https://github.com/rajputshivamsingh510)

⭐ If you find this project useful, consider giving it a star.
