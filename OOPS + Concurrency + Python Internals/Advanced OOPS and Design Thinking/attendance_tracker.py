class AttendanceTracker:
    def __init__(self,ems):
        self.ems=ems  
        self.attendance_record = {}
        for date, record in self.ems.data.get("attendance", {}).items():
            self.attendance_record[date] = {"present": set(record.get("present", [])),
                "absent": set(record.get("absent", [])),"holiday": record.get("holiday", False)}

    def mark_attendance(self,date,present_ids):
        all_ids={emp["emp_id"] for emp in self.ems.data["employees"]}
        present_set = set(present_ids)
        absent_set = all_ids - present_set
        self.attendance_record[date] = {"present": present_set,"absent": absent_set,"holiday": False}
        print(f"Attendance recorded for {date}")

    def mark_absent(self, date, emp_id):
        if date not in self.attendance_record:
            # If date does not exist yet, mark all others present and this one absent
            all_ids = {emp["emp_id"] for emp in self.ems.data["employees"]}
            self.attendance_record[date] = {"present": all_ids - {emp_id},"absent": {emp_id},"holiday": False}
        else:
            self.attendance_record[date]["absent"].add(emp_id)
            self.attendance_record[date]["present"].discard(emp_id)
        print(f"Employee {emp_id} marked absent for {date}")

    def mark_holiday(self, date):
        all_ids = {emp["emp_id"] for emp in self.ems.data["employees"]}
        self.attendance_record[date] = {"present": set(),"absent": set(),"holiday": True}
        print(f"{date} marked as holiday")

    def get_employee_report(self, emp_id):
        report = {}
        for date, record in sorted(self.attendance_record.items()):
            if record["holiday"]:
                status="Holiday"
            elif emp_id in record["present"]:
                status="Present"
            elif emp_id in record["absent"]:
                status="Absent"
            else:
                status="Not marked"
            report[date]=status
        return report