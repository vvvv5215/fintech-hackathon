from fastapi import FastAPI, Depends, HTTPException, Query, Path, Body, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, Expense
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExpenseCreate(BaseModel):
    user_email: str
    event_name: str
    cost: float
    name: str
    role: str

class ExpenseRead(BaseModel):
    id: int
    user_email: str
    event_name: str
    cost: float
    timestamp: datetime
    receipt_url: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    class Config:
        orm_mode = True

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI backend!"}

@app.post("/expenses", response_model=ExpenseRead)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.get("/expenses", response_model=List[ExpenseRead])
def list_expenses(user_email: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Expense).filter(Expense.user_email == user_email).order_by(Expense.timestamp.desc()).all()

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"ok": True}

@app.delete("/expenses/by_user/{user_email}")
def delete_expenses_by_user(user_email: str, db: Session = Depends(get_db)):
    db.query(Expense).filter(Expense.user_email == user_email).delete()
    db.commit()
    return {"ok": True}

@app.get("/expenses/all", response_model=List[ExpenseRead])
def list_all_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).order_by(Expense.timestamp.desc()).all()

@app.patch("/expenses/{expense_id}/receipt", response_model=ExpenseRead)
def update_receipt_url(expense_id: int, receipt_url: str = Body(...), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.receipt_url = receipt_url
    db.commit()
    db.refresh(expense)
    return expense

@app.post("/role_change")
def role_change(payload: dict = Body(...), db: Session = Depends(get_db)):
    user_email = payload.get('user_email')
    name = payload.get('name')
    role = payload.get('role')
    if not user_email or not role:
        raise HTTPException(status_code=400, detail="user_email and role required")
    db_expense = Expense(
        user_email=user_email,
        event_name='Role Change',
        cost=0.0,
        name=name or user_email,
        role=role
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"ok": True, "id": db_expense.id}

@app.post("/become_handler")
def become_handler(payload: dict = Body(...), db: Session = Depends(get_db)):
    user_email = payload.get('user_email')
    name = payload.get('name')
    secret_code = payload.get('secret_code')
    if not user_email or not secret_code:
        raise HTTPException(status_code=400, detail="user_email and secret_code required")
    HANDLER_SECRET_CODE = os.environ.get('HANDLER_SECRET_CODE', 'iiit123')
    if secret_code != HANDLER_SECRET_CODE:
        raise HTTPException(status_code=403, detail="Invalid secret code")
    db_expense = Expense(
        user_email=user_email,
        event_name='Become Handler',
        cost=0.0,
        name=name or user_email,
        role='handler'
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"ok": True, "id": db_expense.id}

@app.get("/users_from_expenses")
def users_from_expenses(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT DISTINCT user_email as email, name, role
        FROM expenses
        WHERE user_email IS NOT NULL
    """)).fetchall()
    return [dict(row._mapping) for row in result]