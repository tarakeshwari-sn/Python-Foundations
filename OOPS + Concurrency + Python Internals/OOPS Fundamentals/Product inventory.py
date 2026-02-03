import csv
import os

file = "inventory.csv"

class Product:
    def __init__(self,pid,name,price,qty):
        self.pid = str(pid)
        self.name = name.lower()
        self.price = float(price)
        self.qty = int(qty)

    def to_row(self):
        return [self.pid,self.name,self.price,self.qty]

class Inventory:
    def __init__(self,file_name=file):
        self.file_name = file_name
        self.init_file()

    def init_file(self):
        if not os.path.exists(self.file_name):
            with open(self.file_name, "w", newline="") as f:
                csv.writer(f).writerow(["product_id","name","price","quantity"])

    def read_all(self):
        with open(self.file_name, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            data = list(reader)
        return header, data

    def _write_all(self, rows):
        with open(self.file_name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "name", "price", "quantity"])
            writer.writerows(rows)

    def create_product(self, product):
        _, data = self.read_all()
        for row in data:
            if row[0] == product.pid:
                print("Product already exists.")
                return
        data.append(product.to_row())
        self._write_all(data)
        print("Product created.")

    def delete_product(self, pid):
        _, data = self.read_all()
        new_data = [row for row in data if row[0] != str(pid)]
        if len(new_data) == len(data):
            print("Product not found.")
            return
        self._write_all(new_data)
        print("Product deleted.")

    def update_product(self, pid, price=None):
        _, data = self.read_all()
        found = False
        for row in data:
            if row[0] == str(pid):
                if price is not None:
                    row[2] = float(price)
                found = True
        if not found:
            print("Product not found.")
            return
        self._write_all(data)
        print("Product updated.")

    def view_all(self):
        _, data = self.read_all()
        if not data:
            print("No products available.")
            return
        for row in data:
            print(row)

    def search(self, value):
        _, data = self.read_all()
        for row in data:
            if row[0] == str(value) or row[1] == value.lower():
                print(row)
                return
        print("Product not found.")

    def stock_in(self,pid,qty):
        self.change_stock(pid,qty)

    def stock_out(self, pid, qty):
        self.change_stock(pid, -qty)

    def change_stock(self, pid, delta):
        _, data = self.read_all()
        found = False

        for row in data:
            if row[0] == str(pid):
                new_qty = int(row[3]) + delta
                if new_qty < 0:
                    print("Insufficient stock.")
                    return
                row[3] = new_qty
                found = True

        if not found:
            print("Product not found.")
            return

        self._write_all(data)
        print("Stock updated.")

def menu():
    inv = Inventory()

    while True:
        print(""" Inventory Management
            1. Create Product
            2. Delete Product
            3. Update Product Price
            4. View All Products
            5. Search Product
            6. Stock IN
            7. Stock OUT
            0. Exit
            """)
        choice = input("Enter choice: ")

        if choice == "1":
            pid = input("Product ID: ")
            name = input("Name: ")
            price = float(input("Price: "))
            qty = int(input("Quantity: "))
            inv.create_product(Product(pid, name, price, qty))

        elif choice == "2":
            pid = input("Product ID: ")
            inv.delete_product(pid)

        elif choice == "3":
            pid = input("Product ID: ")
            price = float(input("New Price: "))
            inv.update_product(pid, price)

        elif choice == "4":
            inv.view_all()

        elif choice == "5":
            value = input("Product ID or Name: ")
            inv.search(value)

        elif choice == "6":
            pid = input("Product ID: ")
            qty = int(input("Quantity IN: "))
            inv.stock_in(pid, qty)

        elif choice == "7":
            pid = input("Product ID: ")
            qty = int(input("Quantity OUT: "))
            inv.stock_out(pid, qty)

        elif choice == "0":
            print("You've exited system.")
            break

        else:
            print("Invalid choice.")
menu()