import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from text_delimiter_tool.version import load_app_version


class VersionTests(unittest.TestCase):
    def test_reads_first_existing_version_file_and_strips_whitespace(self) -> None:
        with TemporaryDirectory() as temp_dir:
            version_file = Path(temp_dir) / "VERSION"
            version_file.write_text("1.2.3\n", encoding="utf-8")

            result = load_app_version([Path(temp_dir) / "missing", version_file])

            self.assertEqual(result, "1.2.3")

    def test_raises_when_no_version_file_exists(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with self.assertRaises(FileNotFoundError):
                load_app_version([Path(temp_dir) / "missing"])


if __name__ == "__main__":
    unittest.main()
