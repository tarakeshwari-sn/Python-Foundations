# Employement Management System
Role based employee management portal for employee,managers and HR team.

## Roles and operations:
### HR
1. add_employee()
2. delete_employee()
3. upgrade_salary()
4. view_attendance()
5. mark_holiday()

### Manager
1. mark_attendance() - mark only present people using emp_id
2. approve_leave() - specific using emp_id or everyone's
3. promote_employee() - can only promote employee to manager
4. view_attendance() - specific using emp_id or everyone's

### Employee
1. view_profile()
2. edit_profile()
3. view_attendance()
4. request_leave()

## Concepts used: 
Polymorphism (Method overriding)  - view_attendance displays attendance based on access level of the user for privacy purposes.

Loose Coupling - Classes depend as little as possible on each other's internals (operations).

Composition vs Inheritance - Here EMS has a HAS-A relationship with AttendanceTracker rather than inheriting it.

## Storage:
Used JSON file for persistant storage in the following format.
```
{
    "employees": [
        {
            "emp_id": 101,
            "emp_name": "Alice Johnson",
            "emp_dob": "1995-06-12",
            "emp_role": "Manager",
            "emp_salary": 50000,
            "username": "alice",
            "password": "alice123",
            "leaves": [
                {
                    "date": "01022026",
                    "reason": "Medical",
                    "status": "Approved"
                },
                {
                    "date": "29032004",
                    "reason": "Sick leave",
                    "status": "Approved"
                }
            ]}
    ],
    "attendance": {
        "28032005": {
            "present": [],
            "absent": [],
            "holiday": false
        }
}}
```
