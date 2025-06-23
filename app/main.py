from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .database import SessionLocal, init_db
from .redis_client import get_redis
from .elasticsearch_client import get_elasticsearch
from .crud import (
    get_all_departments, get_department_by_id, create_department, update_department,
    soft_delete_department, hard_delete_department, restore_department, get_all_soft_deleted_departments,
    get_all_employees, get_employee_by_id, create_employee, update_employee,
    soft_delete_employee, hard_delete_employee, restore_employee, get_all_soft_deleted_employees
)
from .schemas import DepartmentCreate, DepartmentUpdate, EmployeeCreate, EmployeeUpdate, Department, Employee
import redis
from pydantic import BaseModel
from typing import Any

app = FastAPI()

# Success response model
class SuccessResponse(BaseModel):
    message: str
    data: Any = None

# API Router with /api/v1 prefix
router = APIRouter(prefix="/api/v1")

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
        db.execute(text("SELECT 1"))
        app.state.db_status = "PostgreSQL connection successful"
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {
        "redis": app.state.redis_status,
        "elasticsearch": app.state.es_status,
        "postgresql": app.state.db_status
    }

# Department endpoints
@router.get("/departments/", response_model=list[Department])
async def read_departments(db: Session = Depends(get_db)):
    return get_all_departments(db)

@router.get("/departments/{department_id}", response_model=Department)
async def read_department(department_id: int, db: Session = Depends(get_db)):
    department = get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.post("/departments/", response_model=SuccessResponse)
async def create_dept(department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = create_department(db, department)
    return {"message": "Department created successfully", "data": db_department}

@router.put("/departments/{department_id}", response_model=SuccessResponse)
async def update_dept(department_id: int, department: DepartmentUpdate, db: Session = Depends(get_db)):
    db_department = update_department(db, department_id, department)
    return {"message": "Department updated successfully", "data": db_department}

@router.delete("/departments/{department_id}/soft", response_model=SuccessResponse)
async def soft_delete_dept(department_id: int, db: Session = Depends(get_db)):
    soft_delete_department(db, department_id)
    return {"message": "Department soft deleted successfully"}

@router.delete("/departments/{department_id}/hard", response_model=SuccessResponse)
async def hard_delete_dept(department_id: int, db: Session = Depends(get_db)):
    hard_delete_department(db, department_id)
    return {"message": "Department permanently deleted successfully"}

@router.post("/departments/{department_id}/restore", response_model=SuccessResponse)
async def restore_dept(department_id: int, db: Session = Depends(get_db)):
    restore_department(db, department_id)
    return {"message": "Department restored successfully"}

@router.get("/departments/soft-deleted", response_model=list[Department])
async def get_soft_deleted_depts(db: Session = Depends(get_db)):
    return get_all_soft_deleted_departments(db)

# Employee endpoints
@router.get("/employees/", response_model=list[Employee])
async def read_employees(db: Session = Depends(get_db)):
    return get_all_employees(db)

@router.get("/employees/{employee_id}", response_model=Employee)
async def read_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/employees/", response_model=SuccessResponse)
async def create_emp(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = create_employee(db, employee)
    return {"message": "Employee created successfully", "data": db_employee}

@router.put("/employees/{employee_id}", response_model=SuccessResponse)
async def update_emp(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = update_employee(db, employee_id, employee)
    return {"message": "Employee updated successfully", "data": db_employee}

@router.delete("/employees/{employee_id}/soft", response_model=SuccessResponse)
async def soft_delete_emp(employee_id: int, db: Session = Depends(get_db)):
    soft_delete_employee(db, employee_id)
    return {"message": "Employee soft deleted successfully"}

@router.delete("/employees/{employee_id}/hard", response_model=SuccessResponse)
async def hard_delete_emp(employee_id: int, db: Session = Depends(get_db)):
    hard_delete_employee(db, employee_id)
    return {"message": "Employee permanently deleted successfully"}

@router.post("/employees/{employee_id}/restore", response_model=SuccessResponse)
async def restore_emp(employee_id: int, db: Session = Depends(get_db)):
    restore_employee(db, employee_id)
    return {"message": "Employee restored successfully"}

@router.get("/employees/soft-deleted", response_model=list[Employee])
async def get_soft_deleted_emps(db: Session = Depends(get_db)):
    return get_all_soft_deleted_employees(db)

# Include the router in the app
app.include_router(router)
