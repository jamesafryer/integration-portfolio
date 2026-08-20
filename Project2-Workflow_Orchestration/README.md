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

