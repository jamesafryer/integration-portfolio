import sqlite3
from demo_requests import appointment_requests
from datetime import datetime, timedelta

SIMULATE_PATIENT_RECORDS_OUTAGE = True
SIMULATE_RECOVERY_BEFORE_RETRY = True
OUTAGE_REQUEST_ID = 9006

def validate_customer(customer_cursor, req_customer_id):
    customer_cursor.execute('''
        SELECT CustomerID, Active FROM Customers WHERE CustomerID = ? ''', 
        (req_customer_id,))
    customer = customer_cursor.fetchone()
    if customer is None:
        return {
            'success': False,
            'reason': 'Customer does not exist.'
        }
    _, active = customer
    if active == 0:
        return {
            'success': False,
            'reason': 'Customer is inactive.'
        }
    return {
        'success': True
    }

def should_simulate_patient_outage(request_id, outage_active):
    return (
        SIMULATE_PATIENT_RECORDS_OUTAGE
        and outage_active
        and request_id == OUTAGE_REQUEST_ID
    )

def validate_patient(patient_cursor, req_patient_id, req_customer_id):
    patient_cursor.execute('''
        SELECT PatientID, CustomerID, Active FROM Patients WHERE PatientID = ? ''',
        (req_patient_id,))
    patient = patient_cursor.fetchone()
    if patient is None:
        return {
            'success': False,
            'reason': 'Patient does not exist.'
        }
    _, customer_id, active = patient
    if customer_id != req_customer_id:
        return {
            'success': False,
            'reason': 'Patient is not listed under this customer.'
        }
    if active == 0:
        return {
            'success': False,
            'reason': 'Patient is inactive.'
        }
    return {
        'success': True
    }

def prepare_appt_details(appt_cursor, req_appt_type_id, req_start_time):
    appt_cursor.execute('''
        SELECT Name, DurationMinutes, BaseCharge FROM AppointmentTypes WHERE AppointmentTypeID = ? ''',
        (req_appt_type_id,))
    appointment = appt_cursor.fetchone()
    if appointment is None:
        return {
            'success': False,
            'reason': 'Appointment type is invalid.'
        }
    appt_type_name, duration_minutes, base_charge = appointment
    start_time = datetime.strptime(
        req_start_time,
        '%Y-%m-%d %H:%M:%S'
    )
    end_time = start_time + timedelta(minutes=duration_minutes)
    return {
        'success': True,
        'appointment_type_name': appt_type_name,
        'duration_minutes': duration_minutes,
        'base_charge': base_charge,
        'start_time': req_start_time,
        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')
    }

def validate_provider(appt_cursor, req_provider_id, req_clinic_id):
    appt_cursor.execute('''
        SELECT ProviderID, ClinicID, Active FROM Providers WHERE ProviderID = ? ''',
        (req_provider_id,))
    provider = appt_cursor.fetchone()
    if provider is None:
        return {
            'success': False,
            'reason': 'Provider does not exist.'
        }
    _, clinic_id, active = provider
    if req_clinic_id != clinic_id:
        return {
            'success': False,
            'reason': 'Provider does not work at specified clinic.'
        }
    if active == 0:
        return {
            'success': False,
            'reason': 'Provider is not active.'
        }
    return {
        'success': True
    }

def check_duplicate_appt(appt_cursor, request, appt_details):
    appt_cursor.execute('''
        SELECT AppointmentID 
        FROM Appointments 
        WHERE 
        CustomerID = ? AND 
        PatientID = ? AND 
        ProviderID = ? AND 
        ClinicID = ? AND 
        AppointmentTypeID = ? AND 
        StartTime = ? AND 
        EndTime = ? 
        ''', (request['CustomerID'], request['PatientID'], request['ProviderID'], request['ClinicID'], request['AppointmentTypeID'], appt_details['start_time'], appt_details['end_time']))
    duplicate = appt_cursor.fetchone()
    if duplicate is not None:
        return {
            'success': False,
            'reason': 'An identical appointment already exists.'
        }
    return {
        'success': True
    }

