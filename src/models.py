from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True)
    site = Column(String)
    response_time = Column(Float)
    status_code = Column(Integer)
    error = Column(String)
    created_at = Column(DateTime, default=datetime.now)