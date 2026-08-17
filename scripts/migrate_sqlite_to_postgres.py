"""Copy the existing local PusulamNet SQLite data to an empty PostgreSQL database.

Run this once from the project folder after creating the Supabase database.
The script preserves primary keys and all relationships, including accounts,
exam types, exams, notes, and study tasks.
"""

from __future__ import annotations

import argparse
import os
import sys

from sqlalchemy import create_engine, func, select, text

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import normalize_database_url
from app.database import Base
import app.models  # noqa: F401 - registers every table with Base.metadata


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default="sqlite:///./pusulamnet.db",
        help="SQLite source URL (default: sqlite:///./pusulamnet.db)",
    )
    parser.add_argument(
        "--target",
        default=os.getenv("DATABASE_URL"),
        help="PostgreSQL target URL. Defaults to the DATABASE_URL environment variable.",
    )
    return parser.parse_args()


def ensure_target_is_empty(target_engine) -> None:
    populated_tables = []
    with target_engine.connect() as connection:
        for table in Base.metadata.sorted_tables:
            if connection.scalar(select(func.count()).select_from(table)):
                populated_tables.append(table.name)

    if populated_tables:
        names = ", ".join(populated_tables)
        raise RuntimeError(
            "Hedef veritabanı boş değil. Verileri yanlışlıkla çoğaltmamak için "
            f"işlem durduruldu: {names}"
        )


def reset_postgres_sequences(connection) -> None:
    for table in Base.metadata.sorted_tables:
        if "id" not in table.c:
            continue
        table_name = table.name
        connection.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
                f"COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table_name}"
            )
        )


def repair_orphaned_course_result_rows(source_connection, rows: list[dict]) -> int:
    """Map legacy course-result IDs to the current course structure in memory.

    Early SQLite versions did not enforce foreign keys when an exam type was
    edited.  A historical result can therefore point to a deleted course ID.
    The old and current course lists retain their display order, so the rows can
    be recovered without changing the local source database.
    """
    course_table = Base.metadata.tables["courses"]
    exam_table = Base.metadata.tables["practice_exams"]
    course_rows = [dict(row) for row in source_connection.execute(select(course_table)).mappings()]
    exam_rows = [dict(row) for row in source_connection.execute(select(exam_table)).mappings()]

    course_ids = {row["id"] for row in course_rows}
    exam_type_by_exam_id = {row["id"]: row["exam_type_id"] for row in exam_rows}
    orphan_ids_by_exam_type: dict[int, set[int]] = {}

    for row in rows:
        if row["course_id"] not in course_ids:
            exam_type_id = exam_type_by_exam_id.get(row["practice_exam_id"])
            if exam_type_id is None:
                raise RuntimeError(f"Deneme #{row['practice_exam_id']} için sınav türü bulunamadı.")
            orphan_ids_by_exam_type.setdefault(exam_type_id, set()).add(row["course_id"])

    replacement_ids: dict[int, int] = {}
    for exam_type_id, orphan_ids in orphan_ids_by_exam_type.items():
        current_course_ids = [
            row["id"]
            for row in sorted(
                (row for row in course_rows if row["exam_type_id"] == exam_type_id),
                key=lambda row: (row["display_order"], row["id"]),
            )
        ]
        old_ids = sorted(orphan_ids)
        if len(old_ids) > len(current_course_ids):
            raise RuntimeError(
                f"Sınav türü #{exam_type_id} için eski ders sonuçları güvenle eşlenemedi."
            )
        replacement_ids.update(dict(zip(old_ids, current_course_ids)))

    repaired_count = 0
    for row in rows:
        replacement_id = replacement_ids.get(row["course_id"])
        if replacement_id is not None:
            row["course_id"] = replacement_id
            repaired_count += 1
    return repaired_count


def migrate(source_url: str, target_url: str) -> None:
    if not source_url.startswith("sqlite"):
        raise ValueError("Kaynak veritabanı SQLite olmalıdır.")

    target_url = normalize_database_url(target_url)
    if not target_url.startswith("postgresql"):
        raise ValueError("Hedef veritabanı PostgreSQL olmalıdır.")

    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url, pool_pre_ping=True)

    Base.metadata.create_all(target_engine)
    ensure_target_is_empty(target_engine)

    with source_engine.connect() as source_connection, target_engine.begin() as target_connection:
        for table in Base.metadata.sorted_tables:
            rows = [dict(row) for row in source_connection.execute(select(table)).mappings()]
            repaired_count = 0
            if table.name == "course_results":
                repaired_count = repair_orphaned_course_result_rows(source_connection, rows)
            if rows:
                target_connection.execute(table.insert(), rows)
            suffix = f" ({repaired_count} eski ders bağlantısı düzeltildi)" if repaired_count else ""
            print(f"{table.name}: {len(rows)} kayıt aktarıldı{suffix}")
        reset_postgres_sequences(target_connection)

    source_engine.dispose()
    target_engine.dispose()


def main() -> None:
    args = parse_arguments()
    if not args.target:
        raise SystemExit("Hedef için DATABASE_URL ayarlayın veya --target parametresini verin.")

    migrate(args.source, args.target)
    print("Aktarım tamamlandı. Eski SQLite dosyanızı yedek olarak saklayın.")


if __name__ == "__main__":
    main()
