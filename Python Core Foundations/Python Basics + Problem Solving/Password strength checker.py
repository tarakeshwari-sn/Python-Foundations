print("Password Strength Checker")
password = str(input("Enter your password: "))
for i in password:
    if len(password) < 8:
        strength = "Weak"
    elif len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isupper() for char in password):
        strength = "Strong"
    else:
        strength = "Moderate"
print("The password is:", strength)