import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from custom_errors import KnownError
from data.inventory_data import ReplaceInventory
from services.inventory_service import ParseInventoryCSV, SyncInventoryFromLatestFile
from services.object_storage_service import get_latest_file_bytes


class InventoryCsvTests(unittest.TestCase):
    def test_parses_headers_with_spaces_and_ignores_blank_rows(self):
        content = (
            "\ufeffQuantity,Card Name,Card Edition\n"
            "2,Sol Ring,CMR\n"
            ",,\n"
            "1,Island,DMU\n"
        ).encode("utf-8")

        self.assertEqual(
            ParseInventoryCSV(content),
            [(2, "Sol Ring", "CMR"), (1, "Island", "DMU")],
        )

    def test_accepts_common_header_aliases(self):
        content = b"qty,name,set\n3,Forest,MKM\n"

        self.assertEqual(ParseInventoryCSV(content), [(3, "Forest", "MKM")])

    def test_rejects_invalid_rows_and_empty_imports(self):
        with self.assertRaises(KnownError):
            ParseInventoryCSV(b"Quantity,Card Name,Card Edition\n-1,Card,SET\n")
        with self.assertRaises(KnownError):
            ParseInventoryCSV(b"Quantity,Card Name,Card Edition\n")

    def test_rejects_extra_csv_fields(self):
        with self.assertRaises(KnownError):
            ParseInventoryCSV(
                b"Quantity,Card Name,Card Edition\n1,Card,SET,unexpected\n"
            )


class InventoryDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_replaces_rows_in_a_single_committed_transaction(self):
        connection = AsyncMock()
        connection.__aenter__.return_value = connection
        cursor = AsyncMock()
        cursor.__aenter__.return_value = cursor
        connection.cursor = Mock(return_value=cursor)
        rows = [(2, "Sol Ring", "CMR")]

        with patch(
            "data.inventory_data.AsyncConnection.connect",
            new=AsyncMock(return_value=connection),
        ):
            count = await ReplaceInventory(rows)

        self.assertEqual(count, 1)
        self.assertEqual(cursor.executemany.await_args.args[1], rows)
        self.assertTrue(
            any("DELETE FROM inventory" in call.args[0] for call in cursor.execute.await_args_list)
        )
        connection.commit.assert_awaited_once()

    async def test_sync_uses_latest_csv_file_and_replaces_with_its_rows(self):
        csv_content = b"Quantity,Card Name,Card Edition\n1,Island,DMU\n"
        with (
            patch(
                "services.inventory_service.get_latest_file_bytes",
                return_value=("Inventory Files/current.csv", csv_content),
            ),
            patch(
                "services.inventory_service.ReplaceInventory",
                new=AsyncMock(return_value=1),
            ) as replace_inventory,
        ):
            result = await SyncInventoryFromLatestFile()

        self.assertEqual(result, ("Inventory Files/current.csv", 1))
        replace_inventory.assert_awaited_once_with([(1, "Island", "DMU")])


class ObjectStorageLatestFileTests(unittest.TestCase):
    def test_selects_latest_updated_csv_within_prefix(self):
        older = SimpleNamespace(
            name="Inventory Files/old.csv",
            updated=datetime(2025, 1, 1, tzinfo=timezone.utc),
            download_as_bytes=Mock(return_value=b"old"),
        )
        newer = SimpleNamespace(
            name="Inventory Files/new.csv",
            updated=datetime(2025, 2, 1, tzinfo=timezone.utc),
            download_as_bytes=Mock(return_value=b"new"),
        )
        ignored = SimpleNamespace(
            name="Inventory Files/notes.txt",
            updated=datetime(2025, 3, 1, tzinfo=timezone.utc),
            download_as_bytes=Mock(return_value=b"ignored"),
        )
        client = Mock()
        client._Client__bucket.return_value.list_blobs.return_value = [
            older,
            newer,
            ignored,
        ]

        with patch(
            "services.object_storage_service.get_client", return_value=client
        ):
            result = get_latest_file_bytes("Inventory Files/", ".csv")

        self.assertEqual(result, ("Inventory Files/new.csv", b"new"))


if __name__ == "__main__":
    unittest.main()
