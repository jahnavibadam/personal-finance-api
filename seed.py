"""Seed the database with sample transactions for testing."""
import random
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import User, Transaction
from app.auth import hash_password
from app.ml_categoriser import smart_categorise

Base.metadata.create_all(bind=engine)

SAMPLE_TRANSACTIONS = [
    (-45.50, "Tesco Groceries", "Tesco"),
    (-3.80, "Costa Coffee morning", "Costa"),
    (-12.99, "Netflix monthly", "Netflix"),
    (-750.00, "Rent payment March", None),
    (-8.50, "Uber to work", "Uber"),
    (-32.00, "Nandos dinner", "Nandos"),
    (-55.00, "Electric bill", None),
    (-9.99, "Spotify premium", "Spotify"),
    (-120.00, "Amazon order", "Amazon"),
    (-4.50, "TfL bus fare", "TfL"),
    (-28.00, "Sainsburys weekly shop", "Sainsburys"),
    (-15.00, "Cinema tickets", None),
    (-42.00, "Gym membership", None),
    (-6.20, "Starbucks latte", "Starbucks"),
    (-200.00, "Dentist checkup", None),
    (-18.50, "Deliveroo pizza", "Deliveroo"),
    (-35.00, "Petrol fill up", None),
    (-22.00, "ASOS clothing", "ASOS"),
    (2500.00, "Salary payment", None),
    (-65.00, "Restaurant birthday dinner", None),
    (-750.00, "Rent payment April", None),
    (-48.00, "Tesco big shop", "Tesco"),
    (-150.00, "Train tickets Edinburgh", None),
    (-11.99, "Disney Plus annual", "Disney"),
    (-380.00, "Unusual large Amazon order", "Amazon"),
]


def seed():
    db = SessionLocal()

    # Create test user
    existing = db.query(User).filter(User.email == "demo@spendsense.io").first()
    if existing:
        print("Demo user already exists, skipping seed.")
        db.close()
        return

    user = User(
        email="demo@spendsense.io",
        hashed_password=hash_password("demo123"),
        name="Demo User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate 3 months of transactions
    today = datetime.utcnow()
    transactions = []

    for weeks_ago in range(12):
        # Pick 5-8 random transactions per week
        num_txns = random.randint(5, 8)
        for _ in range(num_txns):
            amount, desc, merchant = random.choice(SAMPLE_TRANSACTIONS)
            # Slight amount variation
            if amount < 0:
                amount = round(amount * random.uniform(0.8, 1.3), 2)
            date = today - timedelta(weeks=weeks_ago, days=random.randint(0, 6))

            category = smart_categorise(desc, merchant)
            txn = Transaction(
                user_id=user.id,
                amount=amount,
                description=desc,
                category=category,
                merchant=merchant,
                date=date
            )
            transactions.append(txn)

    db.add_all(transactions)
    db.commit()
    print(f"Seeded {len(transactions)} transactions for demo@spendsense.io (password: demo123)")
    db.close()


if __name__ == "__main__":
    seed()
