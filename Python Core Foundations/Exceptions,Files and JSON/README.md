# Student Management System

Console and file based Student Management System with JSON based storage and CSV report exporting.

## Roles and Operations: 
### Principle: 
1. add_student()
2. delete_student()
3. mark_holiday()
4. export_csv()

### Teacher:
1. mark_attendance()
2. enter_grades()

### Student:
1. view_profile()
2. view_attendance()
3. view_grades()

## Concepts Used: 
JSON load/dump - To get and storedata in JSON format.

File Handling - Used JSON and CSV files to store data and convert JSON to CSV format. 

Folder Structure - JSON files are stored separately under data folder and csv files are stored under reports directory.

try/except/finally and Custom exceptions -  Used for error handling.

## Storage:

In students.json, data is stored in following format:
```[
    {
        "id": "23",
        "name": "sara",
        "age": 12,
        "course": "Social"
    }
] 
```

In attendance.json, data is stored in the following format: (Value 23 is here is the student id.)
``` 
{
    "09-02-2026": {
        "present": [
            "23"
        ],
        "absent": [],
        "holiday": false
    }
}
```
In grades.json, data is stored in the following format: (Value 23 is here is the student id.)
```
{
    "23": {
        "Science": 45
    }
}
```