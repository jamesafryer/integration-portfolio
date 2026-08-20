import sqlite3

appt_conn = sqlite3.connect('../data/AppointmentScheduling.db')
billing_conn = sqlite3.connect('../data/Billing.db')
customer_conn = sqlite3.connect('../data/CustomerManagement.db')
patient_conn = sqlite3.connect('../data/PatientRecords.db')

appt_cursor = appt_conn.cursor()
billing_cursor = billing_conn.cursor()
customer_cursor = customer_conn.cursor()
patient_cursor = patient_conn.cursor()

appt_cursor.execute('DELETE FROM Appointments')     # Reset transactional demo data.
billing_cursor.execute('DELETE FROM PendingCharges')       # IDs are explicitly assigned for deterministic testing,
customer_cursor.execute('DELETE FROM Customers')    # so AUTOINCREMENT values are not reset.
patient_cursor.execute('DELETE FROM Patients')

customers = [
    {
        'CustomerID': 1,
        'FirstName': 'Emily',
        'LastName': 'Carter',
        'Email': 'emily.carter@email.com',
        'Phone': '(904) 555-0181',
        'Address': '125 Oak St, Jacksonville, FL', 
        'Active': 1
    },
    {
        'CustomerID': 2,
        'FirstName': 'Michael',
        'LastName': 'Nguyen',
        'Email': 'michael.nguyen@email.com',
        'Phone': '(904) 555-0192',
        'Address': '48 River Rd, Jacksonville, FL',
        'Active': 1
    },
    {
        'CustomerID': 3,
        'FirstName': 'Sarah',
        'LastName': 'Thompson',
        'Email': 'sarah.thompson@email.com',
        'Phone': '(904) 555-0173',
        'Address': '77 Pine St, Jacksonville, FL',
        'Active': 1
    },
    {
        'CustomerID': 4,
        'FirstName': 'David',
        'LastName': 'Ramirez',
        'Email': 'david.ramirez@email.com',
        'Phone': '(904) 555-0164',
        'Address': '12 Cedar St, Jacksonville, FL',
        'Active': 1
    },
    {
        'CustomerID': 5,
        'FirstName': 'Olivia',
        'LastName': 'Brooks',
        'Email': 'olivia.brooks@email.com',
        'Phone': '(904) 555-0155',
        'Address': '34 Birch St, Jacksonville, FL',
        'Active': 1
    }
]
patients = [
    {
        'PatientID': 101,
        'CustomerID': 1,
        'Name': 'Buddy',
        'Species': 'Dog',
        'Breed': 'Golden Retriever',
        'Birthdate': '2018-05-12',
        'Active': 1
    },
    {
        'PatientID': 102,
        'CustomerID': 1,
        'Name': 'Pepper',
        'Species': 'Cat',
        'Breed': 'Domestic Shorthair',
        'Birthdate': '2020-08-22',
        'Active': 1
    },
    {
        'PatientID': 103,
        'CustomerID': 2,
        'Name': 'Nori',
        'Species': 'Cat',
        'Breed': 'Siamese',
        'Birthdate': '2019-03-15',
        'Active': 1
    },
    {
        'PatientID': 104,
        'CustomerID': 3,
        'Name': 'Daisy',
        'Species': 'Dog',
        'Breed': 'Beagle',
        'Birthdate': '2021-11-05',
        'Active': 1
    },
    {
        'PatientID': 105,
        'CustomerID': 3,
        'Name': 'Max',
        'Species': 'Dog',
        'Breed': 'Labrador Retriever',
        'Birthdate': '2014-02-28',
        'Active': 0
    },
    {
        'PatientID': 106,
        'CustomerID': 4,
        'Name': 'Luna',
        'Species': 'Cat',
        'Breed': 'Maine Coon',
        'Birthdate': '2017-09-10',
        'Active': 1
    },
    {
        'PatientID': 107,
        'CustomerID': 5,
        'Name': 'Milo',
        'Species': 'Dog',
        'Breed': 'Australian Shepherd',
        'Birthdate': '2023-02-14',
        'Active': 1
    }
]
existing_appointments = [
    {
        'AppointmentID': 5001,
        'CustomerID': 4,
        'PatientID': 106,
        'ProviderID': 1,
        'ClinicID': 1,
        'AppointmentTypeID': 2, 
        'StartTime': '2026-08-25 10:00:00',
        'EndTime': '2026-08-25 10:45:00',
        'Status': 'Scheduled'
    },
    {
        'AppointmentID': 5002,
        'CustomerID': 5,
        'PatientID': 107,
        'ProviderID': 2,
        'ClinicID': 2,
        'AppointmentTypeID': 1,
        'StartTime': '2026-08-25 14:00:00',
        'EndTime': '2026-08-25 14:30:00',
        'Status': 'Scheduled'
    },
    {
        'AppointmentID': 5003,
        'CustomerID': 3,
        'PatientID': 104,
        'ProviderID': 3, 
        'ClinicID': 1,
        'AppointmentTypeID': 4, 
        'StartTime': '2026-08-25 11:00:00',
        'EndTime': '2026-08-25 11:20:00',
        'Status': 'Scheduled'
    }
]
pending_charges = [
    {
        'ChargeID': 7001,
        'AppointmentID': 5001, 
        'CustomerID': 4,
        'Amount': 8500,
        'Status': 'Pending'
    },
    {
        'ChargeID': 7002,
        'AppointmentID': 5002,
        'CustomerID': 5,
        'Amount': 6500,
        'Status': 'Pending'
    },
    {
        'ChargeID': 7003,
        'AppointmentID': 5003,
        'CustomerID': 3,
        'Amount': 4000,
        'Status': 'Pending'
    }
]

for customer in customers:
    customer_cursor.execute('''
        INSERT INTO Customers (CustomerID, FirstName, LastName, Email, Phone, Address, Active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer['CustomerID'], customer['FirstName'], customer['LastName'], customer['Email'], customer['Phone'], customer['Address'], customer['Active']))
for patient in patients:
    patient_cursor.execute('''
        INSERT INTO Patients (PatientID, CustomerID, Name, Species, Breed, Birthdate, Active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient['PatientID'], patient['CustomerID'], patient['Name'], patient['Species'], patient['Breed'], patient['Birthdate'], patient['Active']))
for appointment in existing_appointments:
    appt_cursor.execute('''
        INSERT INTO Appointments (AppointmentID, CustomerID, PatientID, ProviderID, ClinicID, AppointmentTypeID, StartTime, EndTime, Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (appointment['AppointmentID'], appointment['CustomerID'], appointment['PatientID'], appointment['ProviderID'], appointment['ClinicID'], appointment['AppointmentTypeID'], appointment['StartTime'], appointment['EndTime'], appointment['Status']))
for charge in pending_charges:
    billing_cursor.execute('''
        INSERT INTO PendingCharges (ChargeID, AppointmentID, CustomerID, Amount, Status)
        VALUES (?, ?, ?, ?, ?)
        ''', (charge['ChargeID'], charge['AppointmentID'], charge['CustomerID'], charge['Amount'], charge['Status']))

appt_conn.commit()
billing_conn.commit()
customer_conn.commit()
patient_conn.commit()

appt_conn.close()
billing_conn.close()
customer_conn.close()
patient_conn.close()

print('Seed transactional data input successfully!')