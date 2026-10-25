from io import BytesIO

import pandas as pd
from discord import File
from psycopg import AsyncConnection, sql

from settings import DATABASE_URL


def _unique_sheet_name(table: str, used_names: set[str]) -> str:
    invalid_characters = set("[]:*?/\\")
    base_name = "".join(
        "_" if character in invalid_characters else character for character in table
    )[:31]
    if not base_name:
        base_name = "Table"

    name = base_name
    suffix_number = 2
    while name.casefold() in used_names:
        suffix = f"_{suffix_number}"
        name = f"{base_name[:31 - len(suffix)]}{suffix}"
        suffix_number += 1

    used_names.add(name.casefold())
    return name


async def DatabaseCommandsDownload():
    async with (
        await AsyncConnection.connect(DATABASE_URL) as conn,
        conn.cursor() as cur,
    ):
        await cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name
            """,
            ("public",),
        )
        tables = [row[0] for row in await cur.fetchall()]
        if not tables:
            raise RuntimeError("No tables or views were found in the public schema.")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            used_sheet_names: set[str] = set()
            for table in tables:
                query = sql.SQL("SELECT * FROM {}.{}").format(
                    sql.Identifier("public"), sql.Identifier(table)
                )
                await cur.execute(query)
                columns = [column.name for column in cur.description]
                rows = await cur.fetchall()
                df = pd.DataFrame(rows, columns=columns)
                sheet_name = _unique_sheet_name(table, used_sheet_names)
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)
        file = File(fp=output, filename="database_export.xlsx")

        return file
