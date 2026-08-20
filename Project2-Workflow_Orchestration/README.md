# Cedar Creek Appointment Orchestration

## Overview

Cedar Creek is a fictional veterinary practice that is expanding its integration beyond simple data synchronization. This project demonstrates how multiple independent business systems can work together to complete a single business process while respecting system ownership and maintaining data integrity.

The project focuses on appointment orchestration: coordinating customer validation, patient validation, appointment scheduling, and billing preparation through a centralized workflow.

## Business Context

Following the successful implementation of customer synchronization between Customer Management and Billing, Cedar Creek is now looking to improve the appointment scheduling process.

Receptionists currently interact with several independent software systems while scheduling appointments. Although each system performs its own responsibilities well, coordinating work between them requires multiple manual steps and increases the likelihood of mistakes or incomplete workflows.

Rather than replacing these specialized systems, Cedar Creek has chosen to introduce an orchestration layer that coordinates the existing applications while allowing each system to remain responsible for its own data.

## Existing Systems

| System | Primary Responsibility | Primary Users | Source of Truth |
|--------|------------------------|---------------|-----------------|
| Customer Management | Customer contact information | Reception | Customer Data |
| Patient Records | Medical records and patient ownership | Veterinarians | Patient Data |
| Appointment Scheduling | Providers, appointment types, schedules, appointments | Reception | Scheduling Data |
| Billing | Charges and payment information | Billing Staff | Financial Records |

## Project Scope

This project focuses on coordinating a single business process across multiple systems: scheduling a veterinary appointment.

Rather than synchronizing data between systems, the orchestration layer validates information across multiple sources, applies business rules, creates downstream records where appropriate, and reports workflow outcomes.

Customer synchronization remains the responsibility of Project 1 and is assumed to already be functioning.

## Problem Statement

Scheduling a veterinary appointment requires information from several independent business systems.

Reception staff must verify customer information, locate the correct patient, ensure that the patient belongs to the selected customer, select an appointment type, confirm provider availability, create the appointment, and prepare downstream billing information.

Performing these steps manually increases the risk of scheduling errors, duplicate work, and incomplete workflows.

A successful solution should coordinate these systems automatically while ensuring that each system remains responsible for the information it owns.

## Data Ownership

Each business system remains responsible for its own information.

Customer Management owns customer identity and contact information.

Patient Records owns patient information, customer ownership relationships, medical records, and patient status.

Appointment Scheduling owns appointment types, appointment durations, provider schedules, and appointment records.

Billing owns billing references, charges, invoices, and payment information.

The orchestration layer does not permanently own business data. Instead, it coordinates communication between systems, validates business rules, and creates or updates records within the systems responsible for that information.

## Workflow Strategy

When a receptionist submits an appointment request, the workflow orchestrator validates the request across multiple systems before committing any changes.

The workflow verifies that the customer exists, confirms that the selected patient exists and belongs to the customer, checks that the patient is active, retrieves the appointment duration associated with the selected appointment type, validates provider availability for the requested time, creates the appointment, and creates a downstream billing reference.

If any validation step fails, the workflow stops immediately and reports the reason.

If a temporary system outage prevents validation from completing, the request is placed into a deferred retry queue and automatically retried once the affected system becomes available.

The workflow is considered successful only after all required validation steps have completed and every participating system has received the records it is responsible for.

## Workflow Architecture

The orchestration layer coordinates communication between four independent business systems while allowing each system to remain responsible for the data it owns.

![Workflow Architecture](diagrams/Workflow%20Architecture.png)

## Planned Implementation

- Validate customer identity through Customer Management.
- Validate patient ownership and active status through Patient Records.
- Retrieve appointment metadata from Appointment Scheduling.
- Calculate appointment end time using appointment duration.
- Validate provider availability.
- Detect duplicate appointment requests.
- Create appointment records for successful requests.
- Create downstream billing references for completed appointments.
- Simulate temporary system outages.
- Automatically retry deferred requests after simulated recovery.
- Produce operational reporting summarizing workflow outcomes.

## Workflow Logic

The following flow diagram illustrates the order in which business rules are evaluated, where requests may terminate, and how deferred requests are automatically retried after simulated system recovery.

![Workflow Logic](diagrams/Workflow%20Logic.png)

## Repository Structure

- `src/` contains the orchestration workflow, sample requests, and supporting scripts.
- `data/` contains SQLite databases representing each business system.
- `diagrams/` contains workflow and architecture diagrams.
- `docs/` contains supplemental engineering notes and design decisions.
- `README.md` documents project scope, architecture, execution, and expected behavior.

## Running the Project

### Prerequisites

- Python 3.10+
- DB Browser for SQLite (recommended for inspecting databases)
- Git (optional)

1. Clone the repository.
2. Navigate to the project source directory.
3. Seed the databases:

```bash
python3 seed_data.py      # macOS / Linux
python seed_data.py       # Windows
```

4. Execute the workflow:

```bash
python3 appointment_workflow.py     # macOS / Linux
python appointment_workflow.py      # Windows
```

Expected behavior:

- One appointment request completes successfully.
- Four requests fail business validation.
- One request is deferred because of a simulated Patient Records outage.
- The deferred request is automatically retried after simulated recovery.
- Successful requests create both appointment and billing records.
- A workflow summary is displayed after all requests have been processed.

## Sample Workflow Execution

Running the workflow processes each appointment request independently, reports validation failures immediately, automatically retries deferred requests after simulated recovery, and finishes with an operational summary.

![Workflow Output](diagrams/Workflow%20Output.png)

## Business Rules

The orchestration workflow enforces the following business rules before creating an appointment:

- Customer must exist and be active.
- Patient must exist.
- Patient must belong to the selected customer.
- Patient must be active.
- Appointment type must exist.
- Provider must exist.
- Provider must belong to the selected clinic.
- Provider must be active.
- Duplicate appointments are rejected.
- Providers cannot be scheduled for overlapping appointments.
- Billing records are created only after a successful appointment is created.

## Current Limitations

- Inter-system communication is simulated directly through SQLite databases rather than REST APIs.
- Workflow execution is initiated manually rather than by an external scheduling application.
- Provider availability considers only existing scheduled appointments and does not model calendars, breaks, or clinic hours.
- Billing records are created immediately after appointment creation without transactional rollback across systems.
- Retry behavior simulates a single temporary outage scenario rather than a persistent background retry service.
- Authentication, authorization, logging, and audit trails are outside the scope of this project.

## Resulting Appointment Records

Successful requests create appointment records within the Appointment Scheduling system while rejected requests leave scheduling data unchanged.

The screenshot below shows the resulting appointment table after workflow execution.

![Appointments Table](diagrams/Appointments%20Outcome.png)

## Relationship to Project 1

This project assumes that customer information has already been synchronized between Customer Management and Billing, as implemented in Project 1.

Rather than focusing on keeping data synchronized, this project demonstrates how multiple systems can be coordinated to complete a business process while respecting system ownership, enforcing business rules, and handling transient system failures.

