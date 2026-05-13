import base64
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import services
from services import (
    analyze_hidden_chars,
    apply_patch,
    check_for_patches,
    clean_hidden_text,
    compare_json,
    csv_to_json_data,
    decode_jwt,
    epoch_to_local_datetime_text,
    find_binary_indices,
    json_to_csv_text,
    list_files_to_process,
    process_file_split_streaming,
    ticks_to_local_datetime_text,
)


ANOMALIES = {
    "\u200B": "Zero-Width Space",
    "\uFEFF": "BOM",
    "\u0007": "Bell",
}


class ServicesUnitTests(unittest.TestCase):
    def test_analyze_hidden_chars_reports_named_and_control_characters(self):
        text = "A\u200BB\uFEFFC\u0007D\u0001"
        findings = analyze_hidden_chars(text, ANOMALIES)

        self.assertTrue(any("Zero-Width Space" in item for item in findings))
        self.assertTrue(any("BOM" in item for item in findings))
        self.assertTrue(any("Bell" in item for item in findings))
        self.assertTrue(any("Control Character" in item for item in findings))

    def test_list_files_to_process_filters_by_csv_excel_and_no_ext(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "a.csv").write_text("x\n1\n", encoding="utf-8")
            (root / "b.CSV").write_text("x\n2\n", encoding="utf-8")
            (root / "book.xlsx").write_text("fake", encoding="utf-8")
            (root / "legacy.xls").write_text("fake", encoding="utf-8")
            (root / "plainfile").write_text("no extension", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "ignored.csv").write_text("x\n3\n", encoding="utf-8")

            csv_files = sorted(list_files_to_process(temp_dir, "CSV", ".csv"))
            excel_files = sorted(list_files_to_process(temp_dir, "EXCEL", ".xlsx"))
            no_ext_files = sorted(list_files_to_process(temp_dir, "NO EXT", ""))

            self.assertEqual(csv_files, ["a.csv", "b.CSV"])
            self.assertEqual(excel_files, ["book.xlsx", "legacy.xls"])
            self.assertEqual(no_ext_files, ["plainfile"])
            self.assertEqual(list_files_to_process(str(root / "missing"), "CSV", ".csv"), [])

    def test_find_binary_indices_returns_left_to_right_positions(self):
        self.assertEqual(find_binary_indices("010100001"), [2, 4, 9])
        self.assertEqual(find_binary_indices("0000"), [])

    def test_clean_hidden_text_removes_anomalies_and_control_chars(self):
        text = "A\u200BB\uFEFFC\u0007D"
        self.assertEqual(clean_hidden_text(text, ANOMALIES), "ABCD")

    def test_json_to_csv_text_supports_dict_and_list_inputs(self):
        csv_from_dict = json_to_csv_text({"name": "Alice", "age": 30})
        csv_from_list = json_to_csv_text([{"name": "Bob", "age": 25}])

        self.assertIn("name,age", csv_from_dict.replace("\r\n", "\n"))
        self.assertIn("Alice,30", csv_from_dict.replace("\r\n", "\n"))
        self.assertIn("Bob,25", csv_from_list.replace("\r\n", "\n"))
        self.assertEqual(json_to_csv_text("invalid"), "")

    def test_csv_to_json_data_converts_rows_and_fills_nan_as_empty(self):
        csv_text = "name,age,note\nAlice,30,\nBob,25,ok\n"
        result = csv_to_json_data(csv_text)

        self.assertEqual(
            result,
            [
                {"name": "Alice", "age": 30, "note": ""},
                {"name": "Bob", "age": 25, "note": "ok"},
            ],
        )
        self.assertEqual(csv_to_json_data("   "), [])

    def test_compare_json_reports_value_and_shape_changes(self):
        left = {"user": {"name": "Alice"}, "items": [1, 2]}
        right = {"user": {"name": "Bob"}, "items": [1], "active": True}
        diffs = compare_json(left, right)

        self.assertTrue(any("Added key: root.active" in diff for diff in diffs))
        self.assertTrue(any("List length mismatch at root.items: 2 vs 1" in diff for diff in diffs))
        self.assertTrue(any("Value mismatch at root.user.name" in diff for diff in diffs))

    def test_epoch_to_local_datetime_text_supports_seconds_and_milliseconds(self):
        seconds_text = epoch_to_local_datetime_text(1714272000)
        millis_text = epoch_to_local_datetime_text(1714272000000)

        self.assertEqual(seconds_text, millis_text)
        self.assertRegex(seconds_text, r"^2024-04-28 \d{2}:\d{2}:\d{2}$")

    def test_ticks_to_local_datetime_text_returns_expected_timestamp(self):
        result = ticks_to_local_datetime_text(638498592000000000)
        self.assertRegex(result, r"^2024-04-28 \d{2}:\d{2}:\d{2}$")

    def test_decode_jwt_decodes_payload_without_verification(self):
        header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).decode().rstrip("=")
        payload = base64.urlsafe_b64encode(json.dumps({"sub": "123", "exp": 9999999999}).encode()).decode().rstrip("=")
        token = f"{header}.{payload}.signature"

        result = decode_jwt(token)

        self.assertEqual(result["header"]["alg"], "none")
        self.assertEqual(result["payload"]["sub"], "123")
        self.assertEqual(result["signature"], "signature")

    def test_decode_jwt_rejects_invalid_shape(self):
        result = decode_jwt("not-a-jwt")
        self.assertIn("error", result)

    def test_process_file_split_streaming_splits_csv_and_preserves_header(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src"
            out_dir = root / "out"
            src_dir.mkdir()
            out_dir.mkdir()

            (src_dir / "part1.csv").write_text("id,name\n1,Alice\n2,Bob\n", encoding="utf-8-sig")
            (src_dir / "part2.csv").write_text("id,name\n3,Carol\n4,Dan\n5,Eve\n", encoding="utf-8-sig")

            status_messages = []
            result = process_file_split_streaming(
                src_dir=str(src_dir),
                files_to_process=["part1.csv", "part2.csv"],
                out_dir=str(out_dir),
                base_name="batch",
                size=2,
                has_header=True,
                src_ext_label="CSV",
                out_ext_label="CSV",
                out_ext_dot=".csv",
                status_callback=lambda message, force=False: status_messages.append((message, force)),
                cancel_check=lambda: False,
            )

            self.assertEqual(result["total_rows"], 5)
            self.assertEqual(result["files_created"], 3)
            self.assertEqual(result["errors"], [])
            self.assertTrue(any(message.startswith("Processing: part1.csv") for message, _ in status_messages))
            self.assertTrue(any(message.startswith("Created file 1") for message, _ in status_messages))

            output_files = sorted(out_dir.glob("batch_*.csv"))
            self.assertEqual([path.name for path in output_files], ["batch_1.csv", "batch_2.csv", "batch_3.csv"])

            with output_files[0].open("r", encoding="utf-8-sig", newline="") as file_obj:
                rows = list(csv.reader(file_obj))
            self.assertEqual(rows, [["id", "name"], ["1", "Alice"], ["2", "Bob"]])

            with output_files[2].open("r", encoding="utf-8-sig", newline="") as file_obj:
                rows = list(csv.reader(file_obj))
            self.assertEqual(rows, [["id", "name"], ["5", "Eve"]])

    def test_process_file_split_streaming_collects_errors_and_stops_on_cancel(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src"
            out_dir = root / "out"
            src_dir.mkdir()
            out_dir.mkdir()

            (src_dir / "good.csv").write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n", encoding="utf-8-sig")

            cancel_state = {"count": 0}

            def cancel_check():
                cancel_state["count"] += 1
                return cancel_state["count"] >= 3

            result = process_file_split_streaming(
                src_dir=str(src_dir),
                files_to_process=["good.csv", "missing.csv"],
                out_dir=str(out_dir),
                base_name="cancelled",
                size=10,
                has_header=True,
                src_ext_label="CSV",
                out_ext_label="CSV",
                out_ext_dot=".csv",
                status_callback=None,
                cancel_check=cancel_check,
            )

            self.assertLess(result["total_rows"], 3)
            self.assertEqual(result["files_created"], 0)
            self.assertEqual(result["errors"], [])
            self.assertEqual(list(out_dir.glob("cancelled_*.csv")), [])

    def test_process_file_split_streaming_reports_missing_file_errors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src_dir = root / "src"
            out_dir = root / "out"
            src_dir.mkdir()
            out_dir.mkdir()

            result = process_file_split_streaming(
                src_dir=str(src_dir),
                files_to_process=["missing.csv"],
                out_dir=str(out_dir),
                base_name="batch",
                size=10,
                has_header=True,
                src_ext_label="CSV",
                out_ext_label="CSV",
                out_ext_dot=".csv",
                status_callback=None,
                cancel_check=lambda: False,
            )

            self.assertEqual(result["total_rows"], 0)
            self.assertEqual(result["files_created"], 0)
            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("missing.csv", result["errors"][0])

    def test_check_for_patches_includes_expected_hash(self):
        class FakeResponse:
            def json(self):
                return {
                    "version": "20.0",
                    "files": {
                        "alpha.txt": {"hash": "remotehash", "size": 5},
                    },
                }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "alpha.txt").write_text("local", encoding="utf-8")

            with mock.patch.object(services.requests, "get", return_value=FakeResponse()):
                result_patches, result_version = self._run_async(
                    check_for_patches("https://example.com/manifest.json", temp_dir)
                )

            self.assertEqual(result_version, "20.0")
            self.assertEqual(result_patches[0]["rel_path"], "alpha.txt")
            self.assertEqual(result_patches[0]["hash"], "remotehash")

    def test_apply_patch_success_and_hash_validation(self):
        payload = b"patched-content"
        expected_hash = services.hashlib.sha256(payload).hexdigest()

        class FakeResponse:
            status_code = 200

            def iter_content(self, chunk_size=8192):
                yield payload

        with tempfile.TemporaryDirectory() as temp_dir:
            dest = Path(temp_dir) / "target.txt"
            dest.write_text("old-content", encoding="utf-8")

            with mock.patch.object(services.requests, "get", return_value=FakeResponse()):
                success = self._run_async(apply_patch("https://example.com/file.txt", str(dest), expected_hash))

            self.assertTrue(success)
            self.assertEqual(dest.read_bytes(), payload)
            self.assertFalse((Path(str(dest) + ".bak")).exists())

    def test_apply_patch_hash_mismatch_keeps_original_file(self):
        payload = b"patched-content"

        class FakeResponse:
            status_code = 200

            def iter_content(self, chunk_size=8192):
                yield payload

        with tempfile.TemporaryDirectory() as temp_dir:
            dest = Path(temp_dir) / "target.txt"
            dest.write_text("old-content", encoding="utf-8")

            with mock.patch.object(services.requests, "get", return_value=FakeResponse()):
                success = self._run_async(
                    apply_patch("https://example.com/file.txt", str(dest), expected_hash="not-the-real-hash")
                )

            self.assertFalse(success)
            self.assertEqual(dest.read_text(encoding="utf-8"), "old-content")
            self.assertFalse((Path(str(dest) + ".bak")).exists())

    @staticmethod
    def _run_async(awaitable):
        import asyncio

        return asyncio.run(awaitable)


if __name__ == "__main__":
    unittest.main()
