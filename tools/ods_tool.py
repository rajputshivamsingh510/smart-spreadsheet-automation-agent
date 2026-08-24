"""
ODS Import Tool
---------------
Imports CSV data into OpenDocument Spreadsheet (.ods) format.
"""
import csv
import logging
from pathlib import Path
from typing import Dict, Any
import pyexcel_ods3

# Import file manager
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.file_manager import file_manager

logger = logging.getLogger(__name__)


def import_csv_to_ods(csv_path: str, ods_path: str = "employees.ods") -> Dict[str, Any]:
    """
    Import CSV data into a new OpenDocument Spreadsheet (.ods) file.
    
    Args:
        csv_path: Path to the CSV file
        ods_path: Path for the output ODS file
        
    Returns:
        Dictionary with success status, file path, and metadata
    """
    try:
        # Resolve CSV path
        csv_file = Path(csv_path)
        if not csv_file.is_absolute():
            csv_file = file_manager.get_file_path(csv_file.name, subdir="csv")
        
        if not csv_file.exists():
            return {
                "success": False,
                "error": f"CSV file not found: {csv_file}"
            }
        
        # Get ODS file path
        ods_file = Path(ods_path)
        if not ods_file.is_absolute():
            ods_file = file_manager.get_file_path(ods_file.name, subdir="ods")
        ods_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Read CSV data
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            data = list(csv_reader)
        
        # Create ODS file
        data_dict = {
            "Employee Data": data
        }
        pyexcel_ods3.save_data(str(ods_file), data_dict)
        
        # Register the file
        file_manager.register_file(str(ods_file), {
            "source_csv": str(csv_file),
            "rows": len(data)
        })
        
        logger.info(f"✅ Created ODS file: {ods_file}")
        
        return {
            "success": True,
            "filepath": str(ods_file),
            "filename": ods_file.name,
            "rows": len(data),
            "message": f"Successfully created ODS file: {ods_file.name}"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to import to ODS: {e}")
        return {
            "success": False,
            "error": str(e)
        }