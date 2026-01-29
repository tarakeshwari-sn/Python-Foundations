import re

person_email=str(input("Please enter your email address: "))
format = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

if re.match(format, person_email):
    print("Valid email address.")
else:
    print("Invalid email address.")