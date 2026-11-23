import csv
import tempfile
import unittest
from pathlib import Path

import database.questions as questions


class ExportWrongQuestionsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.csv_path = Path(self.temp_dir.name) / "wrong.csv"
        self.original_db_path = questions.DATABASE_PATH
        questions.DATABASE_PATH = self.db_path

    def tearDown(self):
        questions.DATABASE_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def read_rows(self):
        with self.csv_path.open(encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def test_export_preserves_chinese_and_csv_columns(self):
        questions.add_wrong("中文题目", "答案B", "复习说明")
        result = questions.export_wrong(self.csv_path)
        rows = self.read_rows()
        self.assertEqual(Path(result), self.csv_path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["题目"], "中文题目")
        self.assertEqual(rows[0]["答案/记录"], "答案B")
        self.assertEqual(rows[0]["笔记"], "复习说明")

    def test_empty_database_exports_headers(self):
        questions.export_wrong(self.csv_path)
        with self.csv_path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            self.assertEqual(next(reader), ["编号", "题目", "答案/记录", "笔记", "记录时间（UTC）"])
            self.assertEqual(list(reader), [])

    def test_formula_prefix_is_escaped_even_after_whitespace(self):
        self.assertEqual(questions._spreadsheet_safe("  =1+1"), "'  =1+1")
        questions.add_wrong("=1+1", "+danger", "@text")
        questions.export_wrong(self.csv_path)
        row = self.read_rows()[0]
        self.assertEqual(row["题目"], "'=1+1")
        self.assertEqual(row["答案/记录"], "'+danger")
        self.assertEqual(row["笔记"], "'@text")


if __name__ == "__main__":
    unittest.main()
