"""
MCP Server — exposes the agent's tools over the Model Context Protocol so
any MCP-compatible client (Claude Desktop, Claude Code, other agents) can
call them directly, independent of this project's own LangGraph agent.

Run standalone:
    python mcp_server.py

Register in Claude Desktop's claude_desktop_config.json:
    {
      "mcpServers": {
        "employee-agent-tools": {
          "command": "python",
          "args": ["/absolute/path/to/mcp_server.py"]
        }
      }
    }
"""
import logging
from mcp.server.fastmcp import FastMCP

from tools.csv_tool import generate_employee_csv as _generate_csv
from tools.excel_tool import import_csv_to_excel as _import_excel
from tools.gsheets_tool import import_csv_to_google_sheets as _import_gsheets
from tools.ods_tool import import_csv_to_ods as _import_ods

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

mcp = FastMCP("employee-agent-tools")


@mcp.tool()
def generate_employee_csv(filename: str, num_rows: int = 20) -> dict:
    """Generates a CSV file with realistic sample employee data
    (Employee ID, Name, Department, Email, Salary). num_rows minimum is 20."""
    return _generate_csv(filename=filename, num_rows=num_rows)


@mcp.tool()
def import_csv_to_excel(csv_path: str, xlsx_path: str = "employees.xlsx") -> dict:
    """Opens Microsoft Excel (or falls back to openpyxl if Excel isn't installed),
    imports the CSV, and saves it as .xlsx."""
    return _import_excel(csv_path=csv_path, xlsx_path=xlsx_path)


@mcp.tool()
def import_csv_to_google_sheets(csv_path: str, sheet_title: str = "Employee Data") -> dict:
    """Creates a new Google Sheet via the Sheets API and imports the CSV data into it."""
    return _import_gsheets(csv_path=csv_path, sheet_title=sheet_title)


@mcp.tool()
def import_csv_to_ods(csv_path: str, ods_path: str = "employees.ods") -> dict:
    """Imports CSV data into a new OpenDocument Spreadsheet (.ods) file."""
    return _import_ods(csv_path=csv_path, ods_path=ods_path)


if __name__ == "__main__":
    logger.info("Starting MCP server 'employee-agent-tools' over stdio...")
    mcp.run()
