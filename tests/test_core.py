"""Unit tests for c_string_escape_decoder.core.decode."""

import unittest

from c_string_escape_decoder import decode


class DecodeSimpleEscapesTests(unittest.TestCase):
    def test_simple_escapes(self):
        self.assertEqual(decode(r"\n\t\r\a\b\f\v"), "\n\t\r\a\b\f\v")

    def test_quote_and_backslash_escapes(self):
        self.assertEqual(decode(r"\'\"\\\?"), "'\"\\?")

    def test_nul_escape(self):
        self.assertEqual(decode(r"\0"), "\x00")


class DecodeHexTests(unittest.TestCase):
    def test_two_digit_hex(self):
        self.assertEqual(decode(r"\x41\x42"), "AB")

    def test_uppercase_hex(self):
        self.assertEqual(decode(r"\x4A"), "J")

    def test_lowercase_hex(self):
        self.assertEqual(decode(r"\x6a"), "j")

    def test_incomplete_hex_emits_backslash(self):
        # ``\x1`` is not two hex digits, so we keep the backslash and let the
        # 'x' and '1' pass through as ordinary characters.
        self.assertEqual(decode(r"\x1"), "\\x1")


class DecodeOctalTests(unittest.TestCase):
    def test_three_digit_octal(self):
        self.assertEqual(decode(r"\101\102"), "AB")

    def test_short_octal(self):
        self.assertEqual(decode(r"\41\42"), "!\"")

    def test_single_octal_digit(self):
        self.assertEqual(decode(r"\1"), "\x01")

    def test_octal_stops_at_three_digits(self):
        self.assertEqual(decode(r"\1234"), "S4")

    def test_octal_stops_at_non_octal(self):
        self.assertEqual(decode(r"\12x"), "\nx")


class DecodeUnknownTests(unittest.TestCase):
    def test_unknown_escape_kept_literally(self):
        self.assertEqual(decode(r"\g"), "\\g")

    def test_plain_text_passes_through(self):
        self.assertEqual(decode("hello world"), "hello world")

    def test_trailing_backslash_is_kept(self):
        self.assertEqual(decode("abc\\"), "abc\\")

    def test_mixed_content(self):
        self.assertEqual(decode(r"line1\nline2\t\x41\101"), "line1\nline2\tAA")


if __name__ == "__main__":
    unittest.main()
