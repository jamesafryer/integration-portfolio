appointment_requests = [
    # Happy Path (everything works)
    {
        'RequestID': 9001,
        'CustomerID': 1,
        'PatientID': 101,
        'AppointmentTypeID': 1, 
        'ProviderID': 1,
        'ClinicID': 1,
        'RequestedStartTime': '2026-08-25 09:00:00'
    },

    # Patient belongs to a different customer
    {
        'RequestID': 9002,
        'CustomerID': 2,
        'PatientID': 101,
        'AppointmentTypeID': 4, 
        'ProviderID': 3,
        'ClinicID': 1,
        'RequestedStartTime': '2026-08-25 12:00:00'
    },

    # Inactive patient
    {
        'RequestID': 9003,
        'CustomerID': 3,
        'PatientID': 105,
        'AppointmentTypeID': 1,
        'ProviderID': 3, 
        'ClinicID': 1, 
        'RequestedStartTime': '2026-08-25 13:00:00'
    },

    # Provider conflict
    {
        'RequestID': 9004,
        'CustomerID': 4, 
        'PatientID': 106, 
        'AppointmentTypeID': 2, 
        'ProviderID': 1, 
        'ClinicID': 1,
        'RequestedStartTime': '2026-08-25 10:15:00'
    },

    # Duplicate appointment
    {
        'RequestID': 9005,
        'CustomerID': 5, 
        'PatientID': 107,
        'AppointmentTypeID': 1,
        'ProviderID': 2,
        'ClinicID': 2, 
        'RequestedStartTime': '2026-08-25 14:00:00'
    },

    # Otherwise valid request used for Patient Records outage/retry
    {
        'RequestID': 9006,
        'CustomerID': 2,
        'PatientID': 103,
        'AppointmentTypeID': 4, 
        'ProviderID': 2, 
        'ClinicID': 2,
        'RequestedStartTime': '2026-08-25 15:00:00'
    }
]