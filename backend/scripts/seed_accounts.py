"""
Database seeder script to initialize the 4 core accounts for Aashray'sPA.

Usage:
    python scripts/seed_accounts.py
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal  # noqa: E402
from app.services.account_service import AccountService  # noqa: E402


def seed() -> None:
    """Run seeding of the four accounts."""
    db = SessionLocal()
    try:
        service = AccountService(db)
        created = service.seed_default_accounts()
        if created:
            print(f"✅ Successfully seeded {len(created)} new account(s):")
            for acc in created:
                print(f"  - [{acc.platform.upper()}:{acc.account_type.upper()}] {acc.display_name} (ID: {acc.id})")
        else:
            print("ℹ️ All 4 default accounts already exist in the database.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
