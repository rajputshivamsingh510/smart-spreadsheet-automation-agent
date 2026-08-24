"""
Autonomous AI Agent — LangGraph edition with Groq
----------------------------------------
Accepts a natural-language instruction, and uses a LangGraph state graph
(agent node <-> tools node) backed by Groq.

Run with FastAPI:
    uvicorn agent:app --reload

Or run directly:
    python agent.py "Create a sample employee CSV and import it into Excel and Google Sheets."
"""
import os
import sys
import json
import logging
import argparse
from typing import List, Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from tools.csv_tool import generate_employee_csv as _generate_csv
from tools.excel_tool import import_csv_to_excel as _import_excel
from tools.gsheets_tool import import_csv_to_google_sheets as _import_gsheets
from tools.ods_tool import import_csv_to_ods as _import_ods

# Import file manager
from utils.file_manager import file_manager

load_dotenv()

# ---------------------------------------------------------------------------
# Structured logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
)
logger = logging.getLogger("agent")

MAX_RETRIES = 2

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Employee Agent API",
    description="Autonomous AI Agent for employee data import using Groq",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AgentRequest(BaseModel):
    prompt: str
    thread: str = "default"

class AgentResponse(BaseModel):
    success: bool
    thread: str
    session: Optional[Dict[str, Any]] = None
    steps: List[Dict[str, Any]] = []
    summary: str = ""
    error: Optional[str] = None

# Store active tasks for async operations
active_tasks = {}

# ---------------------------------------------------------------------------
# Tools — LangChain @tool wrappers
# ---------------------------------------------------------------------------
@tool
def generate_employee_csv(filename: str, num_rows: int, columns: list = None) -> str:
    """Generates a CSV file with realistic sample data. 
    Use this for any sample data request (students, employees, products, etc.).
    You can specify custom columns like ["Student ID", "Name", "Grade", "Email", "GPA"].
    If no columns are specified, defaults to ["ID", "Name", "Department", "Email", "Salary"]."""
    return json.dumps(_with_retry(_generate_csv, filename=filename, num_rows=num_rows, columns=columns))

@tool
def import_csv_to_excel(csv_path: str, xlsx_path: str) -> str:
    """Opens Microsoft Excel or creates .xlsx with openpyxl."""
    return json.dumps(_with_retry(_import_excel, csv_path=csv_path, xlsx_path=xlsx_path))


@tool
def import_csv_to_google_sheets(csv_path: str, sheet_title: str) -> str:
    """Creates a new Google Sheet and imports CSV data."""
    return json.dumps(_with_retry(_import_gsheets, csv_path=csv_path, sheet_title=sheet_title))


@tool
def import_csv_to_ods(csv_path: str, ods_path: str) -> str:
    """Imports CSV data into OpenDocument Spreadsheet (.ods)."""
    return json.dumps(_with_retry(_import_ods, csv_path=csv_path, ods_path=ods_path))


TOOLS = [generate_employee_csv, import_csv_to_excel, import_csv_to_google_sheets, import_csv_to_ods]

SYSTEM_PROMPT = SystemMessage(content=(
    "You are an autonomous task-execution agent. Given the user's instruction, "
    "decide which tools to call and in what order to fully complete the task. "
    "IMPORTANT: When the user asks to generate any sample CSV (students, employees, products, etc.), "
    "always use the generate_employee_csv tool. "
    "If the user specifies custom columns (e.g., 'Student ID, Name, Grade, Email, GPA'), "
    "pass them as a list to the columns parameter. "
    "If no columns are specified, use the default: ['ID', 'Name', 'Department', 'Email', 'Salary']. "
    "The tool generates at least 20 rows. "
    "Always generate the CSV first, then import to Excel, then import to Google Sheets, "
    "unless the user's instruction implies otherwise. Use sensible defaults for filenames "
    "(sample.csv, sample.xlsx). After all tools are called, give a short summary of what succeeded/failed."
))


def _with_retry(fn, **kwargs) -> dict:
    """Executes a tool function with retries."""
    last = None
    for attempt in range(1, MAX_RETRIES + 2):
        logger.info(f"Executing '{fn.__name__}' (attempt {attempt}) with args={kwargs}")
        try:
            last = fn(**kwargs)
        except Exception as e:
            last = {"success": False, "error": str(e)}
        if last.get("success"):
            return last
        logger.warning(f"'{fn.__name__}' failed on attempt {attempt}: {last.get('error')}")
    return last


