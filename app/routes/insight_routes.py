from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User
from app.schemas import MonthlySummary, TrendPoint, AnomalyResponse
from app.auth import get_current_user
from app.insights import get_monthly_summary, get_weekly_trends, detect_anomalies

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/summary", response_model=MonthlySummary)
def monthly_summary(
    year: int = Query(default=None),
    month: int = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    now = datetime.utcnow()
    y = year or now.year
    m = month or now.month
    return get_monthly_summary(db, user.id, y, m)


@router.get("/trends", response_model=list[TrendPoint])
def weekly_trends(
    weeks: int = Query(default=8, le=52),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return get_weekly_trends(db, user.id, weeks)


@router.get("/anomalies", response_model=list[AnomalyResponse])
def anomalies(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return detect_anomalies(db, user.id)
