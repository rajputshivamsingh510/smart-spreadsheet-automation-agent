"""
CSV Generation Tool
-------------------
Generates realistic sample data and saves it as CSV.
Supports custom columns for any entity (students, employees, products, etc.)
"""
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from faker import Faker
import random

# Import file manager
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.file_manager import file_manager

logger = logging.getLogger(__name__)


def generate_employee_csv(
    filename: str, 
    num_rows: int = 20,
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate a CSV file with realistic sample data.
    Supports custom columns for any entity.
    
    Args:
        filename: Name of the CSV file to create
        num_rows: Number of records to generate (minimum 20)
        columns: List of column names (default: ["ID", "Name", "Department", "Email", "Salary"])
        
    Returns:
        Dictionary with success status, file path, and metadata
    """
    try:
        # Ensure at least 20 rows
        original_rows = num_rows
        if num_rows < 20:
            num_rows = 20
            logger.warning(f"⚠️ Requested {original_rows} rows, but minimum is 20. Generating 20 rows instead.")
        
        # Default columns if not provided
        if columns is None:
            columns = ["ID", "Name", "Department", "Email", "Salary"]
        
        # Get file path using file manager
        file_path = file_manager.get_file_path(filename, subdir="csv")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Faker
        fake = Faker()
        
        # Define departments (for Department column if present)
        departments = [
            "Engineering", "Marketing", "Sales", "Human Resources", 
            "Finance", "Operations", "IT", "Customer Support", 
            "R&D", "Product Management", "Design", "Legal"
        ]
        
        # Grades (for Grade column if present)
        grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
        
        # Generate data
        data = []
        for i in range(1, num_rows + 1):
            record = {}
            for col in columns:
                col_lower = col.lower().strip()
                
                if col_lower == "id" or col_lower == "student id" or col_lower == "employee id":
                    record[col] = f"{i:04d}"
                elif col_lower == "name":
                    record[col] = fake.name()
                elif col_lower == "department" or col_lower == "grade":
                    if "student" in filename.lower() or "grade" in col_lower:
                        record[col] = random.choice(grades)
                    else:
                        record[col] = random.choice(departments)
                elif col_lower == "email":
                    record[col] = fake.email()
                elif col_lower == "salary":
                    record[col] = round(random.uniform(40000, 150000), 2)
                elif col_lower == "gpa":
                    record[col] = round(random.uniform(2.0, 4.0), 2)
                elif col_lower == "age":
                    record[col] = random.randint(18, 65)
                elif col_lower == "phone" or col_lower == "phone number":
                    record[col] = fake.phone_number()
                elif col_lower == "address":
                    record[col] = fake.address().replace("\n", ", ")
                elif col_lower == "city":
                    record[col] = fake.city()
                elif col_lower == "country":
                    record[col] = fake.country()
                elif col_lower == "company":
                    record[col] = fake.company()
                elif col_lower == "job title":
                    record[col] = fake.job()
                elif col_lower == "date" or col_lower == "join date" or col_lower == "hire date":
                    record[col] = fake.date_between(start_date="-10y", end_date="today").isoformat()
                else:
                    # Default: generate appropriate data type
                    if "id" in col_lower:
                        record[col] = f"{i:04d}"
                    elif "name" in col_lower:
                        record[col] = fake.name()
                    elif "email" in col_lower:
                        record[col] = fake.email()
                    elif "date" in col_lower:
                        record[col] = fake.date_between(start_date="-10y", end_date="today").isoformat()
                    else:
                        record[col] = fake.word()
            data.append(record)
        
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for record in data:
                writer.writerow(record)
        
        # Register the file
        file_manager.register_file(str(file_path), {
            "num_rows": num_rows,
            "record_count": len(data),
            "requested_rows": original_rows,
            "columns": columns
        })
        
        logger.info(f"✅ Generated CSV with {len(data)} records: {file_path}")
        
        return {
            "success": True,
            "filepath": str(file_path),
            "filename": file_path.name,
            "rows": num_rows,
            "requested_rows": original_rows,
            "columns": columns,
            "message": f"Successfully generated {num_rows} records with columns: {', '.join(columns)}"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to generate CSV: {e}")
        return {
            "success": False,
            "error": str(e)
        }