<div align="center">

# ⚡ Smart Spreadsheet Automation Agent

**Describe the spreadsheet you want. The agent plans the steps, calls the right tools, and hands you real files.**

An autonomous LLM agent for CSV, Excel, Google Sheets, and ODS workflows — built on LangGraph + Groq, with live execution streamed to a browser console.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent-1C3C3C?style=for-the-badge)](https://www.langchain.com/langgraph)
[![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

[Demo](#-demo) · [Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [Example Prompts](#-example-prompts) · [MCP](#-mcp-support)

</div>

---

## What is this?

Most LLM apps stop at generating text. This one goes further — it's a **tool-using agent** that turns a plain-English request into an actual spreadsheet workflow, end to end.

You don't call a function. You describe an outcome:

> "Create a student dataset with Student ID, Name, Grade, Email and GPA, then put it into Excel and save an ODS copy."

The agent reasons about what that requires, picks a tool sequence on its own, executes each step, streams progress live to the browser, and returns downloadable files.

```
        you
         │  "create students, save as excel + ods"
         ▼
   ┌────────────────┐
   │   THE AGENT     │   LangGraph + Groq
   └────────┬────────┘
            │  decides the plan
            ▼
   generate_csv → import_excel → export_ods
            │
            ▼
        real files
```

The workflow is **not hardcoded**. Ask for a CSV + Excel export and the agent chains `generate_csv → import_excel`. Ask for CSV + Excel + Sheets + ODS and it chains all four. The plan comes from the model, not an if/else tree.

---

## 🎬 Demo

A custom browser-based **Agent Console** (HTML/CSS/vanilla JS) shows the agent thinking and working in real time, instead of hiding everything behind a spinner.

```
┌──────────────────────────────────────────────────────┐
│  SMART SPREADSHEET AGENT                              │
│                                                        │
│  Create 15 students with Student ID, Name, Grade,     │
│  Email and GPA. Import them into Excel and ODS.       │
│                                                        │
│                   [ RUN AGENT ]                        │
├──────────────────────────────────────────────────────┤
│  LIVE EXECUTION                                        │
│   ✓  Generate CSV                                      │
│   ✓  Import to Excel                                   │
│   ✓  Export to ODS                                     │
│   ✓  Task completed                                    │
└──────────────────────────────────────────────────────┘
```

Updates stream from the FastAPI backend to the browser over **Server-Sent Events (SSE)** — no polling, no refresh.

**Try it yourself:**

```
Create a student CSV with 15 students including Student ID,
Name, Grade, Email, and GPA. Import it into Excel and also
save it as an ODS spreadsheet.
```

```
Create a product inventory with Product ID, Name, Category,
Price, and Stock. Import it into Google Sheets.
```

---

## ✨ Features

| | |
|---|---|
| 🤖 **Autonomous tool calling** — the agent infers which tools a request needs, without a fixed pipeline | 📊 **Excel export** — real `.xlsx` workbooks via `openpyxl` |
| 🧠 **LangGraph workflow** — stateful, multi-step execution with memory across turns | ☁️ **Google Sheets** — creates and populates sheets through the Sheets API |
| ⚡ **Groq inference** — fast tool-planning and generation | 📋 **ODS export** — OpenDocument Spreadsheet output |
| 📄 **Custom CSV generation** — any column schema, described in natural language | 🌐 **Live console** — watch the plan execute step by step over SSE |

---

## 🧠 Architecture

```
┌────────────────────────────────────┐
│              BROWSER                │
│         HTML + CSS + JS             │
└──────────────────┬──────────────────┘
                    │  HTTP + SSE
                    ▼
┌────────────────────────────────────┐
│           FASTAPI SERVER            │
└──────────────────┬──────────────────┘
                    ▼
┌────────────────────────────────────┐
│          LANGGRAPH AGENT            │
│              (Groq LLM)             │
└──────────────────┬──────────────────┘
                    │  tool calling
       ┌────────────┼─────────────┐
       ▼            ▼             ▼
  CSV Tool     Excel Tool     ODS Tool
                    │
                    ▼
             Google Sheets Tool
```

Two example plans the agent can produce from the same tool set, depending on what's asked:

```
"csv + excel"                →  generate_csv → import_excel
"csv + excel + sheets + ods" →  generate_csv → import_excel → import_google_sheets → export_ods
```

### Tools

| Tool | What it does |
|---|---|
| `generate_employee_csv` | Generates CSV data with custom, user-described columns |
| `import_csv_to_excel` | Creates an `.xlsx` workbook from the CSV |
| `import_csv_to_google_sheets` | Creates and populates a Google Sheet |
| `import_csv_to_ods` | Creates an `.ods` spreadsheet |

The CSV generator isn't limited to one schema — describe the columns and it adapts:

- `Student ID, Name, Grade, Email, GPA`
- `Product ID, Name, Category, Price, Stock`
- `Employee ID, Name, Department, Email, Salary`

---

## ⚡ Quick Start

### 1. Clone

```bash
git clone https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent.git
cd smart-spreadsheet-automation-agent
```

### 2. Create a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

For Google Sheets support, add your Google API / OAuth credentials as well.

### 5. Run

```bash
uvicorn server:app --reload --port 8000
```

Open **[http://localhost:8000](http://localhost:8000)**.

---

## 💬 Example Prompts

**Employee data**
```
Create 20 sample employees and save them as CSV.
```

**Student data → Excel**
```
Create a student CSV with 15 students including Student ID,
Name, Grade, Email, and GPA. Import it into Excel.
```

**Product data → Google Sheets**
```
Create a product inventory with Product ID, Name, Category,
Price and Stock. Import it into Google Sheets.
```

**Multi-tool workflow**
```
Create 20 employees, import the data into Excel,
and also save the same data as an ODS spreadsheet.
```

**Context-aware follow-up** — the same thread remembers what came before:
```
1) Create the employee CSV and import it into Excel.
2) Now put the same data into Google Sheets.
```

---

## 🔌 MCP Support

The spreadsheet tools can also be exposed through an MCP server, so any MCP-compatible client can use them without the web console:

```bash
python mcp_server.py
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 📁 Project Structure

```
smart-spreadsheet-automation-agent/
├── agent.py                # LangGraph agent definition
├── server.py                # FastAPI app + SSE streaming
├── mcp_server.py             # MCP server exposing the tools
├── cleanup_workspace.py      # Workspace/file cleanup
│
├── tools/
│   ├── csv_tool.py
│   ├── excel_tool.py
│   ├── gsheets_tool.py
│   └── ods_tool.py
│
├── utils/
│   └── file_manager.py
│
├── static/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── workspace/                # Generated files land here
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Agent | Python · LangChain · LangGraph |
| LLM | Groq |
| Backend | FastAPI |
| Frontend | HTML · CSS · Vanilla JavaScript |
| Streaming | Server-Sent Events |
| Spreadsheets | CSV · openpyxl · ODS |
| Cloud | Google Sheets API |
| Integration | MCP |
| Testing | pytest |

---

## 🎯 Why this project?

Most LLM demos stop at:

```
User → LLM → Text
```

This one closes the loop:

```
User → Agent → Tool Selection → Real Execution → Real Files / APIs → Result
```

The point isn't the spreadsheets — it's demonstrating an agent that reasons about a goal, picks its own tools, executes real actions, observes the outcome, and completes a multi-step workflow without a hardcoded pipeline.

---

<div align="center">

## 👤 Author

**Shivam Singh Rajput**

[![GitHub](https://img.shields.io/badge/GitHub-rajputshivamsingh510-181717?style=for-the-badge&logo=github)](https://github.com/rajputshivamsingh510)
[![Repository](https://img.shields.io/badge/Project-Repository-4285F4?style=for-the-badge&logo=github)](https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent)

⭐ If you find this useful, a star helps a lot.

</div>
