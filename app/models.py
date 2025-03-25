from sqlalchemy import Column, Integer, String
from .database import Base

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    department = Column(String(255))

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    job = Column(String(255))

class HiredEmployee(Base):
    __tablename__ = "hired_employees"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    datetime = Column(String(255))
    department_id = Column(Integer)
    job_id = Column(Integer)