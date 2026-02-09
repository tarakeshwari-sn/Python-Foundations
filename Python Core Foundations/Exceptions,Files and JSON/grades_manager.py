import json
import os

base_dir=os.path.dirname(os.path.abspath(__file__))
data_dir=os.path.join(base_dir,"data")
reports_dir=os.path.join(base_dir,"reports")
os.makedirs(data_dir,exist_ok=True)
os.makedirs(reports_dir,exist_ok=True)

File=os.path.join(data_dir,"grades.json")

def load_grades():
    if not os.path.exists(File):
        return {}
    with open(File,"r") as f:
        return json.load(f)

def save_grades(data):
    with open(File,"w") as f:
        json.dump(data,f,indent=4)

def add_grade(student_id,subject,marks):
    data=load_grades()
    
    if student_id not in data:
        data[student_id]={}
    data[student_id][subject]=marks
    save_grades(data)

def get_student_grades(student_id):
    return load_grades().get(student_id, {})
