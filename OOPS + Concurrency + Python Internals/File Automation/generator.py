import os
import csv
import json
import random
import string
from openpyxl import Workbook

BASE_DIR = "incoming_files"
NUM_FILES = 10
ROWS_PER_CSV = 200_000     # ~5–8 MB CSV
LINES_PER_TXT = 150_000    # ~5–7 MB TXT
ENTRIES_PER_JSON = 80_000  # ~5–8 MB JSON
ROWS_PER_EXCEL = 200_000     # ~5–8 MB CSV

os.makedirs(BASE_DIR, exist_ok=True)

# ---------- EXCEL FILES ----------
for i in range(NUM_FILES):
    file_path = os.path.join(BASE_DIR, f"report_{i}.xlsx")

    wb = Workbook(write_only=True)
    ws = wb.create_sheet(title="Report")

    # Header
    ws.append(["RecordID", "Score"])

    # Data
    for j in range(ROWS_PER_EXCEL):
        ws.append([j, round(random.uniform(0, 100), 2)])

    wb.save(file_path)
"""
# ---------- CSV FILES ----------
for i in range(NUM_FILES):
    file_path = os.path.join(BASE_DIR, f"sales_{i}.csv")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["OrderID", "Amount"])
        for j in range(ROWS_PER_CSV):
            writer.writerow([j, round(random.uniform(10, 1000), 2)])

# ---------- JSON FILES ----------
for i in range(NUM_FILES):
    file_path = os.path.join(BASE_DIR, f"user_logs_{i}.json")
    data = []
    for j in range(ENTRIES_PER_JSON):
        data.append({
            "user_id": j,
            "action": random.choice(["login", "logout", "click", "purchase"]),
            "timestamp": j
        })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

# ---------- TXT FILES ----------
for i in range(NUM_FILES):
    file_path = os.path.join(BASE_DIR, f"error_dump_{i}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        for _ in range(LINES_PER_TXT):
            f.write(
                "".join(random.choices(string.ascii_letters + string.digits, k=80))
                + "\n"
            )
"""
print("Test files generated successfully!")
