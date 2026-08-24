"""
FastAPI backend for the Employee-Data Pipeline web frontend.

Run:
    uvicorn server:app --reload --port 8000

Then open http://127.0.0.1:8000
"""
import json
import queue
import threading
import asyncio
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent import build_graph, SYSTEM_PROMPT, build_report
from utils.file_manager import file_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

# Define paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
WORKSPACE_DIR = BASE_DIR / "workspace"

# Ensure workspace directory exists
WORKSPACE_DIR.mkdir(exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="Employee Data Pipeline",
    description="Autonomous AI Agent for employee data import",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class RunRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    thread_id: str = "web-session"


def _sse(event: str, data: dict) -> str:
    """Formats one Server-Sent Event frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _run_agent_sync(prompt: str, thread_id: str, q: "queue.Queue[tuple[str, dict]]") -> None:
    """
    Runs the LangGraph agent to completion on a background thread.
    """
    try:
        logger.info(f"🚀 Starting agent with prompt: {prompt[:50]}...")
        graph = build_graph()
        logger.info("✅ Graph built successfully")
    except Exception as e:
        import traceback
        logger.error(f"❌ Failed to build graph: {e}\n{traceback.format_exc()}")
        q.put(("error", {"message": f"Failed to build graph: {str(e)}"}))
        q.put(("done", {}))
        return

    config = {"configurable": {"thread_id": thread_id}}
    messages = [SYSTEM_PROMPT, HumanMessage(content=prompt)]
    all_messages = list(messages)

    try:
        for chunk in graph.stream({"messages": messages}, config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                new_msgs = state_update.get("messages", [])
                all_messages.extend(new_msgs)

                if node_name == "agent":
                    for msg in new_msgs:
                        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                            for tc in msg.tool_calls:
                                logger.info(f"🤔 Tool call: {tc['name']}")
                                q.put(("tool_call", {"tool": tc["name"], "args": tc["args"]}))
                        elif isinstance(msg, AIMessage) and msg.content:
                            logger.info(f"💬 Agent: {msg.content[:100]}...")
                            q.put(("agent_message", {"content": msg.content}))

                elif node_name == "tools":
                    for msg in new_msgs:
                        if isinstance(msg, ToolMessage):
                            try:
                                result = json.loads(msg.content)
                            except (json.JSONDecodeError, TypeError):
                                result = {"success": False, "error": str(msg.content)}
                            logger.info(f"🔧 Tool result: {msg.name} -> {result.get('success', False)}")
                            q.put(("tool_result", {"tool": msg.name, "result": result}))
    except Exception as e:
        logger.exception("Agent run failed")
        q.put(("error", {"message": str(e)}))

    report = build_report(all_messages)
    q.put(("report", report))
    q.put(("done", {}))
    logger.info("🏁 Agent finished")


@app.post("/api/run")
async def run(req: RunRequest):
    """Kicks off one agent run and streams its progress as SSE."""
    logger.info(f"📨 Received request: thread={req.thread_id}, prompt={req.prompt[:50]}...")
    
    q: "queue.Queue[tuple[str, dict]]" = queue.Queue()
    thread = threading.Thread(
        target=_run_agent_sync, args=(req.prompt, req.thread_id, q), daemon=True
    )
    thread.start()

    async def event_stream():
        loop = asyncio.get_event_loop()
        while True:
            try:
                event, data = await loop.run_in_executor(None, q.get)
                yield _sse(event, data)
                if event == "done":
                    break
            except Exception as e:
                logger.error(f"❌ Event stream error: {e}")
                yield _sse("error", {"message": str(e)})
                break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        },
    )


@app.get("/api/download")
async def download(path: str):
    """
    Serves a file the agent produced for download.
    """
    try:
        # Get just the filename
        filename = Path(path).name
        logger.info(f"🔍 Searching for file: {filename}")
        
        # Find the file in workspace
        found_file = None
        for file_path in WORKSPACE_DIR.rglob(filename):
            if file_path.is_file():
                found_file = file_path
                break
        
        # Also check the root directory as fallback
        if not found_file:
            root_file = BASE_DIR / filename
            if root_file.exists():
                found_file = root_file
        
        if not found_file or not found_file.exists():
            logger.warning(f"❌ File not found: {filename}")
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
        
        logger.info(f"✅ Serving file: {found_file}")
        return FileResponse(
            path=str(found_file),
            filename=found_file.name,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files")
async def list_files():
    """
    List all files in the workspace.
    """
    try:
        files = []
        for file_path in WORKSPACE_DIR.rglob("*"):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path.relative_to(BASE_DIR)),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        return {"files": files}
    except Exception as e:
        logger.error(f"❌ Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "port": 8000,
        "workspace": str(WORKSPACE_DIR),
        "workspace_exists": WORKSPACE_DIR.exists()
    }


@app.get("/")
async def root():
    """Root endpoint - serves the frontend."""
    # Check if static directory exists
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(str(STATIC_DIR / "index.html"))
    else:
        return {
            "message": "Employee Data Pipeline API is running",
            "docs": "/docs",
            "status": "healthy"
        }


# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    logger.warning(f"⚠️ Static directory not found at: {STATIC_DIR}")
    # Create static directory if it doesn't exist
    STATIC_DIR.mkdir(exist_ok=True)
    logger.info(f"✅ Created static directory at: {STATIC_DIR}")


# Make sure app is exported
__all__ = ["app"]