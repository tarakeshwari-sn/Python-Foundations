from datetime import datetime

def is_weekend(date_str):
    date_obj = datetime.strptime(date_str, "%d%m%Y")
    return date_obj.weekday() >= 5   #Saturday,Sunday

class AttendanceTracker:
    def __init__(self):
        self.attendance_record = {}   #{date: {"present": set(), "holiday": bool}}
        self.students = {}            #{student_id: student_name}

class Student:
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def view_attendance(self, tracker):
        teacher = Teacher("System", "SYS")
        return teacher.student_report(tracker, self)

class Teacher:
    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def enter_student(self, tracker, sid, sname):
        tracker.students[sid] = sname

    def mark_attendance(self, tracker, date, present_student_ids):
        if is_weekend(date) or (tracker.attendance_record[date]["holiday"]==True):
            print("Cannot mark attendance on holidays.")
            return

        valid_ids = set(tracker.students.keys())
        present_ids = set(present_student_ids) & valid_ids

        tracker.attendance_record[date] = {"present": present_ids,"holiday": False}

    def update_attendance(self, tracker, date, updated_present_ids):
        if date not in tracker.attendance_record:
            print("No attendance record found for this date.")
            return

        if tracker.attendance_record[date]["holiday"] or is_weekend(date):
            print("Cannot update attendance for holiday/weekend.")
            return

        valid_ids = set(tracker.students.keys())
        tracker.attendance_record[date]["present"] = set(updated_present_ids) & valid_ids
        print("Attendance updated successfully.")

    def mark_holiday(self, tracker, date):
        if is_weekend(date):
            print("Weekends are already holidays.")
            return

        tracker.attendance_record[date] = {"present": set(),"holiday": True}

    def working_days(self, tracker):
        return sum(1 for date, info in tracker.attendance_record.items() if not is_weekend(date) and not info["holiday"])

    def student_report(self, tracker, student):
        total_working_days = 0
        present_days = 0
        day_wise = {}

        for date, info in tracker.attendance_record.items():
            if is_weekend(date) or info["holiday"]:
                continue
            total_working_days += 1
            if student.user_id in info["present"]:
                present_days += 1
                day_wise[date] = "Present"
            else:
                day_wise[date] = "Absent"

        percentage = (present_days / total_working_days * 100) if total_working_days else 0

        return {
            "Student Name": student.name,
            "Student ID": student.user_id,
            "Total Working Days": total_working_days,
            "Days Present": present_days,
            "Attendance %": round(percentage, 2),
            "Day-wise Attendance": day_wise}

tracker = AttendanceTracker()
print("\nAttendance Tracker")

while True:
    print("\n1. Teacher\n2. Student\n3. Exit")
    role = input("Select your role: ")

    if role == '1':
        teacher = Teacher(input("Enter Teacher Name: "), input("Enter Teacher ID: "))

        while True:
            print("""
            1. Create Students
            2. Mark Attendance
            3. View Student Attendance
            4. Mark Holiday
            5. Update Attendance
            6. View Total Working Days
            7. Logout """)
            choice = input("Choose an option: ")

            if choice == '1':
                num = int(input("Number of students: "))
                for _ in range(num):
                    sname = input("Student Name: ")
                    sid = input("Student ID: ")
                    teacher.enter_student(tracker, sid, sname)
                    print(f"Student {sname} added.")

            elif choice == '2':
                date = input("Date (ddmmyyyy): ")
                ids = input("Present IDs (comma-separated): ")
                teacher.mark_attendance(tracker, date, ids.split(","))
                print("Attendance marked.")

            elif choice == '3':
                sid = input("Student ID: ")
                if sid in tracker.students:
                    student = Student(tracker.students[sid], sid)
                    report = teacher.student_report(tracker, student)
                    for i, j in report.items():
                        print(f"{i}: {j}")
                else:
                    print("Student not found.")

            elif choice == '4':
                teacher.mark_holiday(tracker, input("Holiday Date: "))
                print("Holiday marked.")

            elif choice == '5':
                date = input("Date to Update: ")
                ids = input("Updated Present IDs: ")
                teacher.update_attendance(tracker, date, ids.split(","))
                print("Attendance updated.")

            elif choice == '6':
                print("Total Working Days:", teacher.working_days(tracker))

            elif choice == '7':
                break

            else:
                print("Invalid choice.")

    elif role == '2':
        sid = input("Student ID: ")
        if sid in tracker.students:
            student = Student(tracker.students[sid], sid)
            report = student.view_attendance(tracker)
            for k, v in report.items():
                print(f"{k}: {v}")
        else:
            print("Student not found.")

    elif role == '3':
        print("Program Exited.")
        break

    else:
        print("Invalid role.")
