import json,os,csv
from attendance_tracker import AttendanceTracker
from grades_manager import add_grade, get_student_grades,load_grades

base_dir=os.path.dirname(os.path.abspath(__file__))
data_dir=os.path.join(base_dir,"data")
reports_dir=os.path.join(base_dir,"reports")
os.makedirs(data_dir,exist_ok=True)
os.makedirs(reports_dir,exist_ok=True)

student_file=os.path.join(data_dir,"students.json")

class StudentNotFoundError(Exception):
    pass

class InvalidMarksError(Exception):
    pass

class FileOperationError(Exception):
    pass

def get_student_by_id(sid):
    for s in load_students():
        if s["id"]==sid:
            return s
    raise StudentNotFoundError(f"Student ID {sid} not found")

def load_students():
    if not os.path.exists(student_file):
        return []
    with open(student_file,"r") as f:
        return json.load(f)

def save_students(students):
    with open(student_file,"w") as f:
        json.dump(students,f,indent=4)

class Student:
    def __init__(self, sid):
        self.sid=sid
        self.attendance=AttendanceTracker()

    def view_profile(self):
        for s in load_students():
            if s["id"]==self.sid:
                print(s)
                return
        print("Student not found")

    def view_attendance(self):
        report=self.attendance.get_student_report(self.sid)
        for d,status in report.items():
            print(d,":",status)

    def view_grades(self):
        grades=get_student_grades(self.sid)
        if not grades:
            print("No grades found")
            return
        for sub, marks in grades.items():
            print(sub,":",marks)


class Teacher:
    def __init__(self):
        self.attendance=AttendanceTracker()

    def mark_attendance(self):
        date=input("Date (dd-mm-yyyy): ")
        students=load_students()
        all_ids=[s["id"] for s in students]

        present=input("Present IDs: ").split(",")
        self.attendance.mark_attendance(date,all_ids,present)
        print("Attendance marked")

    def enter_grades(self):
        try:
            sid = input("Student ID: ")
            subject = input("Subject: ")
            marks = int(input("Marks: "))

            if marks < 0 or marks > 100:
                raise InvalidMarksError("Marks must be between 0 and 100")
            get_student_by_id(sid)
            add_grade(sid,subject, marks)
            print("Grade added")

        except ValueError:
            print("Marks must be a number")

        except (StudentNotFoundError,InvalidMarksError) as e:
            print(e)
        finally:
            print("Grade operation finished")

class Principal:
    def __init__(self):
        self.attendance=AttendanceTracker()

    def add_student(self):
        students=load_students()
        students.append({"id": input("ID: "),"name": input("Name: "),"age": int(input("Age: ")),"course": input("Course: ")})
        save_students(students)
        print("Student added")

    def delete_student(self):
        sid=input("ID to delete: ")
        students=[s for s in load_students() if s["id"] != sid]
        save_students(students)
        print("Student deleted")

    def mark_holiday(self):
        date=input("Holiday date (dd-mm-yyyy): ")
        self.attendance.mark_holiday(date)
        print("Holiday marked")

def export_students_csv():
    students=load_students()
    path=os.path.join(reports_dir,"students.csv")
    with open(path,"w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["id", "name", "age", "course"])
        writer.writeheader()
        writer.writerows(students)

def export_grades_csv():
    grades=load_grades()
    path=os.path.join(reports_dir,"grades.csv")
    with open(path,"w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["Student ID", "Subject", "Marks"])
        for sid,subs in grades.items():
            for sub, marks in subs.items():
                writer.writerow([sid, sub, marks])

def main():
    print("Student Management System")
    print("Login: 1.Student  2.Teacher  3.Principal")
    role = input("Choice: ")

    if role=="1":
        s=Student(input("Student ID: "))
        while True:
            print("Hi Student")
            print("1.View Profile 2.View Attendance 3.View Grades 4.Exit")
            c=input("Choice: ")
            if c =="1": s.view_profile()
            elif c == "2": s.view_attendance()
            elif c == "3": s.view_grades()
            else: break

    elif role=="2":
        t=Teacher()
        while True:
            print("Hi Teacher")
            print("1.Mark Attendance 2.Enter Grades 3.Exit")
            c=input("Choice: ")
            if c=="1": t.mark_attendance()
            elif c=="2": t.enter_grades()
            else: break

    elif role=="3":
        p=Principal()
        while True:
            print("Hi Principle")
            print("1.Add Student 2.Delete Student 3.Mark Holiday 4.Export CSV 5.Exit")
            c=input("Choice: ")
            if c=="1": p.add_student()
            elif c=="2": p.delete_student()
            elif c=="3": p.mark_holiday()
            elif c=="4":
                export_students_csv()
                export_grades_csv()
                print("Exported to CSV")
            else: break

if __name__ == "__main__":
    main()