# ---------------------------------------------------------------------------
# LangGraph state graph
# ---------------------------------------------------------------------------
def build_graph():
    """Build the LangGraph with Groq as the only LLM provider."""
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY not set. Please set it in your .env file.")

    try:
        model = ChatGroq(
            model="openai/gpt-oss-20b",  # You can change this to any Groq model
            api_key=groq_api_key,
            temperature=0.3
        )
        logger.info("✅ Groq model initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Groq: {e}")
        raise

    model_with_tools = model.bind_tools(TOOLS)

    def agent_node(state: MessagesState):
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


def run_agent(user_prompt: str, thread_id: str = "default") -> dict:
    """
    Runs the agent graph on a user instruction.
    """
    # Ensure session exists for this thread
    file_manager.ensure_session_exists(thread_id)
    
    app_graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}
    messages = [SYSTEM_PROMPT, HumanMessage(content=user_prompt)]

    all_messages = list(messages)
    session_path = file_manager.current_session or "No session"
    print(f"\n🚀 Agent starting... (Session: {session_path})")

    for chunk in app_graph.stream({"messages": messages}, config=config, stream_mode="updates"):
        for node_name, state_update in chunk.items():
            new_msgs = state_update.get("messages", [])
            all_messages.extend(new_msgs)

            if node_name == "agent":
                for msg in new_msgs:
                    if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                        for tc in msg.tool_calls:
                            print(f"  🤔 Agent decided to call: {tc['name']}({tc['args']})")
                    elif isinstance(msg, AIMessage) and msg.content:
                        print(f"  💬 Agent: {msg.content[:120]}")

            elif node_name == "tools":
                for msg in new_msgs:
                    if isinstance(msg, ToolMessage):
                        try:
                            result = json.loads(msg.content)
                            status = "✅ succeeded" if result.get("success") else "❌ failed"
                        except (json.JSONDecodeError, TypeError):
                            status = "⚠️ returned non-JSON result"
                        print(f"  {status}: {msg.name}")

    print("🏁 Agent finished.\n")
    report = build_report(all_messages)
    
    # Add file session info to report
    report["session"] = file_manager.get_session_summary()
    
    return report


def build_report(messages) -> dict:
    """Walks the message history and extracts a per-step success/failure report."""
    steps = []
    pending_calls = {}

    for msg in messages:
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                pending_calls[tc["id"]] = {"tool": tc["name"], "args": tc["args"]}
        elif isinstance(msg, ToolMessage):
            call = pending_calls.get(msg.tool_call_id, {"tool": msg.name, "args": {}})
            try:
                result = json.loads(msg.content)
            except (json.JSONDecodeError, TypeError):
                result = {"success": False, "error": str(msg.content)}
            steps.append({"tool": call["tool"], "args": call["args"], "result": result})

    summary = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            summary = msg.content
            break

    return {"steps": steps, "summary": summary}


def print_report(report: dict):
    print("\n" + "=" * 60)
    print("AGENT EXECUTION REPORT")
    print("=" * 60)
    for i, step in enumerate(report["steps"], 1):
        status = "✅ SUCCESS" if step["result"].get("success") else "❌ FAILED"
        print(f"\nStep {i}: {step['tool']}  -->  {status}")
        print(f"  Args:   {json.dumps(step['args'])}")
        print(f"  Result: {json.dumps(step['result'])}")
    
    if "session" in report:
        print("\n" + "-" * 60)
        print("📁 SESSION FILES")
        print("-" * 60)
        session = report["session"]
        if session.get("active"):
            print(f"  Session: {session['session_path']}")
            print(f"  Files: {session['file_count']}")
            if session.get('file_types'):
                print(f"  Types: {', '.join([f'{k}: {v}' for k, v in session['file_types'].items()])}")
            print(f"  Total Size: {session['total_size_mb']} MB")
        else:
            print("  No active session")
    
    print("\n" + "-" * 60)
    print("Summary:", report["summary"])
    print("=" * 60)


# ---------------------------------------------------------------------------
# FastAPI Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "online",
        "message": "Employee Agent API is running with Groq",
        "version": "1.0.0",
        "provider": "groq"
    }


