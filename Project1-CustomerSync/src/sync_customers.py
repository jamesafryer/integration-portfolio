import sqlite3

SIMULATE_OUTAGE = True
SIMULATE_RECOVERY_BEFORE_RETRY = True
OUTAGE_CUSTOMER_ID = 3

def get_source_customers(customer_cursor):
    customer_cursor.execute('SELECT * FROM Customers')
    source_customers = customer_cursor.fetchall()
    return source_customers

def sync_customer(customer, billing_cursor, outage_active):
    customer_id, first_name, last_name, email, phone, address, version, _ = customer
    billing_cursor.execute('''
        SELECT CustomerVersion FROM Customers WHERE CustomerID = ? ''',
        (customer_id,))
    billing_customer = billing_cursor.fetchone()
    if should_simulate_outage(customer_id, outage_active):
        raise ConnectionError("Simulated Billing outage")
    if billing_customer is None:
        billing_cursor.execute('''
            INSERT INTO Customers (CustomerID, DisplayName, Email, Phone, Address, CustomerVersion)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (customer_id, f"{first_name} {last_name}", email, phone, address, version))
        return {
            'status': 'created',
            'customer_id': customer_id,
            'display_name': f"{first_name} {last_name}"
        }
    customer_version = billing_customer[0]
    if version > customer_version:
        billing_cursor.execute('''
            UPDATE Customers
            SET DisplayName = ?, Email = ?, Phone = ?, Address = ?, CustomerVersion = ?, LastSyncedAt = CURRENT_TIMESTAMP
            WHERE CustomerID = ?''',
            (f"{first_name} {last_name}", email, phone, address, version, customer_id))
        return {
            'status': 'updated',
            'customer_id': customer_id,
            'display_name': f"{first_name} {last_name}",
            'old_version': customer_version,
            'new_version': version
        }
    return {
        'status': 'unchanged',
        }

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
    orphaned_customers = []
    for orphaned_customer_id in orphaned_customer_ids:
        billing_cursor.execute('''
            SELECT DisplayName FROM Customers WHERE CustomerID = ?''', 
            (orphaned_customer_id,))
        orphaned_customers.append({
            'customer_id': orphaned_customer_id,
            'display_name': billing_cursor.fetchone()[0]
        })
    return orphaned_customers

def print_summary(created, updated, unchanged, orphaned, deferred, retry_pending, retry_successful):
    print(
        "=== Synchronization complete ===\n\n"
        "[CREATED]\n\n"
    )
    for c in created:
        print(
        f"Customer ID: {c['customer_id']}\n" 
        f"{c['display_name']}\n\n"
        )                                        
    print("[UPDATED]\n\n")
    for u in updated:
        print(
        f"Customer ID: {u['customer_id']}\n"
        f"{u['display_name']}\n"
        f"Version: {u['old_version']} -> {u['new_version']}\n\n"
        )
    print("[DEFERRED]\n\n")
    for d in deferred:
        print(
        f"Customer ID: {d['customer_id']}\n"
        f"{d['display_name']}\n"
        f"Reason: {d['reason']}\n\n"
        )
    print("[RETRY RESULTS]\n\n")
    for r in retry_successful:
        print(
        f"Customer ID: {r['customer_id']}\n"
        f"{r['display_name']}\n"
        f"Status: {r['status']}\n\n"
        )
    for r in retry_pending:
        print(
        f"Customer ID: {r['customer_id']}\n"
        f"{r['display_name']}\n"
        f"Status: {r['status']}\n"
        f"Reason: {r['reason']}\n\n"
        )
    print("=== Orphaned Customers ===\n\n")
    for o in orphaned:
        print(
        f"Customer ID: {o['customer_id']}\n"
        f"{o['display_name']}\n\n"
        )
    print(
        "=== Summary ===\n\n"
        f"Created: {len(created)}\n"
        f"Updated: {len(updated)}\n"
        f"Unchanged: {unchanged}\n\n"
        f"Deferred: {len(deferred)}\n"
        f"Retry Successful: {len(retry_successful)}\n"
        f"Retry Pending: {len(retry_pending)}\n\n"
        f"Orphaned: {len(orphaned)}"
    )

def should_simulate_outage(customer_id, outage_active):
    return (
        SIMULATE_OUTAGE
        and outage_active 
        and customer_id == OUTAGE_CUSTOMER_ID
    )

def main():
    customer_conn = sqlite3.connect('../data/CustomerManagement.db')
    billing_conn = sqlite3.connect('../data/Billing.db')

    customer_cursor = customer_conn.cursor()
    billing_cursor = billing_conn.cursor()
    customers_to_sync = get_source_customers(customer_cursor)

    outage_active = SIMULATE_OUTAGE

    created = []
    updated = []
    unchanged = 0
    deferred_customers = []
    deferred = []
    retry_pending = []
    retry_successful = []

    for customer in customers_to_sync:
        try:
            result = sync_customer(customer, billing_cursor, outage_active)
            if result['status'] == 'created':
                created.append(result)
            elif result['status'] == 'updated':
                updated.append(result)
            elif result['status'] == 'unchanged':
                unchanged += 1
        except ConnectionError as e:
            deferred.append({
                'customer_id': customer[0],
                'display_name': f"{customer[1]} {customer[2]}",
                'reason': str(e)
            })
            deferred_customers.append(customer)

    if SIMULATE_RECOVERY_BEFORE_RETRY:
        outage_active = False

    for customer in deferred_customers:
        try:
            result = sync_customer(customer, billing_cursor, outage_active)
            if result['status'] == 'created' or result['status'] == 'updated' or result['status'] == 'unchanged':
                retry_successful.append(result)
        except ConnectionError as e:
            retry_pending.append({
                'customer_id': customer[0],
                'display_name': f"{customer[1]} {customer[2]}",
                'status': 'retry_pending',
                'reason': str(e)
            })

    orphaned= get_orphaned_customers(customer_cursor, billing_cursor)

    billing_conn.commit()

    customer_conn.close()
    billing_conn.close()

    print_summary(created, updated, unchanged, orphaned, deferred, retry_pending, retry_successful)


if __name__ == "__main__":
    main()