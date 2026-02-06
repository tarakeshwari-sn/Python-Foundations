# Banking System 
Console-based banking system developed using  JSON-based storage.  

It supports User and Manager roles with persistent data storage and simulates real world working operations such as creating account,deposits,withdrawals etc.

## Roles and Operations: 

Each user of the system needs to log in using their id and password to perform operations with respect to their role.

### User
1. deposit(amt)
2. withdraw(amt)
3. display(pin)
4. update_pin(old_pin,new_pin)
5. close_Acc(pin)
6. transfer(to_acc, amt, pin)

### Manager
1. create_account(acc, uname, pin, bal) -- for user
2. view_user(acc)
3. freeze_account(acc) --- of user
4. loan_eligibility(acc)
5. view_all_users()

## Concepts Used: 
 Classes and objects - Defined real-world entities as classes and created multiple objects at runtime. Object methods (user.deposit(), manager.create_account() ) are used for implementation.

init - Used to initialize object state and set default values. It prepares object for use.

Instance variables - Each object has them individually.

## Storage: 
Data is stored in a JSON file in the following format: 

```users = { account_number: User_object }```

## Serialization and Deserialization: 

To convert objects to and from JSON:

```to_dict()```	: Converts a User object into a dictionary.

```from_dict()```	: Recreates a User object from stored JSON

## Static Methods for Shared Operations: 

The following methods are declared as ```@staticmethod```:

```load_users()``` - To load data from JSON file.

```save_users()``` - To save data to JSON file.

They operate on shared application data (users) and do not depend on a specific object instance.


# Inventory System 
Console-based inventory system developed using CSV-based storage.  

## Operations: 
1. create_product()
2. delete_product()
3. update_product() --- price
4. view_all() ---view all products
5. search(value) --- search specific product
6. stock_in(pid,qty) --- stock in of specific product
7. stock_out(pid_qty) --- stock out of specific product

Analytics:
1. inv.low_stock_products()
2. out_of_stock_products()
3. total_inventory_value()
4. highest_priced_products()
5. lowest_priced_products()
6. product_summary()

## Concepts Used: 
 Classes and objects - Defined real-world entities as classes and created multiple objects at runtime. Object methods are used for implementation.

init - Used to initialize object state and set default values. It prepares object for use.

Instance and class variables - Each object has them individually.

## Storage: 
Data is stored in CSV in the following format:
```
product_id,name,price,quantity
1,chocolates,35.0,33
```