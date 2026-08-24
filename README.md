# Autonomous Employee-Data Import Agent

An AI agent that accepts a natural-language instruction (e.g. *"Create a
sample employee CSV and import it into Excel and Google Sheets"*), dynamically
decides which tools to call and in what order using a **LangGraph state
graph** backed by Gemini (free tier), executes them with retry logic, keeps
conversation memory across turns, and reports success/failure per step —
with no manual steps required after the command is issued.

## How it works

The agent is a LangGraph `StateGraph` with two nodes that loop until the
task is complete:

```
        ┌────────────┐
   ───► │   agent    │  Gemini decides: call a tool, or finish
        │  (Gemini)  │
        └─────┬──────┘
              │  tool call requested
              ▼
        ┌────────────┐
        │   tools    │  Executes generate_employee_csv /
        │  (ToolNode)│  import_csv_to_excel / import_csv_to_google_sheets
        └─────┬──────┘
              │  result fed back as a ToolMessage
              └──────────► back to "agent"
                            (loops until Gemini has no more tool calls,
                             then the graph ends and prints the report)
```

1. `agent.py` builds this graph and sends your instruction to the `agent`
   node, which asks Gemini (`gemini-2.0-flash`) to decide the next action.
2. Gemini is **not hardcoded to a fixed step order** — it reasons about the
   instruction and picks tools dynamically via `bind_tools`.
3. `langgraph.prebuilt.tools_condition` routes to the `tools` node whenever
   Gemini requests a tool call; `ToolNode` executes it and the result flows
   back to `agent` as a `ToolMessage`. This repeats until Gemini stops
   requesting tools.
4. Each tool call is retried up to 2 times on failure (`_with_retry`).
5. A `MemorySaver` checkpointer gives the agent memory across runs when you
   reuse the same `--thread` id (see "Running the agent" below).
6. A final structured report is built from the message history, showing
   ✅/❌ for every step.

### Tools available to the agent
| Tool | What it does |
|---|---|
| `generate_employee_csv` | Writes a CSV with 20+ rows of realistic sample employee data (via `faker`) |
| `import_csv_to_excel` | Launches real MS Excel via COM automation (Windows + Excel installed) and imports/saves the CSV as `.xlsx`. **Automatically falls back** to writing a real `.xlsx` file with `openpyxl` if Excel isn't available — and reports which method it used. |
| `import_csv_to_google_sheets` | Creates a new Google Sheet via the Sheets API and writes the CSV data into it |
| `import_csv_to_ods` | Writes the same data into a genuine OpenDocument Spreadsheet (`.ods`) file, for LibreOffice/OpenOffice compatibility |

These same tools are also exposed as a **standalone MCP server** (`mcp_server.py`) — see below.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a free Gemini API key
Go to https://aistudio.google.com/apikey → create a key (free tier is
sufficient for this task). Copy `.env.example` to `.env` and paste it in:
```bash
cp .env.example .env
# then edit .env and set GEMINI_API_KEY=...
```

### 3. Set up Google Sheets API access (free)
1. Go to https://console.cloud.google.com/ → create a project (or reuse one).
2. Enable the **Google Sheets API** for that project.
3. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
   - Application type: **Desktop app**.
4. Download the JSON file, rename it to `credentials.json`, and place it in
   the project root (same folder as `agent.py`).
5. The first time you run the agent, a browser window will open asking you
   to log into Google and approve access — this is normal OAuth consent.
   After approving once, a `token.json` is cached so you won't be asked again.

   > ⚠️ Never commit `credentials.json` or `token.json` to git — both are
   > already in `.gitignore`.

### 4. (Windows only, optional) Enable real Excel automation
If you have Microsoft Excel installed and licensed on your Windows machine:
```bash
pip install pywin32
```
No extra config needed — the agent detects Excel automatically. If Excel
isn't installed, the agent silently uses the `openpyxl` fallback and reports
that in the output — the workflow still fully succeeds either way.

## Running the agent
```bash
python agent.py "Create a sample employee CSV and import it into Excel and Google Sheets."
```

