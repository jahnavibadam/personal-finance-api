# SpendSense

Personal Finance API with spending insights, transaction categorisation, and anomaly detection.

## Stack

- **Backend:** Python, FastAPI, Pydantic
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Auth:** JWT (OAuth2 password flow)
- **Insights:** Statistical anomaly detection, category-based trend analysis

## Quick Start

```bash
pip install -r requirements.txt
python seed.py          # create demo user + sample data
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for interactive API docs.

## Demo Credentials

- Email: `demo@spendsense.io`
- Password: `demo123`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Get JWT token |
| POST | /transactions | Add transaction |
| POST | /transactions/bulk | Bulk add |
| GET | /transactions | List with filters |
| DELETE | /transactions/{id} | Delete |
| GET | /insights/summary | Monthly category breakdown |
| GET | /insights/trends | Week-over-week spending |
| GET | /insights/anomalies | Flag unusual transactions |

## Features

- Auto-categorisation via keyword matching (groceries, dining, transport, subscriptions, etc.)
- Monthly spend breakdown by category with percentages
- Week-over-week trend tracking with change percentages
- Anomaly detection: flags transactions > 2σ above category average
- JWT auth with bcrypt password hashing
- CORS enabled for frontend integration
