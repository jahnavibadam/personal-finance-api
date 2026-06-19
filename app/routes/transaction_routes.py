from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models import User, Transaction
from app.schemas import TransactionCreate, TransactionResponse
from app.auth import get_current_user
from app.ml_categoriser import smart_categorise

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    txn: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    category = txn.category or smart_categorise(txn.description, txn.merchant)

    transaction = Transaction(
        user_id=user.id,
        amount=txn.amount,
        description=txn.description,
        category=category,
        merchant=txn.merchant,
        date=txn.date
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.post("/bulk", response_model=list[TransactionResponse], status_code=201)
def bulk_create(
    txns: list[TransactionCreate],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    results = []
    for txn in txns:
        category = txn.category or smart_categorise(txn.description, txn.merchant)
        transaction = Transaction(
            user_id=user.id,
            amount=txn.amount,
            description=txn.description,
            category=category,
            merchant=txn.merchant,
            date=txn.date
        )
        db.add(transaction)
        results.append(transaction)

    db.commit()
    for t in results:
        db.refresh(t)
    return results


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Transaction).filter(Transaction.user_id == user.id)

    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    return query.order_by(Transaction.date.desc()).limit(limit).all()


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()
