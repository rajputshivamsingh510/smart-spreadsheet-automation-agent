"""
Unit tests for the agent's tools. External services (Excel COM, Google API)
are mocked so tests run anywhere without needing Windows/Excel/Google creds.
"""
import os
import sys
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.csv_tool import generate_employee_csv
from tools.excel_tool import import_csv_to_excel
from tools.gsheets_tool import import_csv_to_google_sheets
from tools.ods_tool import import_csv_to_ods


def test_generate_employee_csv_creates_at_least_20_rows():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "employees.csv")
        result = generate_employee_csv(path, num_rows=20)
        assert result["success"] is True
        assert result["rows"] == 20

        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["Employee ID", "Name", "Department", "Email", "Salary"]
        assert len(rows) - 1 == 20  # minus header


def test_generate_employee_csv_enforces_minimum_20_rows():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "employees.csv")
        result = generate_employee_csv(path, num_rows=5)
        assert result["rows"] == 20  # enforced minimum


def test_excel_import_missing_csv_fails_gracefully():
    result = import_csv_to_excel("nonexistent_file.csv", "out.xlsx")
    assert result["success"] is False
    assert "not found" in result["error"].lower()


def test_excel_import_falls_back_to_openpyxl_on_non_windows():
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "employees.csv")
        xlsx_path = os.path.join(tmp, "employees.xlsx")
        generate_employee_csv(csv_path, 20)

        with patch("platform.system", return_value="Linux"):
            result = import_csv_to_excel(csv_path, xlsx_path)

        assert result["success"] is True
        assert result["method"] == "openpyxl_fallback"
        assert Path(xlsx_path).exists()


def test_gsheets_import_missing_csv_fails_gracefully():
    result = import_csv_to_google_sheets("nonexistent_file.csv")
    assert result["success"] is False
    assert "not found" in result["error"].lower()


@patch("tools.gsheets_tool._get_credentials")
@patch("tools.gsheets_tool.build")
def test_gsheets_import_success_mocked(mock_build, mock_creds):
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "employees.csv")
        generate_employee_csv(csv_path, 20)

        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().create().execute.return_value = {"spreadsheetId": "abc123"}

        result = import_csv_to_google_sheets(csv_path, "Test Sheet")
        assert result["success"] is True
        assert result["spreadsheet_id"] == "abc123"
        assert "abc123" in result["spreadsheet_url"]


def test_ods_import_missing_csv_fails_gracefully():
    result = import_csv_to_ods("nonexistent_file.csv")
    assert result["success"] is False
    assert "not found" in result["error"].lower()


def test_ods_import_creates_real_file():
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "employees.csv")
        ods_path = os.path.join(tmp, "employees.ods")
        generate_employee_csv(csv_path, 20)

        result = import_csv_to_ods(csv_path, ods_path)
        assert result["success"] is True
        assert Path(ods_path).exists()
        assert Path(ods_path).stat().st_size > 0
