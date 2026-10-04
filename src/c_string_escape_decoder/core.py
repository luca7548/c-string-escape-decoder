"""Decode C/C++ string escape sequences into raw character form."""

# Precomputed table of single-character escape sequences. Both Python and
# the C/C++ language family use this same set of simple escapes, so we can
# look them up directly. \"?\" is included because the standard treats \\? as
# a valid, if rarely useful, escape that yields a literal '?'.
_SIMPLE_ESCAPES = {
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "0": "\0",
    "'": "'",
    '"': '"',
    "\\": "\\",
    "?": "?",
}


def _hex_value(digits: str) -> str:
    """Convert up to two hex digits into a single character."""
    return chr(int(digits, 16))


def _octal_value(digits: str) -> str:
    """Convert one to three octal digits into a single character."""
    return chr(int(digits, 8))


def decode(s: str) -> str:
    """Decode the C/C++ escape sequences in *s* and return the raw text.

    Recognised sequences:

    - Simple escapes: \\a \\b \\f \\n \\r \\t \\v \\0 \\' \\" \\\\ \\?
    - Hex escapes \\xHH: the ``x`` is followed by exactly two hex digits.
      The standard permits an arbitrary run of hex digits, but that makes
      the grammar greedy in ways that are rarely useful and easy to get
      wrong, so this implementation fixes the length at two.
    - Octal escapes \\OOO: one to three octal digits following the backslash.

    A stray backslash followed by a character the standard does not define as
    an escape (for example ``\\g``) is emitted literally, backslash and all.
    This mirrors how most C compilers warn-but-keep.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue

        # Bare trailing backslash is kept as-is; there is nothing to escape.
        if i + 1 >= n:
            out.append(c)
            i += 1
            continue

        nxt = s[i + 1]

        if nxt == "x":
            # Require exactly two hex digits. This is the deliberate scope
            # noted above: it keeps parsing local and unambiguous.
            hex_digits = s[i + 2:i + 4]
            if len(hex_digits) == 2 and all(ch in "0123456789abcdefABCDEF" for ch in hex_digits):
                out.append(_hex_value(hex_digits))
                i += 4
                continue
            # Not enough hex digits: emit the backslash and let the 'x' be
            # treated as an ordinary character on the next pass.
            out.append(c)
            i += 1
            continue

        if nxt in "01234567":
            j = i + 1
            oct_digits = ""
            while j < n and len(oct_digits) < 3 and s[j] in "01234567":
                oct_digits += s[j]
                j += 1
            out.append(_octal_value(oct_digits))
            i = j
            continue

        if nxt in _SIMPLE_ESCAPES:
            out.append(_SIMPLE_ESCAPES[nxt])
            i += 2
            continue

        # Unknown escape: keep the backslash so the consumer can see the
        # original text and decide whether to complain.
        out.append(c)
        i += 1

    return "".join(out)
