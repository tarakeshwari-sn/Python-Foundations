products={"Milk":50,"Bread":20,"Eggs":10,"Butter":40,"Cheese":60,"Apples":30,"Bananas":25}

def calculate_bill(shopping_cart):
    total=0
    for item in shopping_cart:
        if item in products:
            total+=products[item]
    return total

print("Welcome to the Billing System")
print("Available products are " )
for item, price in products.items():
    print(item)

product_no=int(input("Enter the number of products you want to buy: "))
shopping_cart=[]

for i in range(product_no):
    product_name=input(f"Enter the name of product {i+1}: ")

    if product_name not in products:
        print(f"Sorry, {product_name} is not available.")
        break

    product_quantity=int(input(f"Enter the quantity of {product_name}: "))
    for j in range(product_quantity):
        shopping_cart.append(product_name)

total_bill=calculate_bill(shopping_cart)
print(f"Your total bill amount is: {total_bill}")
