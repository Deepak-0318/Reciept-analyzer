# models.py

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class Receipt(BaseModel):
    vendor: str
    date: datetime
    amount: float
    category: Optional[str] = None

    @validator('vendor')
    def vendor_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Vendor name cannot be empty")
        return v

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
