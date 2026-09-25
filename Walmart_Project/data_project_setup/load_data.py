import argparse
import csv
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "walmart_dataset" / "data"

TABLES = {
    "customers": [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "city",
        "province",
        "country",
        "created_timestamp",
        "updated_timestamp",
        "is_active",
    ],
    "employees": [
        "employee_id",
        "store_id",
        "first_name",
        "last_name",
        "email",
        "job_title",
        "salary",
        "created_timestamp",
        "updated_timestamp",
        "is_active",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "store_id",
        "order_timestamp",
        "payment_method",
        "order_status",
        "total_amount",
        "created_timestamp",
        "updated_timestamp",
        "is_active",
    ],
    "order_items": [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "line_amount",
        "created_timestamp",
        "updated_timestamp",
        "is_active",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "brand",
        "price",
        "created_timestamp",
        "updated_timestamp",
        "is_active",
    ],
    "stores": [
        "store_id",
        "store_name",
        "city",
        "province",
        "country",
        "created_timestamp",
        "updated_timestamp",
        "is_active",
    ],
}


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def validate_csv_headers(table_name: str, csv_path: Path, columns: list[str]) -> None:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        headers = next(csv.reader(csv_file), [])
    if headers != columns:
        raise ValueError(
            f"{csv_path.name} headers do not match raw.{table_name}: "
            f"expected {columns}, got {headers}"
        )


def load_table(cursor, table_name: str, columns: list[str]) -> int:
    csv_path = DATA_DIR / f"{table_name}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV file: {csv_path}")
    validate_csv_headers(table_name, csv_path, columns)
    copy_statement = sql.SQL(
        "COPY {} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
    ).format(
        sql.Identifier("raw", table_name),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        cursor.copy_expert(copy_statement.as_string(cursor), csv_file)
    return cursor.rowcount


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load Walmart CSV files into raw tables."
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate the raw tables before loading the CSV files.",
    )
    args = parser.parse_args()
    load_dotenv(BASE_DIR / ".env")
    database_url = os.environ.get("DATABASE_URL_UNPOOLED") or os.environ.get(
        "DATABASE_URL"
    )
    if not database_url:
        raise RuntimeError("DATABASE_URL or DATABASE_URL_UNPOOLED is not configured")

    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            if args.replace:
                table_names = ", ".join(
                    f'"raw"."{table_name}"' for table_name in TABLES
                )
                cursor.execute(f"TRUNCATE TABLE {table_names}")
            for table_name, columns in TABLES.items():
                row_count = load_table(cursor, table_name, columns)
                print(f"Loaded {row_count:,} rows into raw.{table_name}")

            print("Verified row counts:")
            for table_name in TABLES:
                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier("raw", table_name)
                    )
                )
                print(f"  raw.{table_name}: {cursor.fetchone()[0]:,}")


if __name__ == "__main__":
    main()
