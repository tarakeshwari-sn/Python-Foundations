import json

file_name="bank_details.json"

class User:
    def __init__(self,acc_num,name,pin,balance=0,status=True):
        self.acc_num=acc_num
        self.name=name
        self.pin=pin
        self.status=True
        self.balance=balance

    def to_dict(self):
        return {
            "acc_num": self.acc_num,"name": self.name,
            "pin": self.pin,"balance": self.balance,
            "status": self.status}

    @staticmethod
    def from_dict(data):
        return User(data["acc_num"],data["name"],data["pin"],
                    data["balance"],data["status"])
    
    @staticmethod
    def load_users():
        global users
        try:
            with open(file_name, "r") as f:
                raw = json.load(f)
                users = {int(acc): User.from_dict(u) for acc, u in raw.items()}
        except FileNotFoundError:
            users = {}
    
    @staticmethod
    def save_users():
        with open(file_name, "w") as f:
            json.dump({acc: user.to_dict() for acc, user in users.items()},f,indent=4)
    
    def deposit(self,amount, pin):
        if self.status and self.pin==pin:
            if amount>0:
                self.balance+=amount
                print(f"Deposited ₹{amount}. New Balance: ₹{self.balance}")
                User.save_users()
            else:
                print("Deposit amount must be positive.")
        else:
            print("Account inactive or wrong PIN.")

    def withdraw(self,amount,pin):
        if self.status and self.pin==pin:
            if 0<amount<=self.balance:
                self.balance-=amount
                print(f"Withdrawn ₹{amount}. New Balance: ₹{self.balance}")
                User.save_users()
            else:
                print("Insufficient balance.")
        else:
            print("Account inactive or wrong PIN.")

    def display(self,pin):
        if self.status and self.pin==pin:
            print(f"Account Number : {self.acc_num}")
            print(f"Name           : {self.name}")
            print(f"Balance        : ₹{self.balance}")
            print(f"Status         : {'Active' if self.status else 'Closed'}")
        else:
            print("Account inactive or wrong PIN.")

    def update_pin(self,old_pin,new_pin):
        if self.status and self.pin == old_pin:
            self.pin=new_pin
            print("PIN updated.")
            User.save_users()
        else:
            print("Wrong PIN or inactive account.")

    def close_acc(self,pin):
        if self.status and self.pin==pin:
            self.status=False
            print("Account closed.")
            User.save_users()
        else:
            print("Wrong PIN or account already closed.")

class Manager:
    def __init__(self,name,mid):
        self.name=name
        self.mid=mid

    def create_account(self,acc_num,name,pin,balance=0):
        if acc_num not in users:
            users[acc_num]=User(acc_num, name, pin, balance)
            print("Account created.")
            User.save_users()
        else:
            print("Account already exists.")

    def view_user(self,acc_num):
        if acc_num in users:
            user=users[acc_num]
            print("Account number: ",acc,"| User name : ",user.name,"| Balance: ",user.balance,"| Account Status: ",user.status)
        else:
            print("User not found.")

    def freeze_account(self,acc_num):
        if acc_num in users:
            users[acc_num].status=False
            print("Account frozen.")
            User.save_users()
        else:
            print("User not found.")

    def loan_eligibility(self,acc_num):
        if acc_num in users:
            if users[acc_num].balance >= 50000:
                print("Eligible for loan.")
            else:
                print("Not eligible for loan.")
        else:
            print("User not found.")

    def view_all_users(self):
        for acc, user in users.items():
            print(acc, user.name, user.balance, user.status)

users = {}
User.load_users()
print("Welcome to Banking System")

while True:
    role = int(input("\nUser(1)|Manager(2)|Exit(0): "))

    if role == 1:
        acc_num=int(input("Account Number: "))
        pin=int(input("PIN: "))

        if acc_num in users and users[acc_num].pin == pin:
            user=users[acc_num]
        else:
            print("Invalid credentials.")
            continue

        print("""
                1. Deposit
                2. Withdraw
                3. Display Balance
                4. Change PIN
                5. Close Account
                0. Exit
                """)
        while True:
            choice=int(input("Action: "))

            if choice==1:
                amt=float(input("Amount: "))
                user.deposit(amt, pin)

            elif choice==2:
                amt=float(input("Amount: "))
                user.withdraw(amt, pin)

            elif choice==3:
                user.display(pin)

            elif choice== 4:
                new_pin = int(input("New PIN: "))
                user.update_pin(pin, new_pin)
                pin = new_pin

            elif choice==5:
                user.close_acc(pin)
                break

            elif choice==0:
                break

            else:
                print("Invalid option.")

    elif role==2:
        name = input("Manager Name: ")
        mid = int(input("Manager ID: "))
        manager = Manager(name, mid)

        print("""
            1. Create Account
            2. View User
            3. Freeze Account
            4. Check Loan Eligibility
            5. View All Users
            0. Exit
            """)

        while True:
            choice=int(input("Action: "))

            if choice == 1:
                acc=int(input("Account Number: "))
                uname=input("User Name: ")
                pin=int(input("PIN: "))
                bal=float(input("Initial Balance: "))
                manager.create_account(acc, uname, pin, bal)

            elif choice==2:
                acc=int(input("Account Number: "))
                manager.view_user(acc)

            elif choice==3:
                acc = int(input("Account Number: "))
                manager.freeze_account(acc)

            elif choice==4:
                acc = int(input("Account Number: "))
                manager.loan_eligibility(acc)

            elif choice==5:
                manager.view_all_users()

            elif choice==0:
                break

            else:
                print("Invalid option.")

    elif role == 0:
        print("Thank you for using the banking system.")
        break

    else:
        print("Invalid role.")