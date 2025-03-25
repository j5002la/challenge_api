# challenge_api
globant-db-migrations

A FastAPI-based solution for uploading historical data from CSV files to PostgreSQL database.

## Features

- CSV upload for 3 entity types:
  - Departments
  - Jobs
  - Hired Employees
- Batch processing (1-1000 records per batch)
- Header-less CSV support
- PostgreSQL integration
- Data validation (NULLS)

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- FastAPI
- SQLAlchemy
- pandas

## Installation

1. Clone repository:
```bash
git clone git@github.com:j5002la/challenge_api.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
```sql
-- Create database and user
CREATE DATABASE globant_db;
\c globant_db;

CREATE USER globant_user WITH PASSWORD 'globant_pass';
GRANT ALL PRIVILEGES ON DATABASE globant_db TO globant_user;

-- Create tables
CREATE TABLE departments (
    id INT PRIMARY KEY,
    department VARCHAR(255) NOT NULL
);

CREATE TABLE jobs (
    id INT PRIMARY KEY,
    job VARCHAR(255) NOT NULL
);

CREATE TABLE hired_employees (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    datetime TIMESTAMP,
    department_id INT,
    job_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Create indexes
CREATE INDEX idx_he_datetime ON hired_employees(datetime);
CREATE INDEX idx_he_department ON hired_employees(department_id);
CREATE INDEX idx_he_job ON hired_employees(job_id);
```

## Configuration

Create `.env` file:
```ini
DATABASE_URL=postgresql://globant_user:globant_pass@localhost:5432/globant_db
```

## Usage

Start the server:
```bash
uvicorn app.main:app --reload
```

Example CSV upload:
```bash
curl -X POST -F "file=@departments.csv" http://localhost:8000/upload/departments?batch_size=500
```

Sample CSV format (no headers):
```
1,Engineering
2,Marketing
```

## API Documentation

- **POST** `/upload/{table_name}`
  - Parameters:
    - `table_name`: departments|jobs|hired_employees
    - `batch_size`: 1-1000 (default: 1000)
  - CSV file: Raw file upload without headers

Response:
```json
{
  "message": "Data uploaded successfully",
  "total_records": 1000,
  "inserted_records": 1000,
  "batches_used": 1
}
```

## Development Process

Key commit history showing evolution:
1. `feat: Initial FastAPI setup`
2. `build: Add PostgreSQL integration`
3. `feat: Add CSV upload endpoint`
4. `fix: Handle header-less CSVs`
5. `docs: Add API documentation`
6. `perf: Add batch processing`

Full history available in [COMMIT_HISTORY.md](COMMIT_HISTORY.md)