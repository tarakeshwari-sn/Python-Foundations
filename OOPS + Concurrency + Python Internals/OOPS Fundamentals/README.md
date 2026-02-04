# Banking System 
This project is a console-based banking system developed using  JSON-based storage.  

It supports User and Manager roles with persistent data storage.

The system simulates real-world banking operations such as deposits, withdrawals, account creation, account freezing, and loan eligibility checks.


## Design Approach

The application is structured around real-world banking entities, modeled as Python classes i.e; User and Manager.

## User Class
The `User` class represents a bank customer and encapsulates:
- Account details
- PIN-based authentication
- Transaction operations

Each user object manages its own data and behavior (Encapsulation).

## Manager Class
The `Manager` class represents bank staff with administrative privileges, including:
- Creating new user accounts
- Viewing user details
- Freezing user accounts
- Checking loan eligibility

This design enforces role-based access control.

## Data Storage Using JSON
- User data is stored in a JSON file: `bank_details.json`
- Data is loaded when the application starts
- All updates are saved immediately after any modification

This ensures data remains intact across program executions.


## In-Memory Data Storage
```users = { account_number: User_object }```

## Serialization and Deserialization

To convert objects to and from JSON:

to_dict()	: Converts a User object into a dictionary.

from_dict()	: Recreates a User object from stored JSON

## Static Methods for Shared Operations

The following methods are declared as ```@staticmethod```:

```load_users()``` - To load data from JSON file.

```save_users()``` - To save data to JSON file.

They operate on shared application data (users) and do not depend on a specific object instance.

## Interaction with user
It uses menu driven console to interact with user and perform operations they have permission to perform.

# Inventory System 
This project is a console-based inventory management system developed using CSV-based storage.  

The system simulates real-world inventory operations such as product creation,quantity updation, stock input and stock output.

## Design Approach



## Data Storage Using JSON
- User data is stored in a CSV file: `inventory.csv`
- Data is loaded when the application starts.
- All updates are saved immediately after any modification.

This ensures data remains intact across program executions.


## In-Memory Data Storage
```users = { account_number: User_object }```


## Interaction with user
It uses menu driven console to interact with user and perform operations they have permission to perform.
