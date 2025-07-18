from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    event_name = Column(String)
    cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    receipt_url = Column(String, nullable=True)
    name = Column(String, nullable=True)
    role = Column(String, nullable=True)
