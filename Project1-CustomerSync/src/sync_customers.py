import sqlite3

customer_conn = sqlite3.connect('../data/CustomerManagement.db')
billing_conn = sqlite3.connect('../data/Billing.db')

customer_cursor = customer_conn.cursor()
billing_cursor = billing_conn.cursor()

created = 0
updated = 0
unchanged = 0
orphaned = 0

customer_cursor.execute('''
    SELECT * FROM Customers
''')
fetched_customers = customer_cursor.fetchall()

for customer in fetched_customers:
    CustomerID, FirstName, LastName, Email, Phone, Address, Version, UpdatedAt = customer
    billing_cursor.execute('''
        SELECT * FROM Customers WHERE CustomerID = ? ''',
        (CustomerID,))
    billing_customer = billing_cursor.fetchone()
    if billing_customer is None:
        billing_cursor.execute('''
            INSERT INTO Customers (CustomerID, DisplayName, Email, Phone, Address, CustomerVersion)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (CustomerID, f"{FirstName} {LastName}", Email, Phone, Address, Version))
        created += 1
    else:
        _, DisplayName, BillingEmail, BillingPhone, BillingAddress, CustomerVersion, LastSyncedAt = billing_customer
        if Version > CustomerVersion:
            billing_cursor.execute('''
                UPDATE Customers
                SET DisplayName = ?, Email = ?, Phone = ?, Address = ?, CustomerVersion = ?, LastSyncedAt = CURRENT_TIMESTAMP
                WHERE CustomerID = ?''',
                (f"{FirstName} {LastName}", Email, Phone, Address, Version, CustomerID))
            updated += 1
        else:
            unchanged += 1

customer_cursor.execute('''
    SELECT CustomerID FROM Customers
''')
fetched_customer_ids = {customer[0] for customer in customer_cursor.fetchall()}
billing_cursor.execute('''
    SELECT CustomerID FROM Customers
''')
fetched_billing_customer_ids = {customer[0] for customer in billing_cursor.fetchall()}

orphaned_customer_ids = fetched_billing_customer_ids - fetched_customer_ids
orphaned = len(orphaned_customer_ids)

billing_conn.commit()

customer_conn.close()
billing_conn.close()

print(f"Synchronization complete. Created: {created}, Updated: {updated}, Unchanged: {unchanged}, Orphaned: {orphaned}.")