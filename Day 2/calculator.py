print("This is the Calculator. \n If you want to know an expression value , press 1 \n "
"If you want to type the expression yourself in parts, press 2")
choice = int(input("Enter your choice: "))

if choice == 1:
    expression = input("Enter the mathematical expression: ")
    try:
        result = eval(expression)
        print(f"The result of the expression '{expression}' is: {result}")
    except Exception as e:
        print(f"Error evaluating expression: {e}")

elif choice == 2:

    no_of_terms = int(input("Enter the number of terms in the expression: "))
    expression = ""

    for i in range(no_of_terms):
        term = input(f"Enter term {i+1} (number or operator): ")
        expression += term + " "
    try:
        result = eval(expression)
        print(f"The result of the expression '{expression.strip()}' is: {result}")
    except Exception as e:
        print(f"Error evaluating expression: {e}")

else:
    print("Invalid choice. Please restart the calculator and choose either 1 or 2.")