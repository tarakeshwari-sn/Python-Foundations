print("Student Marks Manager")

name=str(input("Enter student name: "))
math=int(input("Enter marks in Math: "))
sci=int(input("Enter marks in Science: "))
eng=int(input("Enter marks in English: "))

avg=(math+sci+eng)/3

if avg<35:
    result="Fail"

elif avg<50:
    result="C"

elif avg<75:
    result="B"

else:
    result="A"
    
print("\n Grade for the student",name,"is",result)
