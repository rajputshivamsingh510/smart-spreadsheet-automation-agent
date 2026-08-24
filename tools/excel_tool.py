"""
Excel Import Tool
-----------------
Imports CSV data into Microsoft Excel or creates .xlsx using openpyxl.
"""
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any
import openpyxl
import csv

# Import file manager
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.file_manager import file_manager

logger = logging.getLogger(__name__)


def import_csv_to_excel(csv_path: str, xlsx_path: str = "employees.xlsx") -> Dict[str, Any]:
    """
    Import CSV data into Microsoft Excel or create .xlsx with openpyxl.
    
    Args:
        csv_path: Path to the CSV file
        xlsx_path: Path for the output Excel file
        
    Returns:
        Dictionary with success status, file path, and metadata
    """
    try:
        # Resolve paths using file manager
        csv_file = Path(csv_path)
        if not csv_file.is_absolute():
            csv_file = file_manager.get_file_path(csv_file.name, subdir="csv")
        
        if not csv_file.exists():
            return {
                "success": False,
                "error": f"CSV file not found: {csv_file}"
            }
        
        # Get Excel file path
        xlsx_file = Path(xlsx_path)
        if not xlsx_file.is_absolute():
            xlsx_file = file_manager.get_file_path(xlsx_file.name, subdir="excel")
        xlsx_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to open with Microsoft Excel first
        excel_opened = False
        try:
            # On Windows
            if os.name == 'nt':
                subprocess.Popen(['start', 'excel', str(csv_file)], shell=True)
                excel_opened = True
            # On macOS
            elif os.name == 'posix' and sys.platform == 'darwin':
                subprocess.Popen(['open', '-a', 'Microsoft Excel', str(csv_file)])
                excel_opened = True
            # On Linux with LibreOffice
            elif os.name == 'posix':
                subprocess.Popen(['libreoffice', '--calc', str(csv_file)])
                excel_opened = True
        except Exception as e:
            logger.warning(f"Could not open Excel directly: {e}")
        
        # Always create .xlsx with openpyxl as fallback
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Employee Data"
        
        # Read CSV and write to Excel
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            for row_idx, row in enumerate(csv_reader, 1):
                for col_idx, value in enumerate(row, 1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
        
        # Save Excel file
        wb.save(xlsx_file)
        
        # Register the file
        file_manager.register_file(str(xlsx_file), {
            "source_csv": str(csv_file),
            "excel_opened": excel_opened
        })
        
        logger.info(f"✅ Created Excel file: {xlsx_file}")
        
        return {
            "success": True,
            "filepath": str(xlsx_file),
            "filename": xlsx_file.name,
            "excel_opened": excel_opened,
            "message": f"Successfully created Excel file: {xlsx_file.name}"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to import to Excel: {e}")
        return {
            "success": False,
            "error": str(e)
        }