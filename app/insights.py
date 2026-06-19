"""
Insights engine — computes spending summaries, trends, and anomalies.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from collections import defaultdict

from app.models import Transaction
from app.schemas import CategorySummary, MonthlySummary, TrendPoint, AnomalyResponse


def get_monthly_summary(db: Session, user_id: int, year: int, month: int) -> MonthlySummary:
    """Get spending breakdown by category for a given month."""
    txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        extract("year", Transaction.date) == year,
        extract("month", Transaction.date) == month,
        Transaction.amount < 0  # only expenses
    ).all()

    category_totals = defaultdict(lambda: {"total": 0.0, "count": 0})
    for txn in txns:
        category_totals[txn.category]["total"] += abs(txn.amount)
        category_totals[txn.category]["count"] += 1

    total_spend = sum(v["total"] for v in category_totals.values())

    categories = [
        CategorySummary(
            category=cat,
            total=round(data["total"], 2),
            count=data["count"],
            percentage=round((data["total"] / total_spend * 100) if total_spend > 0 else 0, 1)
        )
        for cat, data in sorted(category_totals.items(), key=lambda x: x[1]["total"], reverse=True)
    ]

    return MonthlySummary(
        month=f"{year}-{month:02d}",
        total_spend=round(total_spend, 2),
        transaction_count=len(txns),
        categories=categories
    )


def get_weekly_trends(db: Session, user_id: int, weeks: int = 8) -> list[TrendPoint]:
    """Get week-over-week spending totals."""
    today = datetime.utcnow()
    start = today - timedelta(weeks=weeks)

    txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= start,
        Transaction.amount < 0
    ).all()

    weekly = defaultdict(float)
    for txn in txns:
        week_start = txn.date - timedelta(days=txn.date.weekday())
        week_key = week_start.strftime("%Y-%m-%d")
        weekly[week_key] += abs(txn.amount)

    sorted_weeks = sorted(weekly.items())
    trends = []
    for i, (week, total) in enumerate(sorted_weeks):
        change = None
        if i > 0:
            prev = sorted_weeks[i - 1][1]
            change = round(((total - prev) / prev * 100) if prev > 0 else 0, 1)
        trends.append(TrendPoint(week=week, total=round(total, 2), change_pct=change))

    return trends


def detect_anomalies(db: Session, user_id: int) -> list[AnomalyResponse]:
    """Flag transactions that deviate significantly from category averages."""
    txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.amount < 0
    ).all()

    if not txns:
        return []

    # Compute mean and stddev per category
    category_amounts = defaultdict(list)
    for txn in txns:
        category_amounts[txn.category].append(abs(txn.amount))

    category_stats = {}
    for cat, amounts in category_amounts.items():
        mean = sum(amounts) / len(amounts)
        variance = sum((a - mean) ** 2 for a in amounts) / max(len(amounts), 1)
        stddev = variance ** 0.5
        category_stats[cat] = (mean, stddev)

    # Flag anything > mean + 2*stddev
    anomalies = []
    for txn in txns:
        mean, stddev = category_stats.get(txn.category, (0, 0))
        amount = abs(txn.amount)
        if stddev > 0 and amount > mean + 2 * stddev:
            reason = f"£{amount:.2f} is {((amount - mean) / stddev):.1f}x std dev above avg £{mean:.2f} for {txn.category}"
            anomalies.append(AnomalyResponse(
                id=txn.id,
                amount=txn.amount,
                description=txn.description,
                category=txn.category,
                date=txn.date,
                reason=reason
            ))
            # Mark in DB
            txn.is_anomaly = True

    db.commit()
    return anomalies
