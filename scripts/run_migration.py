"""Supabase Migration 실행 스크립트.

이 스크립트는 로컬 migration 파일을 Supabase에 적용합니다.

사용법:
    python scripts/run_migration.py <migration_number>

예시:
    python scripts/run_migration.py 003
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from src.config import get_supabase_url, get_supabase_key


def read_migration_file(migration_number: str) -> str:
    """Read migration SQL file.

    Args:
        migration_number: Migration file number (e.g., "003")

    Returns:
        SQL content as string
    """
    migrations_dir = Path(__file__).parent.parent / "migrations"
    migration_file = migrations_dir / f"{migration_number}_add_subcategory_summary_fields.sql"

    if not migration_file.exists():
        # Try other naming patterns
        for sql_file in migrations_dir.glob(f"{migration_number}_*.sql"):
            migration_file = sql_file
            break

    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_number}_*.sql")

    return migration_file.read_text(encoding="utf-8")


def execute_migration(sql: str, dry_run: bool = False) -> bool:
    """Execute migration SQL on Supabase.

    Args:
        sql: SQL content to execute
        dry_run: If True, print SQL without executing

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        print("=== Dry Run Mode ===")
        print("SQL to be executed:")
        print(sql)
        print("=== End of Dry Run ===")
        return True

    try:
        client = create_client(get_supabase_url(), get_supabase_key())

        # Note: Supabase Python client doesn't support arbitrary SQL execution directly
        # You need to use PostgreSQL client or Supabase CLI instead
        print("⚠️  Warning: Python Supabase client cannot execute arbitrary SQL.")
        print("Please use one of these methods:")
        print("  1. Supabase Dashboard: https://app.supabase.com/sql")
        print("  2. Supabase CLI: supabase db push")
        print("  3. psql: psql -h <host> -U <user> -d <database> -f migrations/003_*.sql")
        print("\nSQL content:")
        print(sql)

        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_number> [--dry-run]")
        print("\nAvailable migrations:")
        migrations_dir = Path(__file__).parent.parent / "migrations"
        for sql_file in sorted(migrations_dir.glob("*.sql")):
            print(f"  - {sql_file.name}")
        sys.exit(1)

    migration_number = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    try:
        sql = read_migration_file(migration_number)
        print(f"Loaded migration: {migration_number}")
        print(f"SQL length: {len(sql)} characters")

        if execute_migration(sql, dry_run):
            print(f"✅ Migration {migration_number} completed successfully!")
        else:
            print(f"⚠️  Migration {migration_number} needs manual execution.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
