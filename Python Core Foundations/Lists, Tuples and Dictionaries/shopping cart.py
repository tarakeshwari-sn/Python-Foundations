cart={}
def add_items():
    num_items = int(input("How many items would you like to add to your shopping cart? "))
    for i in range(num_items):
        item = input(f"Enter the name of item {i+1}: ")
        quantity = int(input(f"Enter the quantity of {item}: "))
        cart[item]= quantity
    print("Items added to your cart.")

def view_cart():
    if not cart:
        print("Your shopping cart is empty.")
    else:
        print("Items in your shopping cart:")
        for item, quantity in cart.items():
            print(f"{item}: {quantity}")

def update_cart():
    item = input("Enter the name of the item you want to update: ")
    if item in cart:
        quantity = int(input(f"Enter the new quantity for {item}: "))
        cart[item] = quantity
        print(f"{item} updated to quantity {quantity}.")
    else:
        print(f"{item} is not in your cart.")

def delete_item():
    item = input("Enter the name of the item you want to delete: ")
    if item in cart:
        del cart[item]
        print(f"{item} has been removed from your cart.")
    else:
        print(f"{item} is not in your cart.")

while True:
    print("\nShopping Cart Menu: \n Press the corresponding number to choose an option:")
    print("Add Items (1)")
    print("View Cart (2)")
    print("Update Cart (3)")    
    print("Delete Item (4)")
    print("Exit (5) \n")

    choice = input("Your choice: ")
    
    if choice == '1':
        add_items()
    elif choice == '2':
        view_cart()
    elif choice == '3':
        update_cart()
    elif choice == '4':
        delete_item()
    elif choice == '5':
        print("Exiting the shopping cart.")
        break
    else:
        print("Invalid choice. Please try again.")