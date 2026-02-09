import json
from attendance_tracker import AttendanceTracker

class Employee:
    def __init__(self,**kwargs):
        self.emp_id=kwargs.get("emp_id")
        self.emp_name=kwargs.get("emp_name")
        self.emp_dob=kwargs.get("emp_dob")
        self.emp_role=kwargs.get("emp_role")
        self.emp_salary=kwargs.get("emp_salary", 0)
        self.username=kwargs.get("username")
        self.password=kwargs.get("password")
        self.leaves=kwargs.get("leaves", [])

    def view_profile(self):
        print(f"\nEmployee ID: {self.emp_id}")
        print(f"Name: {self.emp_name}")
        print(f"DOB: {self.emp_dob}")
        print(f"Role: {self.emp_role}")
        print(f"Salary: {self.emp_salary}")

    def edit_profile(self, data):
        new_name=input("Enter new name (leave blank to keep same): ")
        new_dob=input("Enter new DOB (leave blank to keep same): ")
        for emp in data["employees"]:
            if emp["emp_id"]==self.emp_id:
                if new_name:
                    emp["emp_name"]=self.emp_name = new_name
                if new_dob:
                    emp["emp_dob"]=self.emp_dob = new_dob
                print("Profile updated successfully")

    def view_attendance(self,tracker):
        report=tracker.get_employee_report(self.emp_id)
        print(f"\nAttendance for Employee ID {self.emp_id}:")
        for date,status in report.items():
            print(date,":",status)

    def request_leave(self,data):
        date=input("Leave date (ddmmyyyy): ")
        reason=input("Reason: ")
        for emp in data["employees"]:
            if emp["emp_id"]==self.emp_id:
                emp.setdefault("leaves", []).append({"date":date,"reason":reason,"status":"Pending"})
                print("Leave requested")

class Manager:
    def __init__(self, tracker, data):
        self.tracker = tracker
        self.data = data

    def mark_attendance(self):
        date=input("Date (ddmmyyyy): ")
        ids=[int(i.strip()) for i in input("Present IDs (comma separated): ").split(",")]
        self.tracker.mark_attendance(date, ids)
        print("Attendance marked")

    def approve_leave(self):
        emp_id = int(input("Employee ID to process leave: "))
        for emp in self.data["employees"]:
            if emp["emp_id"] == emp_id:
                for leave in emp.get("leaves", []):
                    if leave["status"] == "Pending":
                        print(leave)
                        decision = input("Approve? (y/n): ")
                        if decision.lower() == "y":
                            leave["status"] = "Approved"
                            self.tracker.mark_absent(leave["date"], emp_id)
                        else:
                            leave["status"] = "Rejected"
                print("Leave processed")
                return
        print("Employee not found")

    def promote_employee(self):
        emp_id=int(input("Employee ID to promote: "))
        new_role=input("New Role: ")
        for emp in self.data["employees"]:
            if emp["emp_id"]==emp_id:
                emp["emp_role"]=new_role
                print("Role updated successfully")
                return
        print("Employee not found")

    def view_attendance(self):
        emp_id=input("Enter Employee ID (leave blank for all): ")
        if emp_id:
            emp_id=int(emp_id)
            report=self.tracker.get_employee_report(emp_id)
            print(emp_id, report)
        else:
            for emp in self.data["employees"]:
                print(emp["emp_id"], self.tracker.get_employee_report(emp["emp_id"]))

class HR:
    def __init__(self, data, tracker):
        self.data=data
        self.tracker=tracker

    def add_employee(self):
        self.data["employees"].append({
            "emp_id":int(input("ID: ")),"emp_name":input("Name: "),"emp_dob":input("DOB: "),
            "emp_role":input("Role: "),"emp_salary":float(input("Salary: ")),
            "username":input("Username: "),"password":input("Password: "),"leaves": []})
        print("Employee added")

    def delete_employee(self):
        emp_id = int(input("Employee ID to delete: "))
        self.data["employees"]=[e for e in self.data["employees"] if e["emp_id"] != emp_id]
        print("Employee deleted")

    def upgrade_salary(self):
        inc = float(input("Increment amount: "))
        for emp in self.data["employees"]:
            emp["emp_salary"] += inc
        print("Salary updated for all employees")

    def view_attendance(self):
        for emp in self.data["employees"]:
            print(emp["emp_id"], self.tracker.get_employee_report(emp["emp_id"]))

    def mark_holiday(self):
        date=input("Holiday date (ddmmyyyy): ")
        self.tracker.mark_holiday(date)
        print("Holiday marked")

class EmployeeManagementSystem:
    def __init__(self, data_file):
        self.data_file = data_file
        self.load_data()
        self.attendance_tracker = AttendanceTracker(self)

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.data=json.load(f)
        except FileNotFoundError:
            self.data = {"employees": [], "attendance": {}}

    def save_data(self):
        self.data["attendance"] = {
            d: {"present": list(v["present"]),"absent": list(v.get("absent", [])),"holiday": v["holiday"]}
            for d, v in self.attendance_tracker.attendance_record.items()}
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def login(self):
        username=input("Username: ")
        password=input("Password: ")
        user=next((e for e in self.data["employees"] if e["username"] == username and e["password"] == password), None)
        if not user:
            print("Invalid credentials")
            return None
        print(f"Login successful! Welcome {user['emp_name']} ({user['emp_role']})")
        return user

    def emp_menu(self, user_data):
        employee=Employee(**user_data)
        while True:
            print("\n1.View Profile\n2.Edit Profile\n3.Request Leave\n4.View Attendance\n0.Exit")
            c=int(input("Choice: "))
            if c==1:
                employee.view_profile()
            elif c==2:
                employee.edit_profile(self.data)
                self.save_data()
            elif c==3:
                employee.request_leave(self.data)
                self.save_data()
            elif c==4:
                employee.view_attendance(self.attendance_tracker)
            elif c==0:
                break

    def manager_menu(self):
        manager=Manager(self.attendance_tracker, self.data)
        while True:
            print("\n1.Mark Attendance\n2.Approve Leave Requests\n3.Promote Employee\n4.View Employee Attendance\n0.Exit")
            c=int(input("Choice: "))
            if c==1:
                manager.mark_attendance()
                self.save_data()
            elif c==2:
                manager.approve_leave()
                self.save_data()
            elif c==3:
                manager.promote_employee()
                self.save_data()
            elif c==4:
                manager.view_attendance()
            elif c==0:
                break

    def hr_menu(self):
        hr=HR(self.data, self.attendance_tracker)
        while True:
            print("\n1.Add Employee\n2.Delete Employee\n3.Upgrade Salary\n4.View Employee Attendance\n5.Mark Holiday\n0.Exit")
            c=int(input("Choice: "))
            if c ==1:
                hr.add_employee()
                self.save_data()
            elif c==2:
                hr.delete_employee()
                self.save_data()
            elif c==3:
                hr.upgrade_salary()
                self.save_data()
            elif c==4:
                hr.view_attendance()
            elif c==5:
                hr.mark_holiday()
                self.save_data()
            elif c == 0:
                break
            
if __name__ == "__main__":
    ems=EmployeeManagementSystem("Advanced OOPS and Design Thinking/employees.json")
    while True:
        print("\nLogin")
        user = ems.login()
        if not user:
            continue

        role=user["emp_role"].lower()
        if role=="employee":
            ems.emp_menu(user)
        elif role=="manager":
            ems.manager_menu()
        elif role=="hr":
            ems.hr_menu()