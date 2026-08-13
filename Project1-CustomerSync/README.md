# Cedar Creek Customer Synchronization

## Overview

Cedar Creek is a fictional veterinary practice that is looking to make navigation of their multiple systems more seamless and cohesive. This first project documents a relatively basic process of synchronizing records between two systems, one of which is the owner of the data. 

## Business Context

Cedar Creek is a relatively new veterinary practice, just expanding to their second clinic location. It has multiple software systems because the business has grown organically over time, and new systems were added as the need arose to transition to a digital format. 

They would prefer to integrate their multiple systems rather than buy one packaged software system because of employee fluency with the current systems and the training and cost incurred when implementing a new system from scratch. Also, their specialized systems include specific functions that they worry might be difficult for a general software system to replicate. 

## Existing Systems

| System | Primary Responsibility | Primary Users | Source of Truth | Synchronizes With |
|--------|------------------------|---------------|-----------------|-------------------|
| Customer Management | Customer contact information | Reception | Customer Data | Billing, Patient Records, Appointment Scheduling |
| Patient Records | Medical histories | Veterinarians | Medical Records | Customer Management |
| Appointment Scheduling | Appointments and schedules | Reception | Appointment Data | Customer Management |
| Billing | Invoices and payments | Billing Staff | Financial Records | Customer Management |

## Project Scope

Although several systems exist within Cedar Creek, this project focuses exclusively on the synchronization of customer information between Customer Management and Billing. The remaining systems provide business context and become the focus of later projects in this portfolio.

## Problem Statement

The current multiple system architecture means that each system that requires customer data is too independent and requires manual input for each customer. This is an issue when a customer needs to change contact information or other customer information, because the receptionists need to input the change in multiple systems. 

The risk is that sometimes our receptionists forget to change information across all the required systems, leaving one system with outdated or incorrect information. A successful resolution to this problem would mean that, when information is added or updated to the customer management system, the billing system updates with that new information automatically.

## Data Ownership

Customer-facing fields like their unique identifier, name, email, phone, address, etc. should all be owned by the Customer Management system. Billing-owned fields are things like invoice amount, balance, payment status, autopay settings, and payment settings. 

Billing can hold customer name and contact information as a local copy. Any discrepancies between these values and the matching ones in the Customer Management system can be resolved with the values from the Customer Management system taking precedence. Billing should never be able to edit customer-facing fields. Any changes should originate from Customer Management. 

This separation of ownership is defined so that discrepancies can be handled predictably and internally, automating the process of updating customer records. 

## Synchronization Strategy

Say, for example, a customer needs to change their phone number. The receptionist changes the information in the Customer Management system, which creates a patch update for the billing system, including a version number, the field(s) changed, and the customer's unique identifier. The billing system checks those records against the version number currently stored locally, and the newer version is what ends up being stored locally. 

Exceptional Cases:
If the same update arrives twice, it can be treated as a duplicate and not reapplied.
If an older update arrives after a new one and the field(s) changed are the same, we will keep the newer version's information.
If billing is temporarily unavailable, the queue will be populated with updates to be implemented once it comes back available.
Failed updates can be put into a deferred queue to be retried and reconciled. 

Synchronization will be considered successful if the system can run most changes on its own without needing manual input or troubleshooting outside of extremely exceptional cases.

## Planned Implementation

- Create SQLite databases
- Seed sample customers and billing customer snapshots
- Write basic synchronization
- Add field mapping
- Add version checks
- Add duplicate/stale handling
- Add deferred/recovery logic
- Replace simulated handoff with API communication

## Repository Structure

- src/ is code
- data/ will hold databases and sample data
- diagrams/ will hold project visualizations that could be distributed to internal team members or customer employees
- docs/ will hold any design notes or supplemental/training docs
- README explains project scope and purpose

## Lessons Learned

Will be updated as implementation progresses.