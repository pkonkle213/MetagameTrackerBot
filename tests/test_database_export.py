import csv
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from data.database_commands_data import _ArchiveBuilder, _csv_record


class DatabaseExportArchiveTests(unittest.TestCase):
    def test_splits_large_tables_into_readable_bounded_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            builder = _ArchiveBuilder(directory)
            with patch("data.database_commands_data.MAX_ARCHIVE_UNCOMPRESSED_BYTES", 48):
                builder.start_table(1, "orders", ["id", "description"])
                builder.write_row((1, "a" * 20))
                builder.write_row((2, "b" * 20))
                builder.write_row((3, "c" * 20))
                builder.finish_table()
                archive_paths = builder.finish()

            self.assertGreater(len(archive_paths), 1)
            exported_rows = []
            for archive_path in archive_paths:
                with zipfile.ZipFile(archive_path) as archive:
                    self.assertLessEqual(
                        sum(member.file_size for member in archive.infolist()), 48
                    )
                    self.assertEqual(len(archive.namelist()), 1)
                    with archive.open(archive.namelist()[0]) as csv_file:
                        exported_rows.extend(
                            csv.reader(line.decode("utf-8") for line in csv_file)
                        )

            self.assertEqual(
                exported_rows,
                [
                    ["id", "description"],
                    ["1", "a" * 20],
                    ["id", "description"],
                    ["2", "b" * 20],
                    ["id", "description"],
                    ["3", "c" * 20],
                ],
            )

    def test_csv_values_preserve_json_and_escape_csv_fields(self):
        record = _csv_record(({"active": True}, "line one\nline two", None))
        self.assertEqual(
            list(csv.reader([record.decode("utf-8")])),
            [['{"active": true}', "line one\nline two", ""]],
        )

    def test_oversized_row_fails_instead_of_creating_an_oversized_part(self):
        with tempfile.TemporaryDirectory() as directory:
            builder = _ArchiveBuilder(directory)
            with patch("data.database_commands_data.MAX_ARCHIVE_UNCOMPRESSED_BYTES", 24):
                builder.start_table(1, "orders", ["id", "description"])
                with self.assertRaisesRegex(RuntimeError, "exceeds the export part size"):
                    builder.write_row((1, "x" * 30))
                builder.abort()


if __name__ == "__main__":
    unittest.main()
