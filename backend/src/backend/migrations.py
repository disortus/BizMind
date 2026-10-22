from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from backend.database import Base, engine
import backend.models.models  # Ensure all models are registered in Base.metadata


def run_auto_migrations(db_engine: Engine = engine):
    """
    Ensures all tables and newly added columns exist in the database without dropping data.
    Inspects sqlite tables, creates missing tables, applies ALTER TABLE ADD COLUMN for missing fields,
    and backfills defaults.
    """
    # 1. Create any completely new tables
    Base.metadata.create_all(bind=db_engine)

    # 2. Check existing tables for newly introduced columns
    inspector = inspect(db_engine)
    existing_tables = inspector.get_table_names()

    with db_engine.connect() as conn:
        for table_name, table in Base.metadata.tables.items():
            if table_name not in existing_tables:
                continue

            existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
            for col in table.columns:
                if col.name not in existing_columns:
                    # Determine SQLite-compatible column type
                    type_repr = str(col.type).upper()
                    if "BOOL" in type_repr:
                        col_type_str = "BOOLEAN"
                    elif "INT" in type_repr:
                        col_type_str = "INTEGER"
                    elif "FLOAT" in type_repr or "NUMERIC" in type_repr or "DECIMAL" in type_repr:
                        col_type_str = "REAL"
                    elif "DATE" in type_repr:
                        col_type_str = "DATE"
                    else:
                        col_type_str = "TEXT"

                    # Add default if defined
                    default_clause = ""
                    if col.default is not None and hasattr(col.default, "arg"):
                        arg = col.default.arg
                        if isinstance(arg, bool):
                            default_clause = f" DEFAULT {1 if arg else 0}"
                        elif isinstance(arg, (int, float)):
                            default_clause = f" DEFAULT {arg}"
                        elif isinstance(arg, str):
                            default_clause = f" DEFAULT '{arg}'"

                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type_str}{default_clause}"
                    try:
                        conn.execute(text(alter_sql))
                        conn.commit()
                    except Exception:
                        pass

        # 3. Backfill defaults for any NULL rows
        backfill_statements = [
            "UPDATE financial_transactions SET is_archived = 0 WHERE is_archived IS NULL;",
            "UPDATE products SET is_active = 1 WHERE is_active IS NULL;",
            "UPDATE products SET unit_ratio = 1.0 WHERE unit_ratio IS NULL;",
            "UPDATE suppliers SET is_active = 1 WHERE is_active IS NULL;",
            "UPDATE supplier_offers SET is_active = 1 WHERE is_active IS NULL;",
            "UPDATE users SET is_active = 1 WHERE is_active IS NULL;",
            "UPDATE users SET role = 'manager' WHERE role IS NULL;",
            "UPDATE organizations SET currency = '₸' WHERE currency IS NULL;",
            "UPDATE organizations SET alert_threshold_percent = 5.0 WHERE alert_threshold_percent IS NULL;",
        ]
        for stmt in backfill_statements:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass
