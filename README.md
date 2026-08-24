<div align="center">

⚡ Smart Spreadsheet Automation Agent

Give it a task. Let the agent figure out the tools. Get the result.

An autonomous AI agent for CSV, Excel, Google Sheets & ODS automation — powered by LangGraph + Groq.

<br>

<a href="https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent">GitHub</a>
  •  
<a href="#-demo">Demo</a>
  •  
<a href="#-features">Features</a>
  •  
<a href="#-architecture">Architecture</a>
  •  
<a href="#-quick-start">Quick Start</a>
  •  
<a href="#-example-prompts">Prompts</a>

<br><br>

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/LangGraph-Agent-1C3C3C?style=for-the-badge">
<img src="https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge">
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white">
<img src="https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">

</div>

<br>

✦ What is this?

Smart Spreadsheet Automation Agent is a tool-using AI agent that turns plain English into real spreadsheet workflows.

You don't tell it which Python function to call.

You tell it what you want done.

"Create a student dataset with Student ID, Name, Grade, Email and GPA,
then put it into Excel and save an ODS copy."

The agent decides the required tool sequence, executes the operations, streams progress to the browser, and returns the generated outputs.

The idea

        YOU
         │
         │  Natural language
         ▼
   ┌───────────────┐
   │   AI AGENT    │
   │   LangGraph   │
   └───────┬───────┘
           │
      Tool Selection
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
    CSV  Excel  ODS
           │
           ▼
     Google Sheets
           │
           ▼
        RESULT

The LLM decides. The tools execute.

🎬 Demo

The project includes a custom browser-based Agent Console built with HTML, CSS and JavaScript.

The UI shows the agent working instead of hiding everything behind a loading spinner.

A typical run

┌─────────────────────────────────────────────────────┐
│  SMART SPREADSHEET AGENT                            │
│                                                     │
│  Create 15 students with Student ID, Name, Grade,   │
│  Email and GPA. Import them into Excel and ODS.     │
│                                                     │
│                  [ RUN AGENT ]                      │
└─────────────────────────────────────────────────────┘

              LIVE EXECUTION

       ✓  Generate CSV
       ✓  Import to Excel
       ✓  Export to ODS
       ✓  Task completed

Real-time updates are streamed from the FastAPI backend using Server-Sent Events (SSE).

🎥 Recommended demo prompt

Create a student CSV with 15 students including Student ID,
Name, Grade, Email, and GPA. Import it into Excel and also
save it as an ODS spreadsheet.

Then show the generated:

CSV

Excel (.xlsx)

ODS (.ods)

For a second demonstration:

Create a product inventory with Product ID, Name, Category,
Price, and Stock. Import it into Google Sheets.

✨ Features

<table>
<tr>
<td width="50%">

🤖 Autonomous Tool Calling

The agent decides which tools are required from the user's goal.

🧠 LangGraph Workflow

Stateful, multi-step execution with memory and tool routing.

⚡ Groq

Fast LLM inference for agent decisions.

📄 Custom CSV Generation

Generate datasets for employees, students, products, or other entities.

</td>
<td width="50%">

📊 Excel

Create real .xlsx workbooks using openpyxl.

☁️ Google Sheets

Create and populate Google Sheets through the API.

📋 ODS

Export data into OpenDocument Spreadsheet format.

🌐 Live Web Console

Watch tool execution and results in real time.

</td>
</tr>
</table>

🧠 Architecture

┌──────────────────────────────────────┐
│              BROWSER                 │
│         HTML + CSS + JS              │
└──────────────────┬───────────────────┘
                   │
              HTTP + SSE
                   │
                   ▼
┌──────────────────────────────────────┐
│            FASTAPI SERVER             │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│            LANGGRAPH AGENT            │
│                                      │
│              GROQ LLM                │
└──────────────────┬───────────────────┘
                   │
              Tool Calling
                   │
          ┌────────┼─────────┐
          ▼        ▼         ▼
       CSV Tool Excel Tool  ODS Tool
                    │
                    ▼
              Google Sheets

The important part is that the workflow is not hardcoded.

For example, the user might ask for:

CSV + Excel

