import unittest

from text_delimiter_tool.formatter import FormatOptions, format_lines


class FormatterTests(unittest.TestCase):
    def test_formats_multiple_lines_with_commas_between_items(self) -> None:
        result = format_lines(
            "1\n2\n3",
            FormatOptions(prefix="", suffix="", delimiter=",", trailing_delimiter=False),
        )

        self.assertEqual(result, "1,\n2,\n3")

    def test_trims_whitespace_and_skips_blank_lines(self) -> None:
        result = format_lines(
            "  1  \n\n   2\n  \n3  ",
            FormatOptions(prefix="'", suffix="'", delimiter=",", trailing_delimiter=False),
        )

        self.assertEqual(result, "'1',\n'2',\n'3'")

    def test_adds_delimiter_to_every_line_when_enabled(self) -> None:
        result = format_lines(
            "1\n2\n3",
            FormatOptions(prefix="'", suffix="'", delimiter=",", trailing_delimiter=True),
        )

        self.assertEqual(result, "'1',\n'2',\n'3',")

    def test_returns_empty_string_for_empty_input(self) -> None:
        result = format_lines(
            "\n  \n",
            FormatOptions(prefix="", suffix="", delimiter=",", trailing_delimiter=False),
        )

        self.assertEqual(result, "")

    def test_allows_empty_prefix_suffix_and_delimiter(self) -> None:
        result = format_lines(
            "a\nb",
            FormatOptions(prefix="", suffix="", delimiter="", trailing_delimiter=False),
        )

        self.assertEqual(result, "a\nb")


if __name__ == "__main__":
    unittest.main()
