"""
CLI script to evaluate production readiness of the environment configuration.
Usage:
    python scripts/verify_production_readiness.py
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import get_settings  # noqa: E402
from app.core.production_readiness import validate_production_configuration  # noqa: E402


def main() -> int:
    settings = get_settings()
    print("=" * 65)
    print(" 🛡️  AASHRAY'S PA — PRODUCTION READINESS AUDIT")
    print("=" * 65)
    print(f" Environment : {settings.APP_ENV}")
    print(f" App Name    : {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f" Database    : {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'sqlite'}")
    print(f" AI Provider : {settings.AI_PROVIDER} ({settings.AI_MODEL})")
    print("-" * 65)

    issues = validate_production_configuration(settings)
    errors = [i for i in issues if i.level == "ERROR"]
    warnings = [i for i in issues if i.level == "WARNING"]

    if not issues:
        print(" ✅ All production readiness checks PASSED!")
        print("    Configuration is secure and ready for deployment.")
        print("=" * 65)
        return 0

    if warnings:
        print(f"\n ⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"   [{w.field}] {w.message}")

    if errors:
        print(f"\n ❌ Critical Errors ({len(errors)}):")
        for e in errors:
            print(f"   [{e.field}] {e.message}")
        print("\n 🛑 Production startup would be BLOCKED. Fix the critical errors above.")
        print("=" * 65)
        return 1

    print("\n ✅ No critical blocking errors detected.")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
