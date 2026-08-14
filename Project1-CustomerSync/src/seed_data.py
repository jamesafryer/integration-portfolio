import sqlite3

customer_conn = sqlite3.connect('../data/CustomerManagement.db')
billing_conn = sqlite3.connect('../data/Billing.db')

customer_cursor = customer_conn.cursor()
billing_cursor = billing_conn.cursor()

customers = [
    {'CustomerID': 1, 'FirstName': 'Emily', 'LastName': 'Carter', 'Email': 'emily.carter@email.com', 'Phone': '(904) 555-0181', 'Address': '125 Oak St, Jacksonville, FL', 'Version': 3},
    {'CustomerID': 2, 'FirstName': 'Michael', 'LastName': 'Nguyen', 'Email': 'michael.nguyen@email.com', 'Phone': '(904) 555-0127', 'Address': '48 River Rd, Jacksonville, FL', 'Version': 1},
    {'CustomerID': 3, 'FirstName': 'Sarah', 'LastName': 'Thompson', 'Email': 'sarah.thompson@email.com', 'Phone': '(904) 555-0144', 'Address': '910 Maple Ave, Jacksonville, FL', 'Version': 5},
    {'CustomerID': 4, 'FirstName': 'David', 'LastName': 'Ramirez', 'Email': 'david.ramirez@email.com', 'Phone': '(904) 555-0193', 'Address': '77 Cedar Ln, Jacksonville, FL', 'Version': 2},
    {'CustomerID': 5, 'FirstName': 'Olivia', 'LastName': 'Brooks', 'Email': 'olivia.brooks@email.com', 'Phone': '(904) 555-0168', 'Address': '300 Pine Ct, Jacksonville, FL', 'Version': 1}
]
billing_customers = [
    {'CustomerID': 1, 'DisplayName': 'Emily Carter', 'Email': 'emily.carter@email.com', 'Phone': '(904) 555-0100', 'Address': '125 Oak St, Jacksonville, FL', 'CustomerVersion': 2},
    {'CustomerID': 2, 'DisplayName': 'Michael Nguyen', 'Email': 'michael.nguyen@email.com', 'Phone': '(904) 555-0127', 'Address': '48 River Rd, Jacksonville, FL', 'CustomerVersion': 1},
    {'CustomerID': 3, 'DisplayName': 'Sarah Thompson', 'Email': 'sarah.old@email.com', 'Phone': '(904) 555-0144', 'Address': '910 Maple Ave, Jacksonville, FL', 'CustomerVersion': 4},
    {'CustomerID': 4, 'DisplayName': 'David Ramirez', 'Email': 'david.ramirez@email.com', 'Phone': '(904) 555-0193', 'Address': '77 Cedar Ln, Jacksonville, FL', 'CustomerVersion': 2},
    {'CustomerID': 6, 'DisplayName': 'Robert Evans', 'Email': 'robert.evans@email.com', 'Phone': '(904) 555-0111', 'Address': '22 Birch Way, Jacksonville, FL', 'CustomerVersion': 1}
]

customer_cursor.execute('DELETE FROM Customers')
billing_cursor.execute('DELETE FROM Customers')

for customer in customers:
    customer_cursor.execute('''
        INSERT INTO Customers (CustomerID, FirstName, LastName, Email, Phone, Address, Version)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer['CustomerID'], customer['FirstName'], customer['LastName'], customer['Email'], customer['Phone'], customer['Address'], customer['Version']))
for billing_customer in billing_customers:
    billing_cursor.execute('''
        INSERT INTO Customers (CustomerID, DisplayName, Email, Phone, Address, CustomerVersion)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (billing_customer['CustomerID'], billing_customer['DisplayName'], billing_customer['Email'], billing_customer['Phone'], billing_customer['Address'], billing_customer['CustomerVersion']))

customer_conn.commit()
billing_conn.commit()

customer_conn.close()
billing_conn.close()

print("Seed data inserted into CustomerManagement.db and Billing.db successfully.")