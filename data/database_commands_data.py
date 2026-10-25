import csv
import io
import json
import re
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from discord import File
from psycopg import AsyncConnection, sql

from settings import DATABASE_URL


# Keep each ZIP comfortably below Discord's standard upload limit, even when
# CSV data does not compress well. The archive itself is written to disk.
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 8 * 1024 * 1024
DATABASE_FETCH_BATCH_SIZE = 1_000


def _csv_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return f"\\x{value.hex()}"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, default=str)
    isoformat = getattr(value, "isoformat", None)
    if callable(isoformat):
        return isoformat()
    return str(value)


def _csv_record(values: tuple[object, ...] | list[object]) -> bytes:
    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\n").writerow(
        [_csv_value(value) for value in values]
    )
    return output.getvalue().encode("utf-8")


class _ArchiveBuilder:
    """Build small, independent ZIP files without buffering whole tables."""

    def __init__(self, directory: str):
        self.directory = directory
        self.archive_paths: list[str] = []
        self._archive: zipfile.ZipFile | None = None
        self._archive_uncompressed_bytes = 0
        self._member = None
        self._table_index = 0
        self._table_name = ""
        self._columns: tuple[str, ...] = ()
        self._header = b""
        self._table_part = 0

    def _start_archive(self) -> None:
        path = (
            Path(self.directory)
            / f"database_export_{len(self.archive_paths) + 1:04}.zip"
        )
        self._archive = zipfile.ZipFile(
            path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
        )
        self._archive_uncompressed_bytes = 0

    def _finish_member(self) -> None:
        if self._member is not None:
            self._member.close()
            self._member = None

    def _finish_archive(self) -> None:
        self._finish_member()
        if self._archive is not None:
            path = self._archive.filename
            self._archive.close()
            self._archive = None
            self.archive_paths.append(str(path))

    def _safe_table_name(self) -> str:
        safe_name = re.sub(r"[^\w.-]+", "_", self._table_name, flags=re.UNICODE)
        return safe_name.strip("._")[:80] or f"table_{self._table_index}"

    def _start_table_part(self) -> None:
        if len(self._header) > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise RuntimeError(
                f"Column names for table {self._table_name!r} exceed the export part size limit."
            )

        if (
            self._archive is None
            or self._archive_uncompressed_bytes + len(self._header)
            > MAX_ARCHIVE_UNCOMPRESSED_BYTES
        ):
            self._finish_archive()
            self._start_archive()

        self._table_part += 1
        member_name = (
            f"{self._table_index:04}_{self._safe_table_name()}"
            f"_part_{self._table_part:04}.csv"
        )
        self._member = self._archive.open(member_name, mode="w")
        self._member.write(self._header)
        self._archive_uncompressed_bytes += len(self._header)

    def start_table(self, table_index: int, table_name: str, columns: list[str]) -> None:
        self._finish_member()
        self._table_index = table_index
        self._table_name = table_name
        self._columns = tuple(columns)
        self._header = _csv_record(self._columns)
        self._table_part = 0
        self._start_table_part()

    def write_row(self, row: tuple[object, ...]) -> None:
        record = _csv_record(row)
        if len(record) + len(self._header) > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise RuntimeError(
                f"A row in table {self._table_name!r} exceeds the export part size limit."
            )

        if self._archive_uncompressed_bytes + len(record) > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            self._finish_member()
            self._finish_archive()
            self._start_table_part()

        self._member.write(record)
        self._archive_uncompressed_bytes += len(record)

    def finish_table(self) -> None:
        self._finish_member()

    def finish(self) -> list[str]:
        self._finish_archive()
        return self.archive_paths

    def abort(self) -> None:
        try:
            self._finish_archive()
        except Exception:
            pass


class DatabaseExport:
    """Own the generated temporary files until Discord finishes uploading them."""

    def __init__(self, directory: TemporaryDirectory[str], archive_paths: list[str]):
        self._directory = directory
        self.files: list[File] = []
        try:
            for path in archive_paths:
                self.files.append(File(fp=open(path, "rb"), filename=Path(path).name))
        except Exception:
            self.close()
            raise

    def __enter__(self) -> "DatabaseExport":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        for file in self.files:
            file.close()
        self._directory.cleanup()


async def DatabaseCommandsDownload() -> DatabaseExport:
    temporary_directory = TemporaryDirectory(prefix="database-export-")
    builder = _ArchiveBuilder(temporary_directory.name)
    try:
        async with await AsyncConnection.connect(DATABASE_URL) as conn:
            async with conn.cursor() as catalog_cursor:
                await catalog_cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                    """,
                    ("public",),
                )
                tables = [row[0] for row in await catalog_cursor.fetchall()]

            if not tables:
                raise RuntimeError("No tables or views were found in the public schema.")

            for table_index, table in enumerate(tables, start=1):
                query = sql.SQL("SELECT * FROM {}.{}").format(
                    sql.Identifier("public"), sql.Identifier(table)
                )
                async with conn.cursor(
                    name=f"database_export_{table_index}"
                ) as table_cursor:
                    table_cursor.itersize = DATABASE_FETCH_BATCH_SIZE
                    await table_cursor.execute(query)
                    columns = [column.name for column in table_cursor.description]
                    builder.start_table(table_index, table, columns)
                    async for row in table_cursor:
                        builder.write_row(row)
                    builder.finish_table()

        archive_paths = builder.finish()
        return DatabaseExport(temporary_directory, archive_paths)
    except Exception:
        builder.abort()
        temporary_directory.cleanup()
        raise
