import sqlite3
from demo_requests import appointment_requests
from datetime import datetime, timedelta

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
        SELECT * FROM AppointmentTypes WHERE AppointmentTypeID = ? ''',
        (req_appt_type_id,))
    appointment = appt_cursor.fetchone()
    if appointment is None:
        return {
            'success': False,
            'reason': 'Appointment type is invalid.'
        }
    _, appt_type_name, duration_minutes, base_charge = appointment
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