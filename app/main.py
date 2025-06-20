from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  # Add this import
from .database import SessionLocal, init_db
from .redis_client import get_redis
from .elasticsearch_client import get_elasticsearch
from .crud import (
    get_all_departments, get_department_by_id, create_department, update_department,
    soft_delete_department, hard_delete_department, restore_department, get_all_soft_deleted_departments,
    get_all_employees, get_employee_by_id, create_employee, update_employee,
    soft_delete_employee, hard_delete_employee, restore_employee, get_all_soft_deleted_employees
)
from .schemas import DepartmentCreate, DepartmentUpdate, EmployeeCreate, EmployeeUpdate
import redis
from elasticsearch import Elasticsearch

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    init_db()
    # Test connections
    try:
        redis_client = get_redis()
        redis_client.ping()
        app.state.redis_status = "Redis connection successful"
    except redis.ConnectionError:
        app.state.redis_status = "Redis connection failed"
    
    try:
        es_client = get_elasticsearch()
        es_client.ping()
        app.state.es_status = "Elasticsearch connection successful"
    except Exception:
        app.state.es_status = "Elasticsearch connection failed"
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # Use text() for raw SQL
        app.state.db_status = "PostgreSQL connection successful"
    finally:
        db.close()

# Rest of the code remains unchanged...
@app.get("/health")
async def health_check():
    return {
        "redis": app.state.redis_status,
        "elasticsearch": app.state.es_status,
        "postgresql": app.state.db_status
    }

# Department endpoints
@app.get("/departments/")
async def read_departments(db: Session = Depends(get_db)):
    return get_all_departments(db)

@app.get("/departments/{department_id}")
async def read_department(department_id: int, db: Session = Depends(get_db)):
    return get_department_by_id(db, department_id)

@app.post("/departments/")
async def create_dept(department: DepartmentCreate, db: Session = Depends(get_db)):
    return create_department(db, department)

@app.put("/departments/{department_id}")
async def update_dept(department_id: int, department: DepartmentUpdate, db: Session = Depends(get_db)):
    return update_department(db, department_id, department)

@app.delete("/departments/{department_id}/soft")
async def soft_delete_dept(department_id: int, db: Session = Depends(get_db)):
    return soft_delete_department(db, department_id)

@app.delete("/departments/{department_id}/hard")
async def hard_delete_dept(department_id: int, db: Session = Depends(get_db)):
    return hard_delete_department(db, department_id)

@app.post("/departments/{department_id}/restore")
async def restore_dept(department_id: int, db: Session = Depends(get_db)):
    return restore_department(db, department_id)

@app.get("/departments/soft-deleted")
async def get_soft_deleted_depts(db: Session = Depends(get_db)):
    return get_all_soft_deleted_departments(db)

# Employee endpoints
@app.get("/employees/")
async def read_employees(db: Session = Depends(get_db)):
    return get_all_employees(db)

@app.get("/employees/{employee_id}")
async def read_employee(employee_id: int, db: Session = Depends(get_db)):
    return get_employee_by_id(db, employee_id)

@app.post("/employees/")
async def create_emp(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, employee)

@app.put("/employees/{employee_id}")
async def update_emp(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    return update_employee(db, employee_id, employee)

@app.delete("/employees/{employee_id}/soft")
async def soft_delete_emp(employee_id: int, db: Session = Depends(get_db)):
    return soft_delete_employee(db, employee_id)

@app.delete("/employees/{employee_id}/hard")
async def hard_delete_emp(employee_id: int, db: Session = Depends(get_db)):
    return hard_delete_employee(db, employee_id)

@app.post("/employees/{employee_id}/restore")
async def restore_emp(employee_id: int, db: Session = Depends(get_db)):
    return restore_employee(db, employee_id)

@app.get("/employees/soft-deleted")
async def get_soft_deleted_emps(db: Session = Depends(get_db)):
    return get_all_soft_deleted_employees(db)