def validate_provider_availability(appt_cursor, req_provider_id, appt_details):
    req_start_time = datetime.strptime(appt_details['start_time'], '%Y-%m-%d %H:%M:%S')
    req_end_time = datetime.strptime(appt_details['end_time'], '%Y-%m-%d %H:%M:%S')
    appt_cursor.execute('''
        SELECT StartTime, EndTime FROM Appointments WHERE ProviderID = ? AND Status = "Scheduled" 
        ''', (req_provider_id,))
    existing_appointments = appt_cursor.fetchall()
    for appointment in existing_appointments:
        existing_start_str, existing_end_str = appointment
        existing_start = datetime.strptime(existing_start_str, '%Y-%m-%d %H:%M:%S')
        existing_end = datetime.strptime(existing_end_str, '%Y-%m-%d %H:%M:%S')
        if req_start_time < existing_end and req_end_time > existing_start:
            return {
                'success': False,
                'reason': 'Provider is unavailable during the requested time.'
            }
    return {
        'success': True
    }

def create_appt(appt_cursor, request, appt_details):
    appt_cursor.execute('SELECT MAX(AppointmentID) FROM Appointments')
    max_id = appt_cursor.fetchone()[0]
    if max_id is None:
        new_appt_id = 5001
    else:
        new_appt_id = max_id + 1
    appt_cursor.execute('''
        INSERT INTO Appointments (AppointmentID, CustomerID, PatientID, ProviderID, ClinicID, AppointmentTypeID, StartTime, EndTime, Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
        (new_appt_id, request['CustomerID'], request['PatientID'], request['ProviderID'], request['ClinicID'], request['AppointmentTypeID'], appt_details['start_time'], appt_details['end_time'], 'Scheduled'))
    return {
        'success': True,
        'new_appt_id': new_appt_id,
        'customer_id': request['CustomerID'],
        'new_appt_type': request['AppointmentTypeID']
    }

def create_pending_charge(billing_cursor, created_appt, appt_details):
    billing_cursor.execute('SELECT MAX(ChargeID) FROM PendingCharges')
    max_id = billing_cursor.fetchone()[0]
    if max_id is None:
        new_charge_id = 7001
    else:
        new_charge_id = max_id + 1
    billing_cursor.execute('''
        INSERT INTO PendingCharges (ChargeID, AppointmentID, CustomerID, Amount, Status)
        VALUES (?, ?, ?, ?, ?)''',
        (new_charge_id, created_appt['new_appt_id'], created_appt['customer_id'], appt_details['base_charge'], 'Pending'))
    return {
        'success': True,
        'charge_id': new_charge_id,
    }

def orchestrate_workflow(appt_cursor, billing_cursor, customer_cursor, patient_cursor, request, outage_active):
    customer_check = validate_customer(customer_cursor, request['CustomerID'])
    if not customer_check['success']:
        return {
            'success': False,
            'request_id': request['RequestID'],
            'stage': 'Customer Validation',
            'reason': customer_check['reason'],
            'action': 'Verify customer record.'
        }
    if should_simulate_patient_outage(request['RequestID'], outage_active):
        raise ConnectionError('Simulated Patient Records system outage')
    patient_check = validate_patient(patient_cursor, request['PatientID'], request['CustomerID'])
    if not patient_check['success']:
        return {
            'success': False,
            'request_id': request['RequestID'],
            'stage': 'Patient Validation',
            'reason': patient_check['reason'],
            'action': 'Verify patient record.'
        }
    appt_details = prepare_appt_details(appt_cursor, request['AppointmentTypeID'], request['RequestedStartTime'])
    if not appt_details['success']:
        return {
            'success': False,
            'request_id': request['RequestID'],
            'stage': 'Appointment Details',
            'reason': appt_details['reason'],
            'action': 'Verify appointment type.'
        }
    provider_check = validate_provider(appt_cursor, request['ProviderID'], request['ClinicID'])
    if not provider_check['success']:
        return {
            'success': False,
            'request_id': request['RequestID'],
            'stage': 'Provider Validation',
            'reason': provider_check['reason'],
            'action': 'Verify provider record.'
        }
    duplicate_check = check_duplicate_appt(appt_cursor, request, appt_details)
    if not duplicate_check['success']:
        return {
            'success': False,
            'request_id': request['RequestID'],
            'stage': 'Duplicate Check',
            'reason': duplicate_check['reason'],
            'action': 'Review existing appointment; no new appointment was created.'
        }
    availability_check = validate_provider_availability(appt_cursor, request['ProviderID'], appt_details)
    if not availability_check['success']:
        return {
            'success': False,
            'request_id': request['RequestID'],
            'stage': 'Availability Check',
            'reason': availability_check['reason'],
            'action': 'Select another provider or time.'
        }
    created_appt = create_appt(appt_cursor, request, appt_details)
    created_charge = create_pending_charge(billing_cursor, created_appt, appt_details)
    return {
        'success': True,
        'request_id': request['RequestID'],
        'charge_id': created_charge['charge_id'],
        'appt_id': created_appt['new_appt_id']
    }

def print_results(result):
    if result['success']:
        print(
            '==================================\n'
            f"Request {result['request_id']}\n\n"
            'SUCCESS\n\n'
            f"Appointment Created ID: {result['appt_id']}\n\n"
            f"Pending Charge ID: {result['charge_id']}\n"
        )
    else:
        print(
            '==================================\n'
            f"Request {result['request_id']}\n\n"
            'FAILED\n\n'
            f"Stage: {result['stage']}\n"
            f"Reason: {result['reason']}\n"
            f"Recommended Action: {result['action']}\n"
        )

def print_summary(successes, fails, defers, good_retries, pending_retries, failed_retries):
    print(
        '======== Workflow Summary ========\n\n'
        f'Successful: {successes}\n'
        f'Failed: {fails}\n'
        f'Deferred: {defers}\n'
        f'Retry Successful: {good_retries}\n'
        f'Retry Pending: {pending_retries}\n'
        f'Retry Failed: {failed_retries}\n'
    )

def print_deferred(deferred_item):
    print(
        '==================================\n'
        f"Request {deferred_item['request']['RequestID']}\n\n"
        'DEFERRED\n\n'
        f"Reason: {deferred_item['reason']}\n"
        'Action: No action required; retry scheduled automatically\n'
    )

def print_retry_results(result):
    if result['success']:
        print(
            '==================================\n'
            f"Request {result['request_id']}\n\n"
            'RETRY SUCCESS\n\n'
            f"Appointment Created ID: {result['appt_id']}\n\n"
            f"Pending Charge ID: {result['charge_id']}\n"
        )
    else:
        print(
            '==================================\n'
            f"Request {result['request_id']}\n\n"
            'RETRY FAILED\n\n'
            f"Stage: {result['stage']}\n"
            f"Reason: {result['reason']}\n"
            f"Recommended Action: {result['action']}\n"
        )

def main():
    appt_conn = sqlite3.connect('../data/AppointmentScheduling.db')
    billing_conn = sqlite3.connect('../data/Billing.db')
    customer_conn = sqlite3.connect('../data/CustomerManagement.db')
    patient_conn = sqlite3.connect('../data/PatientRecords.db')

    appt_cursor = appt_conn.cursor()
    billing_cursor = billing_conn.cursor()
    customer_cursor = customer_conn.cursor()
    patient_cursor = patient_conn.cursor()

    outage_active = SIMULATE_PATIENT_RECORDS_OUTAGE

    successes = 0
    fails = 0
    defers = 0
    good_retries = 0
    pending_retries = 0
    failed_retries = 0

    deferred_queue = []
    pending_queue = []

    for request in appointment_requests:
        try:
            result = orchestrate_workflow(appt_cursor, billing_cursor, customer_cursor, patient_cursor, request, outage_active)
            if not result['success']:
                fails += 1
            else:
                successes += 1
            print_results(result)
        except ConnectionError as e:
            deferred_queue.append({
                'request': request,
                'reason': str(e)
            })
            print_deferred({
                'request': request,
                'reason': str(e)
            })
            defers += 1

    if SIMULATE_RECOVERY_BEFORE_RETRY:
        outage_active = False

    for item in deferred_queue:
        try:
            result = orchestrate_workflow(appt_cursor, billing_cursor, customer_cursor, patient_cursor, item['request'], outage_active)
            if not result['success']:
                failed_retries += 1
            else:
                good_retries += 1
            print_retry_results(result)
        except ConnectionError as e:
            pending_queue.append({
                'request': item['request'],
                'reason': str(e)
                })
            pending_retries += 1

    for item in pending_queue:
        print(
            '==================================\n'
            f"Request {item['request']['RequestID']} could not be completed at this time.\n"
            'RETRY PENDING\n\n'
            f"Reason: {item['reason']}\n"
            'Recommended Action: Contact system administrator.\n'
        )

    print_summary(successes, fails, defers, good_retries, pending_retries, failed_retries)

    appt_conn.commit()
    billing_conn.commit()

    appt_conn.close()
    billing_conn.close()
    customer_conn.close()
    patient_conn.close()

if __name__ == "__main__":
    main()