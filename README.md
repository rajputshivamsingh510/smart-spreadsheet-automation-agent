Smart Spreadsheet Automation Agent

An autonomous AI agent that understands natural-language instructions and performs real spreadsheet tasks using AI-powered tool calling.

🚀 Overview

Smart Spreadsheet Automation Agent turns simple instructions into real spreadsheet operations.

For example:

Create 20 sample employees and import them into Excel and Google Sheets.

Or:

Create a student CSV with 15 students including Student ID, Name, Grade, Email, and GPA. Import it into Excel.

The agent automatically decides which tools are required and executes them in the correct sequence.

User Instruction
       ↓
   AI Agent
       ↓
 Tool Selection
       ↓
   Generate CSV
       ↓
   Import Excel
       ↓
 Google Sheets / ODS
       ↓
 Execution Result

The project uses LangGraph, LangChain, Groq, Python tools, FastAPI, and a browser-based HTML/CSS/JavaScript frontend.

✨ Features

🤖 Autonomous AI tool selection

🧠 LangGraph agent workflow

🎯 Groq LLM

📄 Custom CSV generation with user-defined columns

📊 Excel .xlsx creation

☁️ Google Sheets integration

📋 ODS spreadsheet generation

🌐 HTML/CSS/JavaScript frontend

⚡ Real-time SSE execution updates

🧵 Conversation/thread memory

🔌 MCP tool server

📁 Session-based file management

🧪 Retry and error handling

🧠 Agent Architecture

The core principle is:

The AI decides what to do. The tools actually do it.

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

The tool sequence is not hardcoded. The agent dynamically chooses and chains tools based on the user's instruction.

🤖 AI Model

The agent currently uses Groq for LLM inference.

User Request
     ↓
   Groq LLM
     ↓
Tool Selection
     ↓
Tool Execution

🛠️ Spreadsheet Tools

Tool

Function

generate_employee_csv

Generates CSV data with custom columns

import_csv_to_excel

Creates an Excel .xlsx file

import_csv_to_google_sheets

Creates and populates a Google Sheet

import_csv_to_ods

Creates an .ods spreadsheet

Custom CSV Columns

The agent can generate data for different types of entities, not only employees.

Examples:

Student ID, Name, Grade, Email, GPA
Product ID, Name, Category, Price, Stock
Employee ID, Name, Department, Email, Salary

The requested columns are interpreted from the natural-language instruction.

Excel

openpyxl is used to create .xlsx files.

Microsoft Excel automation can also be used on Windows.

Google Sheets

Uses the Google Sheets API to create and populate spreadsheets automatically.

🌐 Frontend

The project includes a custom browser-based Agent Console built with:

HTML5

CSS3

Vanilla JavaScript

The frontend allows users to:

Enter natural-language instructions

Start agent runs

View the execution pipeline

Monitor tool calls

See success/failure states

View execution results

Download generated CSV, Excel, and ODS files

Open generated Google Sheets

The frontend communicates with the FastAPI backend using Server-Sent Events (SSE) for real-time execution updates.

Browser
   ↓
HTML / CSS / JavaScript
   ↓
FastAPI Backend
   ↓
LangGraph Agent
   ↓
Groq + Tools

🏗️ Project Structure

smart-spreadsheet-automation-agent/
│
├── agent.py              # LangGraph AI agent
├── server.py             # FastAPI backend + SSE streaming
├── mcp_server.py         # MCP tool server
├── cleanup_workspace.py  # Workspace cleanup
│
├── tools/
│   ├── csv_tool.py       # CSV generation
│   ├── excel_tool.py     # Excel automation
│   ├── gsheets_tool.py   # Google Sheets integration
│   └── ods_tool.py       # ODS generation
│
├── utils/
│   └── file_manager.py   # Session-based file management
│
├── static/
│   ├── index.html        # Frontend UI
│   ├── app.js            # Frontend logic / SSE client
│   └── style.css         # Frontend styling
│
├── workspace/            # Generated files
├── tests/                # Automated tests
├── requirements.txt
├── Dockerfile
└── README.md

⚙️ Tech Stack

AI & Agent

Python

LangChain

LangGraph

Groq

Spreadsheet Automation

Faker

openpyxl

Google Sheets API

Microsoft Excel automation

ODS

Frontend

HTML5

CSS3

JavaScript

Server-Sent Events (SSE)

Backend & Integration

FastAPI

MCP

🔧 Installation

Clone the repository:

git clone https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent.git
cd smart-spreadsheet-automation-agent

Create a virtual environment:

Windows

python -m venv venv
venv\Scripts\activate

macOS / Linux

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Create a .env file:

GROQ_API_KEY=your_groq_api_key_here

For Google Sheets, configure the required Google API credentials such as credentials.json.

▶️ Run

Start the FastAPI backend:

uvicorn server:app --reload --port 8000

Open the frontend:

http://localhost:8000

CLI

The agent can also be run directly:

python agent.py "Create 20 employees and import them into Excel and Google Sheets."

💬 Example Prompts

Employee

Create 20 sample employees and save them as CSV.

Student

Create a student CSV with 15 students including Student ID, Name, Grade, Email, and GPA. Import it into Excel.

Product

Create a product inventory CSV with Product ID, Name, Category, Price, Stock. Import it into Google Sheets.

Multi-step

Create 20 employees, import the data into Excel, and also save the same data as an ODS spreadsheet.

The agent determines the required tool sequence automatically.

🧵 Memory

The agent uses LangGraph memory/checkpointing to maintain context across turns.

Example:

Create the employee CSV and import it into Excel.

Then:

Now also put the same data into Google Sheets.

When the same thread is used, the agent can continue using the previous conversation context.

🔌 MCP Support

The spreadsheet tools are also available through a standalone MCP server.

python mcp_server.py

This allows compatible AI clients to access the spreadsheet tools independently of the main agent.

🧪 Testing

Run:

pytest tests/ -v

🎯 Project Goal

The goal of this project is to demonstrate how an AI agent can move beyond generating text and perform real-world actions through tools.

Instead of:

User → LLM → Text Response

the system enables:

User
 ↓
AI Agent
 ↓
Tool Selection
 ↓
Real-World Action
 ↓
Result

🎥 Demo

The project demonstration shows:

Natural-language task input through the web frontend.

Autonomous tool selection.

Real-time agent execution through SSE.

CSV generation with custom columns.

Excel / Google Sheets / ODS operations.

Generated files and final execution results.

Example Demo Task

Create a student CSV with 15 students including Student ID,
Name, Grade, Email, and GPA. Import it into Excel and also
save it as an ODS spreadsheet.

👤 Author

Shivam Singh Rajput

[GitHub](https://github.com/rajputshivamsingh510)

⭐ If you find the project useful, consider giving it a star.