@app.post("/api/run", response_model=AgentResponse)
async def run_agent_endpoint(request: AgentRequest):
    """
    Run the agent with the given prompt and thread.
    """
    try:
        logger.info(f"Received request: thread={request.thread}, prompt={request.prompt[:50]}...")
        
        # Run the agent
        report = run_agent(request.prompt, thread_id=request.thread)
        
        # Check for errors
        steps = report.get("steps", [])
        all_success = all(step.get("result", {}).get("success", False) for step in steps)
        
        return AgentResponse(
            success=all_success,
            thread=request.thread,
            session=report.get("session"),
            steps=steps,
            summary=report.get("summary", "Task completed"),
            error=None if all_success else "Some steps failed"
        )
        
    except Exception as e:
        logger.error(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run/async")
async def run_agent_async(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Run the agent asynchronously - returns immediately with a task ID.
    """
    task_id = f"task_{int(time.time())}_{request.thread}"
    active_tasks[task_id] = {
        "status": "processing",
        "result": None,
        "thread": request.thread,
        "prompt": request.prompt
    }
    
    # Run in background
    def run_task():
        try:
            result = run_agent(request.prompt, thread_id=request.thread)
            active_tasks[task_id]["status"] = "completed"
            active_tasks[task_id]["result"] = result
        except Exception as e:
            active_tasks[task_id]["status"] = "failed"
            active_tasks[task_id]["error"] = str(e)
    
    background_tasks.add_task(run_task)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Task started"
    }


@app.get("/api/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of an async task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return active_tasks[task_id]


@app.get("/api/files")
async def list_files(thread: Optional[str] = None):
    """
    List all files in the workspace, optionally filtered by thread.
    """
    try:
        if thread:
            file_manager.ensure_session_exists(thread)
            files = file_manager.list_files(recursive=True)
        else:
            files = list(file_manager.base_dir.rglob("*"))
            files = [f for f in files if f.is_file()]
        
        file_list = []
        for f in files:
            file_list.append({
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "created": f.stat().st_ctime,
                "modified": f.stat().st_mtime
            })
        
        return {"files": file_list}
        
    except Exception as e:
        logger.error(f"❌ Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/download/{filename:path}")
async def download_file(filename: str, thread: Optional[str] = None):
    """
    Download a file from the workspace.
    """
    try:
        if thread:
            file_manager.ensure_session_exists(thread)
            file_path = file_manager.get_file_path(filename)
        else:
            file_path = None
            for f in file_manager.base_dir.rglob(filename):
                if f.is_file():
                    file_path = f
                    break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        logger.error(f"❌ Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/files/cleanup")
async def cleanup_files(days: int = 7):
    """
    Clean up old workspace sessions.
    """
    try:
        removed = file_manager.cleanup_old_sessions(keep_days=days)
        return {
            "success": True,
            "removed": removed,
            "message": f"Removed {removed} old sessions"
        }
    except Exception as e:
        logger.error(f"❌ Error cleaning up: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/threads")
async def list_threads():
    """
    List all active threads (sessions).
    """
    try:
        sessions = []
        for session_dir in file_manager.base_dir.iterdir():
            if session_dir.is_dir() and "_" in session_dir.name:
                parts = session_dir.name.split("_")
                if len(parts) >= 2:
                    thread_id = "_".join(parts[:-1])
                    sessions.append({
                        "thread": thread_id,
                        "session": session_dir.name,
                        "path": str(session_dir),
                        "created": session_dir.stat().st_ctime,
                        "files": len(list(session_dir.rglob("*")))
                    })
        
        return {"threads": sessions}
        
    except Exception as e:
        logger.error(f"❌ Error listing threads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "provider": "groq"
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous employee-data import agent")
    parser.add_argument("prompt", nargs="*", help="Natural language instruction")
    parser.add_argument("--thread", default="default", help="Conversation thread id")
    parser.add_argument("--server", action="store_true", help="Run as FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Port for FastAPI server")
    parser.add_argument("--host", default="0.0.0.0", help="Host for FastAPI server")
    args = parser.parse_args()

    if args.server or (not args.prompt and not args.thread):
        # Run as server
        logger.info("🚀 Starting FastAPI server...")
        logger.info(f"📍 Server will run at: http://{args.host}:{args.port}")
        logger.info("📚 API docs available at: /docs")
        uvicorn.run(
            "agent:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level="info"
        )
    else:
        # Run as CLI
        prompt = " ".join(args.prompt) or "Create a sample employee CSV and import it into Excel and Google Sheets."
        logger.info(f"Received instruction: {prompt}")
        report = run_agent(prompt, thread_id=args.thread)
        print_report(report)