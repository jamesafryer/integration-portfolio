import sqlite3

def get_source_customers(customer_cursor):
    customer_cursor.execute('SELECT * FROM Customers')
    source_customers = customer_cursor.fetchall()
    return source_customers

def sync_customer(customer, billing_cursor):
    customer_id, first_name, last_name, email, phone, address, version, _ = customer
    billing_cursor.execute('''
        SELECT CustomerVersion FROM Customers WHERE CustomerID = ? ''',
        (customer_id,))
    billing_customer = billing_cursor.fetchone()
    if billing_customer is None:
        billing_cursor.execute('''
            INSERT INTO Customers (CustomerID, DisplayName, Email, Phone, Address, CustomerVersion)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (customer_id, f"{first_name} {last_name}", email, phone, address, version))
        return 'created'
    customer_version = billing_customer[0]
    if version > customer_version:
        billing_cursor.execute('''
            UPDATE Customers
            SET DisplayName = ?, Email = ?, Phone = ?, Address = ?, CustomerVersion = ?, LastSyncedAt = CURRENT_TIMESTAMP
            WHERE CustomerID = ?''',
            (f"{first_name} {last_name}", email, phone, address, version, customer_id))
        return 'updated'
    return 'unchanged'

def get_orphaned_customers(customer_cursor, billing_cursor):
    customer_cursor.execute('''
        SELECT CustomerID FROM Customers
    ''')
    source_customer_ids = {customer[0] for customer in customer_cursor.fetchall()}
    billing_cursor.execute('''
        SELECT CustomerID FROM Customers
    ''')
    billing_customer_ids = {customer[0] for customer in billing_cursor.fetchall()}
    orphaned_customer_ids = billing_customer_ids - source_customer_ids
    return orphaned_customer_ids

def print_summary(created, updated, unchanged, orphaned):
    print(
        f"Synchronization complete.\n\n"
        f"Created: {created}\n"
        f"Updated: {updated}\n"
        f"Unchanged: {unchanged}\n"
        f"Orphaned: {orphaned}"
    )

def main():
    customer_conn = sqlite3.connect('../data/CustomerManagement.db')
    billing_conn = sqlite3.connect('../data/Billing.db')

    customer_cursor = customer_conn.cursor()
    billing_cursor = billing_conn.cursor()
    customers_to_sync = get_source_customers(customer_cursor)

    created = 0
    updated = 0
    unchanged = 0

    for customer in customers_to_sync:
        result = sync_customer(customer, billing_cursor)
        if result == 'created':
            created += 1
        elif result == 'updated':
            updated += 1
        elif result == 'unchanged':
            unchanged += 1

    orphaned_customer_ids = get_orphaned_customers(customer_cursor, billing_cursor)
    orphaned = len(orphaned_customer_ids)

    billing_conn.commit()

    customer_conn.close()
    billing_conn.close()

    print_summary(created, updated, unchanged, orphaned)


if __name__ == "__main__":
    main()