You can phrase the instruction differently — the model interprets it, e.g.:
```bash
python agent.py "Generate 25 fake employees, put them in Excel, then sync to Google Sheets."
```

### Memory across turns
Pass `--thread` with the same id across multiple invocations to give the
agent memory of earlier turns in that conversation (backed by LangGraph's
`MemorySaver` checkpointer):
```bash
python agent.py "Create the CSV and import it into Excel." --thread demo
python agent.py "Now also push it to Google Sheets, same file as before." --thread demo
```

### Example output
```
============================================================
AGENT EXECUTION REPORT
============================================================

Step 1: generate_employee_csv  -->  ✅ SUCCESS
  Args:   {"filename": "employees.csv", "num_rows": 20}
  Result: {"success": true, "path": "...employees.csv", "rows": 20, "error": null}

Step 2: import_csv_to_excel  -->  ✅ SUCCESS
  Args:   {"csv_path": "employees.csv", "xlsx_path": "employees.xlsx"}
  Result: {"success": true, "method": "openpyxl_fallback", "path": "employees.xlsx", "error": null}

Step 3: import_csv_to_google_sheets  -->  ✅ SUCCESS
  Args:   {"csv_path": "employees.csv", "sheet_title": "Employee Data"}
  Result: {"success": true, "spreadsheet_url": "https://docs.google.com/spreadsheets/d/...", "error": null}

------------------------------------------------------------
Summary: I generated 20 sample employees, saved them to Excel
(via openpyxl since Excel wasn't detected on this machine), and
uploaded the same data to a new Google Sheet. All steps succeeded.
============================================================
```

## Running tests
```bash
pytest tests/ -v
```
Tests mock all external dependencies (Excel COM, Google API), so they run
on any machine without credentials or Excel installed.

## MCP server (bonus)
The same tools are also exposed as a standalone MCP server, so any
MCP-compatible client (Claude Desktop, Claude Code, other agents) can call
them independently of this project's own LangGraph agent:

```bash
python mcp_server.py
```

To register it in Claude Desktop, add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "employee-agent-tools": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

## Docker (optional)
```bash
docker build -t employee-agent .
docker run --env-file .env -v $(pwd)/credentials.json:/app/credentials.json employee-agent
```
Note: inside Linux containers the Excel step always uses the `openpyxl`
fallback, since COM automation requires Windows.

## Project structure
```
employee-agent/
├── agent.py                 # Orchestrator: LangGraph agent<->tools loop, live progress
├── mcp_server.py             # Same tools exposed as a standalone MCP server
├── tools/
│   ├── csv_tool.py            # generate_employee_csv
│   ├── excel_tool.py          # import_csv_to_excel (COM + fallback)
│   ├── gsheets_tool.py         # import_csv_to_google_sheets
│   └── ods_tool.py             # import_csv_to_ods
├── tests/
│   └── test_tools.py          # unit tests (mocked externals)
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Bonus points — all covered
| Bonus | How it's covered |
|---|---|
| Multi-step planning before execution | Gemini plans the tool sequence via the LangGraph agent↔tools loop — nothing hardcoded |
| Memory or conversation history | `MemorySaver` checkpointer, keyed by `--thread` id |
| Additional spreadsheet formats | Produces `.csv`, `.xlsx`, **and** `.ods` |
| Retry logic for failed actions | Every tool call retries up to 2 times (`_with_retry`) |
| Configurable tools | Each tool is a `@tool`-decorated function in `TOOLS` — add one, no graph changes needed |
| MCP server integration | `mcp_server.py` exposes all 4 tools over MCP for any compatible client |
| Dockerized deployment | `Dockerfile` included |
| Unit tests | `tests/test_tools.py`, 8 tests, all external services mocked |
| Structured logging | JSON-formatted logs for every tool invocation |
| Progress updates while executing tasks | `agent.py` streams live 🤔/✅/❌ updates per step via `app.stream()`, not just a final report |

## Example prompts used
- `"Create a sample employee CSV and import it into Excel and Google Sheets."`
- `"Generate 30 employees and put them in both Excel and Google Sheets."`
- `"Also save this as an ODS file."`
