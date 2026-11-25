"""Unsent: The Micro-Confession Sprint.

Writes one two-part micro-confession to /output/entry.txt.

Stdlib only. No network, no environment, no input files, no randomness,
no timestamps. Deterministic: every run writes the same bytes.
"""

from pathlib import Path

# Candidate C (PLAN section 3): "See you Monday".
# Verified counts (python3, re-checked by tests U2/U3/U6):
#   To: line 34 chars, message 102 chars, total 137 chars (ASCII,
#   2 lines, no trailing newline).
TO_LINE = "To: Ben, my best friend since 2019"
MESSAGE = (
    "I practiced telling you I liked you in the mirror for a month "
    "and still said 'see you Monday' instead."
)
ENTRY_TEXT = TO_LINE + "\n" + MESSAGE

OUTPUT_FILE = Path("/output/entry.txt")


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY_TEXT)


if __name__ == "__main__":
    main()
