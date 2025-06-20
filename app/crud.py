from sqlalchemy.orm import Session
from .models import Department, Employee
from .schemas import DepartmentCreate, DepartmentUpdate, EmployeeCreate, EmployeeUpdate
from datetime import datetime
from fastapi import HTTPException

# Department CRUD
def get_all_departments(db: Session):
    return db.query(Department).filter(Department.deleted_at == None).all()

def get_department_by_id(db: Session, department_id: int):
    department = db.query(Department).filter(Department.id == department_id, Department.deleted_at == None).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

def create_department(db: Session, department: DepartmentCreate):
    db_department = Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def update_department(db: Session, department_id: int, department: DepartmentUpdate):
    db_department = get_department_by_id(db, department_id)
    for key, value in department.dict().items():
        setattr(db_department, key, value)
    db_department.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_department)
    return db_department

def soft_delete_department(db: Session, department_id: int):
    db_department = get_department_by_id(db, department_id)
    if not db_department.can_deleted:
        raise HTTPException(status_code=400, detail="Department cannot be deleted")
    db_department.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Department soft deleted"}

def hard_delete_department(db: Session, department_id: int):
    db_department = get_department_by_id(db, department_id)
    if not db_department.can_deleted:
        raise HTTPException(status_code=400, detail="Department cannot be deleted")
    db.delete(db_department)
    db.commit()
    return {"message": "Department permanently deleted"}

def restore_department(db: Session, department_id: int):
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    department.deleted_at = None
    db.commit()
    return {"message": "Department restored"}

def get_all_soft_deleted_departments(db: Session):
    return db.query(Department).filter(Department.deleted_at != None).all()

# Employee CRUD
def get_all_employees(db: Session):
    return db.query(Employee).filter(Employee.deleted_at == None).all()

def get_employee_by_id(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.deleted_at == None).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

def create_employee(db: Session, employee: EmployeeCreate):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee: EmployeeUpdate):
    db_employee = get_employee_by_id(db, employee_id)
    for key, value in employee.dict().items():
        setattr(db_employee, key, value)
    db_employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_employee)
    return db_employee

def soft_delete_employee(db: Session, employee_id: int):
    db_employee = get_employee_by_id(db, employee_id)
    if not db_employee.can_deleted:
        raise HTTPException(status_code=400, detail="Employee cannot be deleted")
    db_employee.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Employee soft deleted"}

def hard_delete_employee(db: Session, employee_id: int):
    db_employee = get_employee_by_id(db, employee_id)
    if not db_employee.can_deleted:
        raise HTTPException(status_code=400, detail="Employee cannot be deleted")
    db.delete(db_employee)
    db.commit()
    return {"message": "Employee permanently deleted"}

def restore_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.deleted_at = None
    db.commit()
    return {"message": "Employee restored"}

def get_all_soft_deleted_employees(db: Session):
    return db.query(Employee).filter(Employee.deleted_at != None).all()
