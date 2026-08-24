"""
Streamlit frontend for the autonomous employee-data import agent.

This is a thin UI layer only — all agent logic (LangGraph graph, tools,
retries, logging) lives in agent.py and is untouched/reused as-is here.

Run:
    streamlit run app.py
"""
import json
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent import build_graph, SYSTEM_PROMPT, build_report

st.set_page_config(page_title="Employee Data Agent", page_icon="🤖", layout="centered")

st.title("🤖 Autonomous Employee-Data Import Agent")
st.caption(
    "Give it a plain-English instruction. It will decide which tools to call "
    "(CSV → Excel → Google Sheets → ODS) and run them autonomously."
)

with st.sidebar:
    st.subheader("Session")
    thread_id = st.text_input(
        "Thread ID (memory)",
        value="streamlit-session",
        help="Reuse the same thread ID across runs to give the agent memory of earlier turns.",
    )
    st.markdown("---")
    st.markdown(
        "**Tools available to the agent**\n"
        "- `generate_employee_csv`\n"
        "- `import_csv_to_excel`\n"
        "- `import_csv_to_google_sheets`\n"
        "- `import_csv_to_ods`"
    )

prompt = st.text_area(
    "Instruction",
    value="Create a sample employee CSV and import it into Excel and Google Sheets.",
    height=80,
)

run_clicked = st.button("Run agent", type="primary")

if run_clicked:
    if not prompt.strip():
        st.warning("Please enter an instruction first.")
        st.stop()

    try:
        app = build_graph()
    except RuntimeError as e:
        st.error(f"Setup issue: {e}")
        st.stop()

    config = {"configurable": {"thread_id": thread_id}}
    messages = [SYSTEM_PROMPT, HumanMessage(content=prompt)]
    all_messages = list(messages)

    st.markdown("### Live progress")
    progress_container = st.container()

    try:
        for chunk in app.stream({"messages": messages}, config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                new_msgs = state_update.get("messages", [])
                all_messages.extend(new_msgs)

                if node_name == "agent":
                    for msg in new_msgs:
                        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                            for tc in msg.tool_calls:
                                progress_container.info(f"🤔 Agent decided to call **{tc['name']}**")
                        elif isinstance(msg, AIMessage) and msg.content:
                            progress_container.write(f"💬 {msg.content}")

                elif node_name == "tools":
                    for msg in new_msgs:
                        if isinstance(msg, ToolMessage):
                            try:
                                result = json.loads(msg.content)
                                ok = result.get("success")
                            except (json.JSONDecodeError, TypeError):
                                ok = None
                            if ok:
                                progress_container.success(f"✅ {msg.name} succeeded")
                            elif ok is False:
                                progress_container.error(f"❌ {msg.name} failed: {result.get('error')}")
                            else:
                                progress_container.warning(f"⚠️ {msg.name} returned an unexpected result")

    except Exception as e:
        st.error(f"Agent run failed: {e}")
        st.stop()

    report = build_report(all_messages)

    st.markdown("### Final report")
    if report["steps"]:
        st.table([
            {
                "Step": i + 1,
                "Tool": s["tool"],
                "Status": "✅ Success" if s["result"].get("success") else "❌ Failed",
                "Details": s["result"].get("error") or s["result"].get("path") or s["result"].get("spreadsheet_url") or "",
            }
            for i, s in enumerate(report["steps"])
        ])
    else:
        st.info("No tool calls were made.")

    st.markdown("### Summary")
    st.write(report["summary"] or "_No summary returned._")

    # Offer download / links for anything the agent produced
    for step in report["steps"]:
        result = step["result"]
        if not result.get("success"):
            continue
        if step["tool"] in ("generate_employee_csv", "import_csv_to_excel", "import_csv_to_ods") and result.get("path"):
            path = result["path"]
            try:
                with open(path, "rb") as f:
                    st.download_button(f"⬇️ Download {path.split('/')[-1]}", f, file_name=path.split("/")[-1])
            except FileNotFoundError:
                pass
        if step["tool"] == "import_csv_to_google_sheets" and result.get("spreadsheet_url"):
            st.markdown(f"📊 [Open Google Sheet]({result['spreadsheet_url']})")
