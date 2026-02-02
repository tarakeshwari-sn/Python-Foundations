import json
import os

file_name = "students.json"

def load_students():
    if not os.path.exists(file_name):
        return []
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_students(students):
    with open(file_name, "w") as f:
        json.dump(students, f, indent=4)

class StudentNotFoundError(Exception):
    pass

def add_student():
    students = load_students()
    num = int(input("How many students to add? "))

    for i in range(num):
        sid = input("Enter ID: ")
        name = input("Enter Name: ")
        age = int(input("Enter Age: "))
        course = input("Enter Course: ")

        students.append({"id": sid,"name": name,"age": age,"course": course})
        print("\n Student added")
    save_students(students)

def view_students():
    students = load_students()
    if not students:
        print("No students found")
        return
    for s in students:
        print(f"ID: {s['id']}, "f"Name: {s['name']}, "f"Age: {s['age']}, "f"Course: {s['course']}")

def find_student():
    sid = input("Enter ID to search: ")
    students = load_students()

    for s in students:
        if s["id"] == sid:
            print(f"ID: {s['id']}, "f"Name: {s['name']}, " f"Age: {s['age']}, "f"Course: {s['course']}")
            return
    raise StudentNotFoundError("Student not found")

def delete_student():
    sid = input("Enter ID to delete: ")
    students = load_students()

    for s in students:
        if s["id"] == sid:
            students.remove(s)
            save_students(students)
            print("Student deleted")
            return
    raise StudentNotFoundError("Student not found")


def update_student():
    sid = input("Enter ID to update: ")
    students = load_students()

    for s in students:
        if s["id"] == sid:
            print("Enter new details (leave blank to keep current value):")
            new_name = input(f"Name [{s['name']}]: ") or s['name']
            new_age = input(f"Age [{s['age']}]: ") or s['age']
            new_course = input(f"Course [{s['course']}]: ") or s['course']

            s['name'] = new_name
            s['age'] = int(new_age)
            s['course'] = new_course

            save_students(students)
            print("Student updated")
            return

    raise StudentNotFoundError("Student not found")

print("Student Management System")

menu = {1: add_student,2: view_students,3: find_student,4: update_student,5: delete_student}

while True:
    print("\n1.Add  2.View  3.Search  4.Update  5.Delete  6.Exit")
    try:
        choice = int(input("Choice: "))
        if choice == 6:
            print("Program exited")
            break
        elif choice in menu:
            menu[choice]()
        else:
            print("Invalid choice")

    except ValueError:
        print("Please enter a valid number")

    except StudentNotFoundError as e:
        print(e)

    finally:
        print("Done")