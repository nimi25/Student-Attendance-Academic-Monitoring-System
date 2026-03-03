**Project Overview**

The Student Attendance Monitoring System is a Python-based web application designed to track, manage, and analyze student attendance on a subject-wise basis.
The system integrates Python backend logic with SQL database management to store structured data, automate attendance calculations, and generate eligibility reports.
This project follows a modular and structured design approach, separating business logic, database operations, and user interface.

**Business Problem**

In many academic institutions, attendance tracking is either manually maintained or partially automated. This often results in:
- Errors in attendance calculation
- Lack of subject-wise visibility                                                                                                                                                                                
- Confusion regarding minimum attendance requirements (e.g., 85%)
- Delayed identification of attendance shortages
- Inefficient tracking of medical claims
- Students and administrators require a reliable system that can:
- Store attendance data in a structured format
- Automatically compute percentages
- Identify eligibility status
- Determine the number of additional classes required

This system provides a centralized and automated solution to improve academic monitoring and decision-making.

**Technologies Used**

- Python 3
- Flask (Web Framework)
- SQL (SQLite/MySQL)
- HTML
- CSS

**SQL Integration**

The system uses an SQL database to ensure structured data storage and retrieval.
Database Operations Used:
CREATE TABLE (Students, Subjects, Attendance)
INSERT (Add student and attendance records)
UPDATE (Apply medical claims, update attendance)
SELECT (Generate reports)
JOIN (Student-wise subject summary)
Aggregate queries for attendance reporting

**System Features:**

**1. Student Management**

Add new students
Store roll number and academic details
View student records

**2. Subject-wise Attendance Tracking**

Record total classes conducted
Record classes attended
Apply medical attendance claims
Update attendance dynamically

**3. Automated Calculations**

Attendance percentage per subject
Overall attendance percentage
Eligibility status (≥ 85% or below)
Minimum additional classes required to reach 85%

**4. Reporting & Monitoring**

Subject-wise attendance summar
Overall attendance dashboard
Shortage alerts
Structured report generation
 
**Attendance Calculation Logic**

Attendance Percentage:
(attended_classes + medical_claims) / total_classes × 100

Minimum Classes Required to Reach 85%:
(attended + x) / (total + x) ≥ 0.85

Where:
x = number of future classes required
The system automatically computes this value using backend Python functions.

**Academic Objectives Covered**

- Modular programming using functions
- Object-oriented design
- SQL database integration
- Exception handling
- Data validation
- Structured MIS reporting
