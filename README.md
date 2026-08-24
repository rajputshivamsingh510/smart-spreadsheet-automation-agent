Smart Spreadsheet Automation Agent

<p align="center">
  <b>Turn natural-language instructions into real spreadsheet actions.</b><br>
  Built with LangGraph, Groq, FastAPI, and a modern HTML/CSS/JavaScript frontend.
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#demo">Demo</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#installation">Installation</a> •
  <a href="#example-prompts">Examples</a>
</p>

<p align="center">
  <a href="https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LangGraph-Agent-1C3C3C" alt="LangGraph">
  <img src="https://img.shields.io/badge/Groq-LLM-F55036" alt="Groq">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI">
</p>

🚀 Overview

Smart Spreadsheet Automation Agent is an autonomous AI agent that accepts a natural-language task, decides which tools are required, and executes the workflow for the user.

Instead of only generating a text response, the agent performs real operations such as:

Generate custom CSV data

Create Excel .xlsx files

Create and populate Google Sheets

Export data to ODS

Chain multiple tools in one task

Example

"Create a student CSV with 15 students including Student ID, Name, Grade, Email, and GPA. Import it into Excel and save it as ODS."

The agent determines the required sequence automatically.

✨ Features



Feature

Description

🤖

Autonomous Agent

Dynamically selects and chains tools

🧠

LangGraph

Stateful multi-step agent workflow

⚡

Groq

Fast LLM inference

📄

Custom CSV

Generate datasets with user-defined columns

📊

Excel

Create .xlsx files with openpyxl

☁️

Google Sheets

Create and populate spreadsheets

📋

ODS

OpenDocument spreadsheet support

🌐

Web UI

HTML + CSS + JavaScript frontend

📡

SSE

Real-time execution updates

🧵

Memory

Thread-based conversation context

🔌

MCP

Expose spreadsheet tools to MCP clients

🎬 Demo

The browser interface provides an Agent Console where you can:

Enter a natural-language instruction

Start the agent

Watch the tool pipeline execute in real time

View success/failure states

Download generated files

Open generated Google Sheets

Review the final execution report

Main demo prompt:

Create a student CSV with 15 students including Student ID,
Name, Grade, Email, and GPA. Import it into Excel and also
save it as an ODS spreadsheet.

🧠 Architecture

The AI decides. The tools execute.

┌──────────────────────────┐
│     HTML / CSS / JS      │
│       Agent Console      │
└────────────┬─────────────┘
             │ SSE / HTTP
             ▼
┌──────────────────────────┐
│      FastAPI Backend     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     LangGraph Agent      │
│                          │
│       Groq LLM           │
└────────────┬─────────────┘
             │ Tool Calling
             ▼
┌─────────────────────────────────────┐
│              Tools                  │
│                                     │
│ CSV → Excel → Google Sheets → ODS   │
└─────────────────────────────────────┘

The tool sequence is not hardcoded. The agent decides which tools are needed based on the user's goal.

🛠️ Tools

Tool

Purpose

generate_employee_csv

Generate CSV data with custom columns

import_csv_to_excel

Create an Excel workbook

import_csv_to_google_sheets

Create and populate Google Sheets

import_csv_to_ods

Create an ODS spreadsheet

Custom Data

The agent can work with different entities, not only employees:

Student ID, Name, Grade, Email, GPA
Product ID, Name, Category, Price, Stock
Employee ID, Name, Department, Email, Salary

🌐 Frontend

The frontend is built entirely with:

HTML5

CSS3

Vanilla JavaScript

Server-Sent Events (SSE)

It provides:

Natural-language prompt input

Live pipeline visualization

Tool execution logs

Step status

Generated file links

Google Sheets links

Final execution summary

Browser
   ↓
HTML / CSS / JS
   ↓
FastAPI
   ↓
LangGraph
   ↓
Groq + Tools

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

AI & Agent: Python · LangChain · LangGraph · Groq

Backend: FastAPI · Server-Sent Events

Frontend: HTML5 · CSS3 · Vanilla JavaScript

Spreadsheet: Faker · openpyxl · Google Sheets API · ODS

Integration: MCP

⚙️ Installation

1. Clone

git clone https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent.git
cd smart-spreadsheet-automation-agent

2. Virtual environment

Windows

python -m venv venv
venv\Scripts\activate

macOS / Linux

python3 -m venv venv
source venv/bin/activate

3. Dependencies

pip install -r requirements.txt

4. Environment

Create .env:

GROQ_API_KEY=your_groq_api_key

For Google Sheets, configure the required Google API/OAuth credentials.

▶️ Run

Start the FastAPI server:

uvicorn server:app --reload --port 8000

Open:

http://localhost:8000

Or run the agent directly:

python agent.py "Create 20 employees and import them into Excel and Google Sheets."

💬 Example Prompts

Employee

Create 20 sample employees and save them as CSV.

Student

Create a student CSV with 15 students including Student ID,
Name, Grade, Email, and GPA. Import it into Excel.

Product

Create a product inventory with Product ID, Name, Category,
Price, and Stock. Import it into Google Sheets.

Multi-tool

Create 20 employees, import the data into Excel,
and also save the same data as an ODS spreadsheet.

The user describes the goal, not the implementation. The agent determines the tool sequence.

🧵 Memory

The agent uses LangGraph checkpointing to maintain context across turns.

Turn 1:
Create the employee CSV and import it into Excel.

Turn 2:
Now also put the same data into Google Sheets.

Using the same thread allows the agent to continue with the previous context.

🔌 MCP

The spreadsheet tools can also be exposed through the MCP server:

python mcp_server.py

This allows compatible AI clients to use the tools independently of the main web application.

🧪 Testing

pytest tests/ -v

🎯 Project Goal

The project demonstrates a core agentic AI concept:

Traditional:
User → LLM → Text

This project:
User
  ↓
AI Agent
  ↓
Tool Selection
  ↓
Real-World Action
  ↓
Result

The same architecture can be extended to other real-world automation tasks.

👤 Author

Shivam Singh Rajput

<a href="https://github.com/rajputshivamsingh510">GitHub</a> ·
<a href="https://github.com/rajputshivamsingh510/smart-spreadsheet-automation-agent">Repository</a>

<p align="center">
  ⭐ If you find this project useful, consider giving it a star.
</p>
