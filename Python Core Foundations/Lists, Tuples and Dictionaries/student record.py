student_details={}
marks=[]

def add_details():
    num_students=int(input("Enter number of students to add: "))
    for i in range(num_students):
        name=str(input("Enter student name: "))
        Grade=str(input("Enter student Grade: "))
        student_details[name]=Grade

        eng_marks=int(input(f"Enter English marks for {name}: "))
        math_marks=int(input(f"Enter Math marks for {name}: "))
        sci_marks=int(input(f"Enter Science marks for {name}: "))
        marks.append([eng_marks, math_marks, sci_marks])
        print("Student details added successfully.")

def update_details():
    name=str(input("Enter the name of the student to update: "))
    if name in student_details:
        new_grade=str(input("Enter new Grade: "))
        student_details[name]=new_grade

        index=list(student_details.keys()).index(name)
        eng_marks=int(input(f"Enter new English marks for {name}: "))
        math_marks=int(input(f"Enter new Math marks for {name}: "))
        sci_marks=int(input(f"Enter new Science marks for {name}: "))
        marks[index]=[eng_marks, math_marks, sci_marks]
        print("Student details updated successfully.")
    
    else:
        print("Student not found.")

def display_details():
    for i, (name, grade) in enumerate(student_details.items()):
        eng_marks, math_marks, sci_marks = marks[i]
        print(f"Name: {name}, Grade: {grade}, English Marks: {eng_marks}, Math Marks: {math_marks}, Science Marks: {sci_marks}")

def delete_details():
    name=str(input("Enter the name of the student to delete: "))
    if name in student_details:
        index=list(student_details.keys()).index(name)
        del student_details[name]
        del marks[index]
        print("Student details deleted successfully.")
    else:
        print("Student not found.")

print("Welcome to the Student Record Manager")
while True:
    print("\n Menu:")
    print("1. Add Student Details")
    print("2. Update Student Details")
    print("3. Display Student Details")
    print("4. Delete Student Details")
    print("5. Exit")

    choice=int(input("Enter your choice (1-5): "))

    if choice==1:
        add_details()
    elif choice==2:
        update_details()
    elif choice==3:
        display_details()
    elif choice==4:
        delete_details()
    elif choice==5:
        print("Exiting the Student Record Manager.")
        break
    else:
        print("Invalid choice. Please try again.")
