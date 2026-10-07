import sqlite3
import getpass
import psycopg2


SQLITE_DB = "save_data.db"


def get_postgres_url():
    print("Paste your Render PostgreSQL External Database URL.")
    print("The password will not be displayed while typing.")
    return getpass.getpass("PostgreSQL URL: ")


def sqlite_type_to_postgres(sqlite_type):
    sqlite_type = sqlite_type.upper()

    if "INT" in sqlite_type:
        return "INTEGER"

    if "REAL" in sqlite_type or "FLOA" in sqlite_type or "DOUB" in sqlite_type:
        return "DOUBLE PRECISION"

    return "TEXT"


def migrate():
    postgres_url = get_postgres_url()

    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row

    postgres_conn = psycopg2.connect(postgres_url)

    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()

    tables = [
        "articles",
        "users",
        "cve_details",
        "recommendations"
    ]

    try:

        # ==========================================
        # CREATE TABLES
        # ==========================================

        for table in tables:

            columns = sqlite_cursor.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()

            column_definitions = []

            for column in columns:

                column_id = column[0]
                column_name = column[1]
                column_type = column[2]
                not_null = column[3]
                default_value = column[4]
                primary_key = column[5]

                pg_type = sqlite_type_to_postgres(column_type)

                definition = f'"{column_name}" {pg_type}'

                if primary_key:
                    definition += " PRIMARY KEY"

                if not_null and not primary_key:
                    definition += " NOT NULL"

                if default_value is not None:

                    default_value = str(default_value)

                    if default_value.upper() == "CURRENT_TIMESTAMP":
                        definition += " DEFAULT CURRENT_TIMESTAMP"

                    elif (
                        default_value.isdigit()
                        or default_value.replace(".", "", 1).isdigit()
                    ):
                        definition += f" DEFAULT {default_value}"

                    elif default_value.startswith("'") and default_value.endswith("'"):
                        definition += f" DEFAULT {default_value}"

                column_definitions.append(definition)

            create_sql = f"""
                CREATE TABLE IF NOT EXISTS "{table}" (
                    {", ".join(column_definitions)}
                )
            """

            postgres_cursor.execute(create_sql)

        postgres_conn.commit()

        print("\nPostgreSQL tables created successfully.")

        # ==========================================
        # COPY DATA
        # ==========================================

        for table in tables:

            columns = sqlite_cursor.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()

            column_names = [column[1] for column in columns]

            rows = sqlite_cursor.execute(
                f'SELECT * FROM "{table}"'
            ).fetchall()

            print(f"\nMigrating {table}: {len(rows)} rows")

            if not rows:
                continue

            quoted_columns = ", ".join(
                f'"{column}"'
                for column in column_names
            )

            placeholders = ", ".join(
                ["%s"] * len(column_names)
            )

            insert_sql = f"""
                INSERT INTO "{table}"
                ({quoted_columns})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """

            for row in rows:
                postgres_cursor.execute(
                    insert_sql,
                    tuple(row)
                )

        postgres_conn.commit()

        # ==========================================
        # FIX ID SEQUENCES
        # ==========================================

        for table in tables:

            columns = sqlite_cursor.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()

            id_column = next(
                (column for column in columns if column[1] == "id"),
                None
            )

            if id_column:

                postgres_cursor.execute(
                    f"""
                    SELECT setval(
                        pg_get_serial_sequence(%s, 'id'),
                        COALESCE(MAX(id), 1),
                        MAX(id) IS NOT NULL
                    )
                    FROM "{table}"
                    """,
                    (table,)
                )

        postgres_conn.commit()

        print("\n==========================================")
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("==========================================")

        # ==========================================
        # VERIFY COUNTS
        # ==========================================

        for table in tables:

            sqlite_count = sqlite_cursor.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            postgres_cursor.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            )

            postgres_count = postgres_cursor.fetchone()[0]

            print(
                f"{table}: "
                f"SQLite={sqlite_count}, "
                f"PostgreSQL={postgres_count}"
            )

    except Exception as error:

        postgres_conn.rollback()

        print("\nMIGRATION FAILED")
        print(error)

    finally:

        sqlite_conn.close()
        postgres_conn.close()


if __name__ == "__main__":
    migrate()