and the agent can choose:

generate_csv → import_excel

Another request might require:

generate_csv → import_excel → import_google_sheets → export_ods

The agent determines the sequence.

🛠️ Tools

Tool

What it does

generate_employee_csv

Generates CSV data with custom columns

import_csv_to_excel

Creates an .xlsx workbook

import_csv_to_google_sheets

Creates and populates a Google Sheet

import_csv_to_ods

Creates an .ods spreadsheet

Custom columns

The agent is not limited to employee data.

Student ID, Name, Grade, Email, GPA

Product ID, Name, Category, Price, Stock

Employee ID, Name, Department, Email, Salary

Tell the agent the columns in natural language and the CSV tool can generate the requested structure.

🌐 Frontend

The frontend is built with:

HTML5
CSS3
Vanilla JavaScript
Server-Sent Events (SSE)

The console provides

Natural-language task input

Agent execution controls

Live pipeline

Tool status

Execution logs

Generated file links

Google Sheets links

Final execution summary

Thread/session support

Browser
   │
   ├── Prompt
   │
   ▼
FastAPI
   │
   ├── Agent execution
   ├── Tool events
   └── SSE stream
   │
   ▼
Browser UI
   │
   ├── Pipeline
   ├── Logs
   └── Results

📁 Project Structure

smart-spreadsheet-automation-agent/
│
├── agent.py
├── server.py
├── mcp_server.py
├── cleanup_workspace.py
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
├── workspace/
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md

🧰 Tech Stack

<div align="center">

Layer

Technology

Agent

Python · LangChain · LangGraph

LLM

Groq

Backend

FastAPI

Frontend

HTML · CSS · Vanilla JavaScript

Streaming

Server-Sent Events

Spreadsheets

CSV · openpyxl · ODS

Cloud

Google Sheets API

Integration

MCP

Testing

pytest

</div>

⚡ Quick Start

1. Clone

git clone https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent.git
cd smart-spreadsheet-automation-agent

2. Create environment

Windows

python -m venv venv
venv\Scriptsctivate

macOS / Linux

python3 -m venv venv
source venv/bin/activate

3. Install

pip install -r requirements.txt

4. Add your API key

Create .env:

GROQ_API_KEY=your_groq_api_key

For Google Sheets, configure the required Google API/OAuth credentials.

5. Start

uvicorn server:app --reload --port 8000

Open:

<div align="center">

http://localhost:8000

</div>

💬 Example Prompts

👨‍💼 Employee

Create 20 sample employees and save them as CSV.

🎓 Student

Create a student CSV with 15 students including Student ID,
Name, Grade, Email, and GPA. Import it into Excel.

📦 Product

Create a product inventory with Product ID, Name, Category,
Price and Stock. Import it into Google Sheets.

🔗 Multi-tool workflow

Create 20 employees, import the data into Excel,
and also save the same data as an ODS spreadsheet.

🧠 Context-aware workflow

Create the employee CSV and import it into Excel.

Then:

Now put the same data into Google Sheets.

The same thread can preserve the previous context.

🔌 MCP

The spreadsheet tools can also be exposed through an MCP server.

python mcp_server.py

This allows compatible MCP clients to use the spreadsheet tools without running the main web interface.

🧪 Testing

pytest tests/ -v

🎯 Why this project?

Most LLM applications stop here:

User → LLM → Text

This project goes one step further:

User
 ↓
AI Agent
 ↓
Tool Selection
 ↓
Real Tool Execution
 ↓
Real Files / APIs
 ↓
Result

The goal is to demonstrate how an AI agent can reason about a task, select tools, execute actions, observe results, and complete a real workflow.

👤 Author

<div align="center">

Shivam Singh Rajput

<a href="https://github.com/rajputshivamsingh510">
  <img src="https://img.shields.io/badge/GitHub-rajputshivamsingh510-181717?style=for-the-badge&logo=github" alt="GitHub">
</a>

<a href="https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent">
  <img src="https://img.shields.io/badge/Project-Repository-4285F4?style=for-the-badge&logo=github" alt="Repository">
</a>

<br><br>

⭐ If you like the project, give it a star.

</div>
