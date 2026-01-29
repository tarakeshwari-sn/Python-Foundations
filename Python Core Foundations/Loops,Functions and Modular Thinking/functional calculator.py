add = lambda x, y: x + y
subtract = lambda x, y: x - y
multiply = lambda x, y: x * y
divide = lambda x, y: x / y if y != 0 else "Error: Division by zero"
modulus = lambda x, y: x % y if y != 0 else "Error: Modulus by zero"
power = lambda x, y: x ** y

operations = {'+': add,'-': subtract,'*': multiply,
    '/': divide,'%': modulus,'^': power}

print("Functional Calculator")

while True:
    choice = int(input("Enter 1 to calculate or 2 to exit: "))

    if choice == 2:
        print("Calculator exited.")
        break

    elif choice == 1:
        expr = int(input("Enter expression mode (1) or two-number mode (2): "))
        
        if expr == 1:
            expression = input("Enter expression (e.g., 3 + 5): ")
            try:
                result = eval(expression)
                print(f"Result: {result}")
            except Exception:
                print("Invalid expression")

        elif expr == 2:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))

            print("Select operation:")
            for op in operations:
                print(op)

            operation = input("Enter operation: ")
            if operation in operations:
                result = operations[operation](num1, num2)
                print(f"Result: {result}")
            else:
                print("Invalid operation")
        else:
            print("Invalid mode selection")
    else:
        print("Invalid choice. Please enter 1 or 2.")
