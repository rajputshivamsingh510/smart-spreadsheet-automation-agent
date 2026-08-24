# Smart Spreadsheet Automation Agent

> An autonomous AI agent that turns natural-language spreadsheet instructions into real actions across CSV, Excel, Google Sheets, and ODS — using tools, LangGraph, multiple LLM providers, and a live web interface.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-1C3C3C)](https://www.langchain.com/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4?logo=google)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/Groq-Fast_Inference-F55036)](https://groq.com/)
[![Mistral](https://img.shields.io/badge/Mistral-AI-FF7000)](https://mistral.ai/)
[![Google Sheets](https://img.shields.io/badge/Google-Sheets-34A853?logo=googlesheets\&logoColor=white)](https://www.google.com/sheets/about/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

## Overview

**Smart Spreadsheet Automation Agent** is an autonomous, tool-using AI system designed to perform real spreadsheet workflows from a single natural-language instruction.

Instead of simply answering:

> "Create a sample employee spreadsheet and put it in Excel and Google Sheets."

the agent actually performs the work.

It interprets the instruction, decides which tools are required, executes those tools in the appropriate order, observes their results, and continues until the requested workflow is complete.

The project combines:

* **LangGraph** for agent orchestration
* **LangChain** for LLM/tool integration
* **Gemini, Groq, and Mistral** as LLM providers
* **Automatic provider fallback** for reliability
* **Python tools** for CSV and spreadsheet operations
* **Microsoft Excel COM automation** when Excel is available
* **openpyxl fallback** when Excel is unavailable
* **Google Sheets API** for cloud spreadsheet creation
* **ODS generation** for LibreOffice/OpenOffice compatibility
* **MCP server support** for external agent clients
* **Web frontend** for interactive agent execution
* **Streaming execution logs** showing what the agent is doing
* **LangGraph memory** for multi-turn workflows

The repository contains both the **agent backend** and the **frontend console**, so it can be used as a complete AI automation application rather than only as a backend experiment.

---

## What Problem Does It Solve?

Traditional spreadsheet automation usually requires manually writing scripts or performing repetitive operations:

1. Create a CSV.
2. Open Excel.
3. Import the CSV.
4. Save it as `.xlsx`.
5. Open Google Sheets.
6. Create a spreadsheet.
7. Copy/import the data.
8. Repeat whenever the workflow changes.

This project replaces that manual workflow with an autonomous agent.

You can give it an instruction such as:

```text
Create 20 sample employees and import the data into Excel and Google Sheets.
```

The agent determines that it needs to:

```text
generate_employee_csv
        ↓
import_csv_to_excel
        ↓
import_csv_to_google_sheets
```

No fixed command sequence has to be manually selected by the user.

---

# Core Objective

The primary objective of the project is:

> **Build an autonomous AI agent capable of completing real-world tasks by using tools instead of relying solely on LLM responses.**

The agent accepts a natural-language instruction and determines which tools are required to complete the requested task.

This makes the project an example of **agentic AI + tool use + workflow automation**.

---

# Key Features

## 🤖 Autonomous Tool Selection

The user does not need to specify which Python function should run.

The LLM receives the user's instruction and decides whether it should:

* generate data
* create a CSV
* import data into Excel
* create a Google Sheet
* generate an ODS spreadsheet
* perform multiple operations sequentially

Tools are exposed to the model through LangChain's tool-binding mechanism.

---

## 🔄 Multi-Model LLM Architecture

The project is designed to support multiple LLM providers rather than depending entirely on one API.

Recommended provider priority:

```text
Gemini
   ↓
Groq
   ↓
Mistral
```

If the preferred provider becomes unavailable because of quota exhaustion, rate limiting, authentication problems, or another provider-level failure, the agent can fall back to the next configured provider.

This prevents a single model API from becoming a complete single point of failure.

### Example

```text
User request
     │
     ▼
 Gemini available?
   │       │
  YES      NO
   │       │
   ▼       ▼
 Gemini    Groq available?
             │       │
            YES      NO
             │       │
             ▼       ▼
            Groq   Mistral
```

This is particularly useful for free-tier development environments where model quotas can be exhausted.

---

# Agent Architecture

At the center of the project is a LangGraph state graph.

Conceptually:

```text
                    ┌──────────────────────┐
                    │   Natural Language   │
                    │       Request        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    LLM Provider      │
                    │ Gemini / Groq /       │
                    │ Mistral              │
                    └──────────┬───────────┘
                               │
                         Tool decision
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Agent Node       │
                    │  Decide next action  │
                    └──────────┬───────────┘
                               │
                        tool requested
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Tool Node       │
                    │ Execute real action  │
                    └──────────┬───────────┘
                               │
                         Tool result
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Agent Node       │
                    │ Evaluate next step   │
                    └──────────┬───────────┘
                               │
                     more tools required?
                         /             \
                       YES             NO
                        │               │
                        └───────┐       ▼
                                │   Final Report
                                │
                                └──► Tool Node
```

The important distinction is that the LLM does not directly perform spreadsheet operations.

It **decides what should happen**.

The tools **actually perform the operation**.

---

# Available Tools

| Tool                          | Purpose                                                          |
| ----------------------------- | ---------------------------------------------------------------- |
| `generate_employee_csv`       | Generates realistic sample employee data                         |
| `import_csv_to_excel`         | Converts/imports CSV into `.xlsx`                                |
| `import_csv_to_google_sheets` | Creates and populates a Google Sheet                             |
| `import_csv_to_ods`           | Creates an OpenDocument Spreadsheet                              |
| MCP tools                     | Expose the same functionality to external MCP-compatible clients |

---

## `generate_employee_csv`

Creates realistic sample employee data using Faker.

Example:

```text
generate_employee_csv(
    filename="employees.csv",
    num_rows=20
)
```

Produces a CSV containing sample employee records.

---

## `import_csv_to_excel`

Converts the generated CSV into an Excel workbook.

When Microsoft Excel is installed on Windows, the project can use real Excel automation through COM.

When Excel is unavailable, it falls back to `openpyxl`.

Conceptually:

```text
CSV
 │
 ├── Microsoft Excel available
 │       ↓
 │    Excel COM
 │       ↓
 │    XLSX
 │
 └── Excel unavailable
         ↓
      openpyxl
         ↓
       XLSX
```

This allows the workflow to continue even without a locally installed Excel application.

---

## `import_csv_to_google_sheets`

Uses the Google Sheets API to:

1. Authenticate with Google.
2. Create a new spreadsheet.
3. Read the CSV.
4. Upload the data.
5. Return the spreadsheet URL.

Example result:

```json
{
  "success": true,
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/..."
}
```

---

## `import_csv_to_ods`

Creates an actual `.ods` OpenDocument spreadsheet.

This provides compatibility with:

* LibreOffice
* OpenOffice
* other OpenDocument-compatible applications

---

# Frontend

The repository also contains a dedicated web frontend rather than exposing only the Python agent.

The frontend is implemented using:

* HTML
* CSS
* JavaScript

The interface acts as an **Agent Console** for interacting with the backend.

The repository's `static/` directory contains:

```text
static/
├── index.html
├── app.js
└── style.css
```

The interface provides:

* Natural-language instruction input
* Thread/session ID
* Run Agent button
* Live pipeline visualization
* Tool execution log
* Final execution report
* Step-by-step success/failure status
* Generated file downloads
* Google Sheets links

The frontend is designed to make the agent's execution observable instead of hiding everything behind a single loading spinner.

---

# Frontend Workflow

The web interface follows this flow:

```text
User enters instruction
        │
        ▼
     Run Agent
        │
        ▼
Backend receives request
        │
        ▼
LangGraph starts execution
        │
        ▼
LLM decides tool
        │
        ▼
Frontend receives streamed update
        │
        ▼
Pipeline station appears
        │
        ▼
Tool executes
        │
        ▼
Result appears in live log
        │
        ▼
Agent decides next action
        │
        ▼
Final report
```

The frontend therefore provides visibility into the agent's actual tool execution.

---

# Frontend Components

## Instruction Panel

The main input area allows the user to describe the desired workflow using natural language.

Example:

```text
Generate 50 employees and put the data into Excel and Google Sheets.
```

The user does not need to know the names of the underlying Python tools.

---

## Thread / Memory

The interface supports a thread ID.

Reusing a thread allows the LangGraph `MemorySaver` checkpointer to maintain conversation state.

For example:

```text
Turn 1:
Create the employee CSV and import it into Excel.

Turn 2:
Now also put the same data into Google Sheets.
```

The same thread can be used to preserve context between turns.

---

## Live Pipeline

The frontend dynamically displays the tools selected by the agent.

For example:

```text
GENERATE CSV
     ↓
IMPORT TO EXCEL
     ↓
IMPORT TO GOOGLE SHEETS
```

The pipeline is not simply a decorative progress bar.

The stations are generated from the agent's actual tool calls.

---

## Reasoning & Tool Log

The interface streams execution events so the user can see:

* what the agent decided to do
* which tool was selected
* whether the tool succeeded
* whether the tool failed
* relevant tool results

This makes debugging and demonstration much easier.

---

## Final Report

After execution, the frontend presents a structured report containing:

* step number
* tool name
* execution status
* output details
* generated files
* Google Sheets links
* final natural-language summary

---

# Backend Architecture

The project separates responsibilities across several components.

```text
smart-spreadsheet-automation-agent/
│
├── agent.py
├── server.py
├── app.py
├── mcp_server.py
├── cleanup_workspace.py
│
├── tools/
├── utils/
├── tests/
│
└── static/
    ├── index.html
    ├── app.js
    └── style.css
```

### `agent.py`

Core agent implementation.

Responsible for:

* LLM initialization
* system prompt
* LangGraph graph
* tool binding
* agent node
* tool execution
* memory/checkpointing
* execution reporting

### `server.py`

Backend HTTP server responsible for serving the web application and handling agent execution requests.

### `app.py`

Streamlit-based interface for running the agent through Streamlit.

This provides an alternative UI to the custom HTML/CSS/JavaScript frontend.

### `mcp_server.py`

Standalone MCP server exposing the spreadsheet tools to compatible external AI clients.

### `tools/`

Contains the actual task-execution tools.

### `utils/`

Supporting utilities used by the application.

### `tests/`

Automated tests for the project's core behavior and external integrations.

### `static/`

Custom browser frontend.

---

# MCP Support

The project also exposes the spreadsheet automation tools through an MCP server.

This allows other MCP-compatible AI systems to use the same tools without requiring them to use this project's LangGraph agent.

Start the MCP server with:

```bash
python mcp_server.py
```

The MCP architecture is:

```text
External AI Client
       │
       ▼
   MCP Protocol
       │
       ▼
 mcp_server.py
       │
       ▼
Spreadsheet Tools
```

This makes the project useful not only as a standalone application but also as a reusable tool server.

---

# Memory

The LangGraph workflow uses a checkpointer to support conversational memory.

A thread ID identifies a conversation.

Example:

```bash
python agent.py "Create the CSV and import it into Excel." --thread demo
```

Then:

```bash
python agent.py "Now also push it to Google Sheets." --thread demo
```

The same thread allows the agent to maintain context across executions.

---

# Execution Reporting

The system produces a structured execution report after the workflow finishes.

Example:

```text
============================================================
AGENT EXECUTION REPORT
============================================================

Step 1: generate_employee_csv
       SUCCESS

Step 2: import_csv_to_excel
       SUCCESS

Step 3: import_csv_to_google_sheets
       SUCCESS

------------------------------------------------------------
Summary:
Generated the employee dataset, created the Excel workbook,
and uploaded the same data to Google Sheets.
============================================================
```

This makes it easy to understand exactly what happened during an autonomous run.

---

# Error Handling

The project includes error handling at multiple levels.

### Tool-level failures

Individual spreadsheet operations return structured results containing information such as:

```json
{
  "success": false,
  "error": "..."
}
```

### Excel fallback

If Microsoft Excel cannot be accessed, the Excel import can fall back to `openpyxl`.

### LLM provider fallback

The multi-provider architecture can use:

```text
Gemini → Groq → Mistral
```

rather than allowing one unavailable provider to stop the complete workflow.

### Execution visibility

Failures are surfaced in the frontend and final execution report rather than silently disappearing.

---

# Example Tasks

The agent can interpret instructions such as:

### Employee Data

```text
Create a sample employee CSV with 50 rows and import it into Excel.
```

### Multiple Destinations

```text
Generate employee data and put it into Excel and Google Sheets.
```

### ODS

```text
Create a sample employee dataset and export it as an ODS spreadsheet.
```

### Multi-step Workflow

```text
Generate 100 employees, save the data as CSV, convert it to Excel,
and upload the same data to Google Sheets.
```

The important point is that the user describes the **goal**, not the implementation.

---

# Technology Stack

## AI / Agent

* Python
* LangChain
* LangGraph
* Gemini
* Groq
* Mistral
* Tool calling
* Stateful agent execution

## Data / Spreadsheet

* CSV
* pandas
* Faker
* openpyxl
* Microsoft Excel COM
* ODS
* Google Sheets API

## Backend

* Python
* HTTP server
* Streaming execution
* JSON-based communication

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* Responsive Agent Console UI

## Integrations

* Google Sheets API
* Microsoft Excel
* MCP

## Testing

* pytest
* Mocked external dependencies

## Deployment

* Docker support

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent.git

cd smart-spreadsheet-automation-agent
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

Configure the LLM provider credentials required by your setup.

Example:

```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
MISTRAL_API_KEY=your_mistral_key
```

For Google Sheets, configure the Google OAuth credentials described below.

> Never commit API keys, OAuth credentials, or generated tokens to Git.

---

# Google Sheets Setup

To enable Google Sheets integration:

1. Create or select a Google Cloud project.
2. Enable the Google Sheets API.
3. Create OAuth credentials.
4. Select **Desktop application** as the application type.
5. Download the credentials file.
6. Place it in the project root.
7. Run the application and complete the Google OAuth flow.

After authentication, the generated token can be reused for subsequent requests.

Credential and token files should remain excluded from Git.

---

# Microsoft Excel Support

The project can use real Microsoft Excel automation on Windows.

If Excel is installed and licensed:

```bash
pip install pywin32
```

The system can then use Excel COM automation.

If Excel is unavailable, the workflow can use `openpyxl` to create a valid `.xlsx` file instead.

This makes Excel export more portable across environments.

---

# Running the Agent

## CLI

Run:

```bash
python agent.py "Create a sample employee CSV and import it into Excel and Google Sheets."
```

Another example:

```bash
python agent.py "Generate 25 fake employees and put them into Excel."
```

---

# Running the Web Frontend

The project includes a browser-based agent console.

Start the backend server according to the project's server configuration, then open the application in your browser.

The frontend provides a graphical interface for:

* entering instructions
* starting agent runs
* watching tool execution
* viewing the pipeline
* inspecting the final report
* downloading generated files
* opening generated Google Sheets

---

# Streamlit Interface

The project also includes a Streamlit application.

Run:

```bash
streamlit run app.py
```

The Streamlit interface provides:

* instruction input
* thread/session management
* live progress
* tool execution status
* final reports
* generated-file downloads
* Google Sheets links

---

# Testing

Run:

```bash
pytest tests/ -v
```

The test suite is designed so that external integrations such as Google APIs and Excel automation can be mocked, allowing tests to run without requiring every external service.

---

# Docker

The repository also includes a `Dockerfile`.

Build:

```bash
docker build -t smart-spreadsheet-agent .
```

Run:

```bash
docker run --env-file .env smart-spreadsheet-agent
```

Google OAuth credentials can be mounted into the container when required.

---

# Project Structure

```text
smart-spreadsheet-automation-agent/
│
├── agent.py                    # Core LangGraph autonomous agent
├── server.py                   # Web/backend server
├── app.py                      # Streamlit frontend
├── mcp_server.py               # MCP tool server
├── cleanup_workspace.py        # Workspace cleanup utility
│
├── tools/
│   ├── csv_tool.py             # CSV generation
│   ├── excel_tool.py           # Excel import/export
│   ├── google_sheets_tool.py   # Google Sheets integration
│   └── ...
│
├── utils/
│   └── ...                     # Supporting utilities
│
├── tests/
│   └── ...                     # Automated tests
│
├── static/
│   ├── index.html              # Web UI
│   ├── app.js                  # Frontend behavior
│   └── style.css               # Frontend styling
│
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Design Philosophy

The project follows a simple principle:

> **The LLM decides. The tools execute.**

The model should not pretend that a file was created.

Instead:

```text
LLM
 ↓
Tool selection
 ↓
Real Python execution
 ↓
Real file/API operation
 ↓
Tool result
 ↓
LLM evaluates result
 ↓
Next action
```

This makes the system substantially closer to a real autonomous agent than a traditional chatbot.

---

# Why LangGraph?

LangGraph provides the stateful workflow layer needed for the agent.

The graph allows the system to:

* maintain state
* execute tools
* route between agent and tool nodes
* loop through multiple actions
* preserve conversation memory
* stream intermediate execution updates
* produce a final execution result

This architecture is especially useful for tasks where the number and order of actions depend on the user's instruction.

---

# Why Multiple LLM Providers?

A production-style agent should not depend entirely on a single model API.

For example, a provider may become unavailable because of:

* free-tier quota exhaustion
* rate limits
* temporary service issues
* invalid credentials
* model availability
* provider-side errors

Using a fallback chain improves resilience:

```text
Primary
Gemini
   ↓ failure
Secondary
Groq
   ↓ failure
Tertiary
Mistral
```

The spreadsheet tools themselves remain independent of the selected LLM provider.

---

# Security Notes

Never commit:

```text
.env
credentials.json
token.json
API keys
OAuth secrets
generated private datasets
```

Use environment variables for API credentials and keep authentication files out of version control.

---

# Limitations

The current project is primarily focused on spreadsheet-oriented automation.

Some operations depend on external requirements:

* Microsoft Excel automation requires Windows + Excel for the COM path.
* Google Sheets requires Google API credentials and authentication.
* LLM execution requires at least one configured provider.
* Internet access is required for cloud-based LLM and Google API operations.
* Provider quotas and rate limits may vary.

---

# Future Improvements

Potential extensions include:

* Excel file upload directly from the frontend
* Drag-and-drop spreadsheet input
* Spreadsheet analysis and visualization
* Formula generation
* Automatic chart creation
* Data cleaning
* CSV filtering and transformation
* Multiple spreadsheet file support
* Google Drive integration
* OneDrive integration
* Microsoft Excel Online integration
* More spreadsheet manipulation tools
* Persistent database-backed agent memory
* Authentication and multi-user sessions
* Job queue/background execution
* Provider health monitoring
* LLM usage/cost dashboard
* More advanced provider load balancing

---

# Project Goal

This project demonstrates how an AI system can move beyond generating text and actually **perform actions in the real world through tools**.

The broader architecture can be extended beyond spreadsheets to other domains such as:

```text
AI Agent
   │
   ├── Files
   ├── Excel
   ├── Google Sheets
   ├── APIs
   ├── Databases
   ├── Cloud Services
   ├── MCP Tools
   └── External Applications
```

The spreadsheet workflow is the foundation for building a more general-purpose autonomous task execution system.

---

# Author

**Shivam Singh Rajput**

GitHub:
https://github.com/rajputshivamsingh510

Repository:
https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent

---

# License

This project is available under the MIT License.
:::

