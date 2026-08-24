# Smart Spreadsheet Automation Agent

> An autonomous AI agent that understands natural-language instructions and performs real spreadsheet tasks using AI-powered tool calling.

## 🚀 Overview

**Smart Spreadsheet Automation Agent** turns simple instructions into real spreadsheet operations.

For example:

```text
Create 20 sample employees and import them into Excel and Google Sheets.
```

The agent automatically decides which tools are required and executes them in the correct sequence.

```text
User Instruction
       ↓
   AI Agent
       ↓
 Tool Selection
       ↓
 ┌───────────────┐
 │ Generate CSV  │
 └───────┬───────┘
         ↓
 ┌───────────────┐
 │ Import Excel  │
 └───────┬───────┘
         ↓
 ┌──────────────────┐
 │ Google Sheets    │
 └───────┬──────────┘
         ↓
   Execution Result
```

The project is built around **LangGraph, LangChain, Python tools, and a browser-based HTML/CSS/JavaScript frontend**.

---

## ✨ Features

* 🤖 Autonomous AI tool selection
* 🧠 LangGraph agent workflow
* 🔄 Gemini → Groq → Mistral fallback
* 📄 CSV generation
* 📊 Excel `.xlsx` creation
* ☁️ Google Sheets integration
* 📋 ODS spreadsheet generation
* 🌐 HTML/CSS/JavaScript frontend
* ⚡ Live agent execution updates
* 🧵 Conversation/thread memory
* 🔌 MCP tool server
* 🧪 Automated tests

---

## 🧠 Agent Architecture

The agent follows a simple principle:

> **The AI decides what to do. The tools actually do it.**

```text
Natural Language Request
          ↓
      LLM Agent
          ↓
    Tool Selection
          ↓
     Tool Execution
          ↓
      Tool Result
          ↓
   More actions required?
       ↓        ↓
      YES       NO
       ↓         ↓
     Tool     Final Report
```

The tool sequence is **not hardcoded**. The agent can dynamically choose and chain tools based on the user's instruction.

---

## 🤖 AI Model Fallback

Multiple LLM providers are supported for reliability:

```text
Gemini
  ↓ unavailable / quota exceeded
Groq
  ↓ unavailable
Mistral
```

This allows the agent to continue operating when a provider reaches its quota or becomes temporarily unavailable.

---

## 🛠️ Spreadsheet Tools

| Tool                          | Function                             |
| ----------------------------- | ------------------------------------ |
| `generate_employee_csv`       | Generates sample employee data       |
| `import_csv_to_excel`         | Creates an Excel `.xlsx` file        |
| `import_csv_to_google_sheets` | Creates and populates a Google Sheet |
| `import_csv_to_ods`           | Creates an `.ods` spreadsheet        |

### Excel

The Excel tool supports:

* Microsoft Excel COM automation on Windows
* `openpyxl` fallback when Excel is unavailable

### Google Sheets

The Google Sheets tool uses the Google Sheets API to create and populate spreadsheets automatically.

---

## 🌐 Frontend

The project includes a custom **browser-based Agent Console** built with:

* HTML
* CSS
* JavaScript

The frontend allows users to:

* Enter natural-language instructions
* Start agent runs
* View the execution pipeline
* Monitor tool calls
* See success/failure states
* View execution results
* Access generated files
* Open generated Google Sheets

The frontend communicates with the Python backend and displays the agent's progress in real time.

```text
Browser
   ↓
HTML / CSS / JavaScript
   ↓
Python Backend
   ↓
LangGraph Agent
   ↓
AI Model + Tools
```

---

## 🏗️ Project Structure

```text
smart-spreadsheet-automation-agent/
│
├── agent.py              # LangGraph AI agent
├── server.py             # Backend server
├── mcp_server.py         # MCP tool server
├── cleanup_workspace.py  # Workspace cleanup
│
├── tools/
│   ├── csv_tool.py       # CSV generation
│   ├── excel_tool.py     # Excel automation
│   ├── gsheets_tool.py   # Google Sheets
│   └── ods_tool.py       # ODS generation
│
├── static/
│   ├── index.html        # Frontend
│   ├── app.js            # Frontend logic
│   └── style.css         # Frontend styling
│
├── tests/                # Automated tests
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## ⚙️ Tech Stack

### AI & Agent

* Python
* LangChain
* LangGraph
* Gemini
* Groq
* Mistral

### Spreadsheet Automation

* pandas
* Faker
* openpyxl
* Google Sheets API
* Microsoft Excel COM
* ODS

### Frontend

* HTML5
* CSS3
* JavaScript

### Integration

* MCP
* REST/API communication

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

Google Sheets functionality additionally requires Google API credentials.

---

## ▶️ Run

### Start the backend

```bash
uvicorn server:app --reload --port 8000
```

Then open the frontend in your browser through the local server.

### Run the agent directly

```bash
python agent.py "Create 20 employees and import them into Excel and Google Sheets."
```

---

## 💬 Example Instructions

```text
Create 20 sample employees and save them as CSV.
```

```text
Generate 50 employees and import them into Excel.
```

```text
Create employee data and put it into Excel and Google Sheets.
```

```text
Also save the same data as an ODS file.
```

The agent determines the required tool sequence automatically.

---

## 🧵 Memory

The agent uses LangGraph's memory/checkpointing to maintain context across turns.

Example:

```text
Create the employee CSV and import it into Excel.
```

Then:

```text
Now also put the same data into Google Sheets.
```

The agent can continue working with the previous conversation context when the same thread is used.

---

## 🔌 MCP Support

The spreadsheet tools are also available through a standalone MCP server.

```bash
python mcp_server.py
```

This allows compatible AI clients to use the spreadsheet automation tools independently of the main agent.

---

## 🧪 Testing

Run:

```bash
pytest tests/ -v
```

External services such as Google Sheets and Excel can be mocked during testing.

---

## 🎯 Project Goal

The goal of this project is to demonstrate how an AI agent can move beyond generating text and **perform real-world actions through tools**.

Instead of:

```text
User → LLM → Text Response
```

the system enables:

```text
User
 ↓
AI Agent
 ↓
Tool Selection
 ↓
Real-World Action
 ↓
Result
```

This architecture can be extended to many other forms of automation beyond spreadsheets.

---

## 👤 Author

**Shivam Singh Rajput**

[GitHub](https://github.com/rajputshivamsingh510)

⭐ If you find the project useful, consider giving it a star.
