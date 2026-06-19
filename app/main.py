from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import auth_routes, transaction_routes, insight_routes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SpendSense",
    description="Personal Finance API — transaction categorisation, spending insights, and anomaly detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(transaction_routes.router)
app.include_router(insight_routes.router)


@app.get("/")
def root():
    return {
        "app": "SpendSense",
        "version": "1.0.0",
        "docs": "/docs"
    }
