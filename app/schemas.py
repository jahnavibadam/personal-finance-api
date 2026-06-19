from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# --- Auth ---
class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Transactions ---
class TransactionCreate(BaseModel):
    amount: float
    description: str
    merchant: Optional[str] = None
    date: datetime
    category: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    category: str
    merchant: Optional[str]
    date: datetime
    is_recurring: bool
    is_anomaly: bool

    class Config:
        from_attributes = True


# --- Insights ---
class CategorySummary(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


class MonthlySummary(BaseModel):
    month: str
    total_spend: float
    transaction_count: int
    categories: list[CategorySummary]


class TrendPoint(BaseModel):
    week: str
    total: float
    change_pct: Optional[float] = None


class AnomalyResponse(BaseModel):
    id: int
    amount: float
    description: str
    category: str
    date: datetime
    reason: str
