# Aashray'sPA

> **One AI Brain. Four Account Identities. One Control Dashboard.**

Aashray'sPA is an AI-powered personal assistant that unifies multiple social and messaging accounts — WhatsApp (personal & business) and Instagram (personal & business) — under a single intelligent brain. Each account maintains its own distinct personality and behavioural rules while sharing a common AI core, memory layer, and administrative dashboard.

---

## Tech Stack

| Layer          | Technology                              |
| -------------- | --------------------------------------- |
| **Backend**    | FastAPI · Python 3.11+                  |
| **ORM**        | SQLAlchemy 2.0 (async-ready)            |
| **Database**   | PostgreSQL (SQLite for local dev)       |
| **Migrations** | Alembic                                 |
| **AI**         | Google Gemini 2.0 Flash                 |
| **Frontend**   | Next.js 14 · React · Tailwind CSS      |
| **Auth**       | JWT (HS256) · Fernet encryption at rest |
| **Messaging**  | WhatsApp Cloud API · Instagram Graph API|

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use SQLite for local dev)
- Node.js 18+ & npm (for the frontend — Phase 7+)
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/your-username/aashrays-pa.git
cd aashrays-pa
```

### 2. Set up the Python environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your actual values (API keys, DB URL, secrets)
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the development server

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

---

## Project Structure

```
aashrays-pa/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Pydantic settings & env loading
│   │   ├── api/                 # Route handlers (versioned)
│   │   │   └── v1/
│   │   ├── core/                # Security, auth, middleware
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic layer
│   │   ├── repositories/        # Data-access layer
│   │   └── utils/               # Shared helpers & utilities
│   ├── alembic/                 # Database migration scripts
│   ├── tests/                   # Pytest test suite
│   └── requirements.txt         # Python dependencies
├── frontend/                    # Next.js dashboard (Phase 7+)
├── .env.example                 # Environment variable template
├── .gitignore
└── README.md
```

---

## Development Phases

| Phase | Description                                      | Status         |
| ----- | ------------------------------------------------ | -------------- |
| **1** | **Foundation & Core Backend Setup**              | 🔧 In Progress |
| 2     | Account Identity & Personality System            | ⏳ Planned      |
| 3     | AI Brain Integration (Gemini)                    | ⏳ Planned      |
| 4     | WhatsApp Cloud API Integration                   | ⏳ Planned      |
| 5     | Instagram API Integration                        | ⏳ Planned      |
| 6     | Memory & Context Management                      | ⏳ Planned      |
| 7     | Admin Dashboard (Next.js)                        | ⏳ Planned      |
| 8     | Advanced Features (scheduling, analytics, media) | ⏳ Planned      |
| 9     | Production Hardening & Deployment                | ⏳ Planned      |

---

## License

This project is proprietary. All rights reserved.

---

<p align="center">Built with ❤️ by Aashray</p>
