# FastAPI + MongoDB Employee Assessment (LLUMO)

## Features
- CRUD APIs for employees
- Search employees by department
- Average salary aggregation
- Search employees by skill
- pagination for employee listing
- Unique index on "employee_id"
- MongoDB JSON schema validation
- JWT Authentication (protects Create/Update/Delete)

## Setup
1. Install MongoDB locally and start it.

2. Clone project, install requirements and run:
   - python -m venv venv
   - .\venv\Scripts\activate
   - pip install -r requirements.txt
   - uvicorn main:app --reload
