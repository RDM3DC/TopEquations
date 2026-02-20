from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TARGET = REPO / "data" / "equations.json"

# Fields that may contain LaTeX needing backslash escaping for JSON
FIELDS = [
    "equationLatex",
    "differentialLatex",
    "sourceLatex",
]

# Match a JSON string field value on one line: "field": "..."
# This file is formatted with each entry on one line, so this is safe.

def escape_json_string_content(s: str) -> str:
    # Escape any backslash that isn't already escaped.
    # i.e. turn \ into \\ but leave existing \\ as-is.
    return re.sub(r"(?<!\\)\\(?!\\)", r"\\\\", s)


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    for field in FIELDS:
        pat = re.compile(rf'("{re.escape(field)}"\s*:\s*")([^"\\]*(?:\\.[^"\\]*)*)(")')
        # The middle group is the raw string content with any escapes; we still need to ensure lone backslashes are doubled.

        def repl(m: re.Match) -> str:
            prefix, content, suffix = m.group(1), m.group(2), m.group(3)
            fixed = escape_json_string_content(content)
            return prefix + fixed + suffix

        text = pat.sub(repl, text)

    TARGET.write_text(text, encoding="utf-8")
    print("Rewrote", TARGET)


if __name__ == "__main__":
    main()
