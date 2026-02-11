import json,os

base_dir=os.path.dirname(os.path.abspath(__file__))
data_dir=os.path.join(base_dir,"data")
reports_dir=os.path.join(base_dir,"reports")
os.makedirs(data_dir,exist_ok=True)
os.makedirs(reports_dir,exist_ok=True)

file=os.path.join(data_dir,"attendance.json")

class AttendanceTracker:
    def __init__(self):
        self.attendance=self._load()

    def _load(self):
        if not os.path.exists(file):
            return {}
        with open(file,"r") as f:
            data=json.load(f)
        for d in data:
            data[d]["present"]=set(data[d]["present"])
            data[d]["absent"]=set(data[d]["absent"])
        return data

    def _save(self):
        data={}
        for d, r in self.attendance.items():
            data[d] = {"present": list(r["present"]),"absent": list(r["absent"]),"holiday": r["holiday"]}
        with open(file,"w") as f:
            json.dump(data,f,indent=4)

    def mark_attendance(self,date,all_ids,present_ids):
        self.attendance[date]={"present": set(present_ids),"absent":set(all_ids)-set(present_ids),"holiday":False}
        self._save()

    def mark_holiday(self,date):
        self.attendance[date]={"present": set(),"absent": set(),"holiday": True}
        self._save()

    def get_student_report(self,student_id):
        report={}
        for d, r in sorted(self.attendance.items()):
            if r["holiday"]:
                report[d]="Holiday"
            elif student_id in r["present"]:
                report[d]="Present"
            elif student_id in r["absent"]:
                report[d]="Absent"
            else:
                report[d]="Not Marked"
        return report
