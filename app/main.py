from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

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

# Serve frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/")
def root():
    return RedirectResponse(url="/app/login.html")
