# Note: Real Excel COM automation only works on Windows, so inside this
# Linux container the Excel step automatically uses the openpyxl fallback.
# This is expected and reported honestly in the execution log.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "agent.py"]
CMD ["Create a sample employee CSV and import it into Excel and Google Sheets."]
