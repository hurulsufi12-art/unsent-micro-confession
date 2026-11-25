"""Tests for the Unsent micro-confession entry (candidate C).

TDD test suite written from PLAN.md section 4.4 before main.py exists.
Gate simulation helpers live here (they model the sealed scorer's rules:
UTF-8, 1-260 chars, not whitespace-only, message <= 200 chars, exactly
two lines) -- they test the *validator*, not main.py, where noted.
"""
import ast
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ENTRY_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ENTRY_DIR))

import main as entry_main  # noqa: E402

ENTRY_TEXT = entry_main.ENTRY_TEXT
OUTPUT_PATH = Path("/output/entry.txt")

SLUG = "u-boothlord-unsent-the-micro-confession-sprint-8c6596ba"
REPO = "hurulsufi12-art/unsent-micro-confession"
BADGE_BASE = f"https://make.fun/badge/{SLUG}"
BADGE_URLS = [
    f"{BADGE_BASE}.svg",
    f"{BADGE_BASE}/{REPO}/rank.svg",
    f"{BADGE_BASE}/{REPO}/reward.svg",
]


# --- Gate simulation (mirrors RULES.txt / competition.yaml) -----------------

def gate_valid(text: str) -> bool:
    """Sealed gate: UTF-8, 1-260 chars, not whitespace-only."""
    if not isinstance(text, str):
        return False
    if not (1 <= len(text) <= 260):
        return False
    if text.strip() == "":
        return False
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def message_valid(text: str) -> bool:
    """Two-part shape + message line <= 200 chars (judge brief)."""
    lines = text.split("\n")
    if len(lines) != 2:
        return False
    if not lines[0].startswith("To: "):
        return False
    if lines[0] != lines[0].strip() or lines[1] != lines[1].strip():
        return False
    if len(lines[1]) > 200:
        return False
    if "\r" in text or "\n\n" in text:
        return False
    # To: line: first name or role only -- no handle, no full name.
    addressee = lines[0][len("To: "):]
    if "@" in addressee:
        return False
    name_token = addressee.split(",")[0].strip()
    words = name_token.split()
    if len(words) == 2 and words[0][0].isupper() and words[1][0].isupper():
        return False
    return True


def run_entry(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-P", "-s", str(ENTRY_DIR / "main.py")],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestUnit(unittest.TestCase):
    def test_u1_two_lines_to_prefix(self):
        lines = ENTRY_TEXT.split("\n")
        self.assertEqual(len(lines), 2, "entry must be exactly 2 lines")
        self.assertTrue(lines[0].startswith("To: "), "line 1 must start with 'To: '")
        self.assertNotEqual(lines[1], "", "message line must be non-empty")

    def test_u2_message_at_most_200_chars(self):
        message = ENTRY_TEXT.split("\n")[1]
        self.assertLessEqual(len(message), 200)
        # candidate C message is 102 chars
        self.assertEqual(len(message), 102)

    def test_u3_total_1_to_260_not_whitespace_only(self):
        self.assertGreaterEqual(len(ENTRY_TEXT), 1)
        self.assertLessEqual(len(ENTRY_TEXT), 260)
        self.assertNotEqual(ENTRY_TEXT.strip(), "")
        # candidate C total is 137 chars
        self.assertEqual(len(ENTRY_TEXT), 137)

    def test_u4_no_trailing_newline_no_blank_line(self):
        self.assertFalse(ENTRY_TEXT.endswith("\n"))
        self.assertNotIn("\n\n", ENTRY_TEXT)

    def test_u5_to_line_first_name_or_role_only(self):
        to_line = ENTRY_TEXT.split("\n")[0]
        self.assertTrue(to_line.startswith("To: "))
        addressee = to_line[len("To: "):]
        self.assertNotIn("@", addressee, "no handle allowed in To:")
        # name token before the comma: exactly one word (first name) ...
        name_token = addressee.split(",")[0].strip()
        self.assertEqual(len(name_token.split()), 1,
                         "name before comma must be a single first name")
        # ... or a role phrase (no second capitalised word = full name)
        words = name_token.split()
        self.assertFalse(
            len(words) == 2 and words[0][0].isupper() and words[1][0].isupper(),
            "no full (two-word) name allowed in To:")
        # candidate C addressee
        self.assertEqual(addressee, "Ben, my best friend since 2019")

    def test_u6_ascii_char_equals_byte(self):
        encoded = ENTRY_TEXT.encode("utf-8")
        self.assertEqual(len(encoded), len(ENTRY_TEXT))

    def test_u7_stdlib_only_imports(self):
        source = (ENTRY_DIR / "main.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        allowed = {"pathlib", "os"}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertTrue(imported.issubset(allowed),
                        f"imports outside allow-list: {imported - allowed}")
        for banned in ("socket", "subprocess", "eval", "exec",
                       "__import__", "os.environ"):
            self.assertNotIn(banned, source, f"banned token present: {banned}")

    def test_u8_no_leading_trailing_whitespace_per_line(self):
        for line in ENTRY_TEXT.split("\n"):
            self.assertEqual(line, line.strip())

    def test_u9_no_cr_or_crlf(self):
        self.assertNotIn("\r", ENTRY_TEXT)
        self.assertEqual(ENTRY_TEXT.count("\n"), 1)


class TestIntegration(unittest.TestCase):
    def test_i1_runs_and_writes_output(self):
        if OUTPUT_PATH.exists():
            OUTPUT_PATH.unlink()
        if OUTPUT_PATH.parent.exists() and not any(OUTPUT_PATH.parent.iterdir()):
            OUTPUT_PATH.parent.rmdir()
        result = run_entry(ENTRY_DIR)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(OUTPUT_PATH.exists(), "/output/entry.txt not created")

    def test_i2_file_bytes_equal_entry_text(self):
        run_entry(ENTRY_DIR)
        self.assertEqual(OUTPUT_PATH.read_bytes(),
                         ENTRY_TEXT.encode("utf-8"))

    def test_i3_file_valid_utf8_and_gate_passes(self):
        run_entry(ENTRY_DIR)
        text = OUTPUT_PATH.read_bytes().decode("utf-8")
        self.assertTrue(gate_valid(text))
        self.assertTrue(message_valid(text))

    def test_i4_two_runs_same_sha256(self):
        run_entry(ENTRY_DIR)
        first = sha256_file(OUTPUT_PATH)
        run_entry(ENTRY_DIR)
        second = sha256_file(OUTPUT_PATH)
        self.assertEqual(first, second)

    def test_i5_existing_output_dir_contents_preserved(self):
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        sentinel = OUTPUT_PATH.parent / "keep-me.txt"
        sentinel.write_text("do not delete", encoding="utf-8")
        result = run_entry(ENTRY_DIR)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(sentinel.exists())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not delete")
        self.assertTrue(OUTPUT_PATH.exists())
        sentinel.unlink()

    def test_i6_readme_has_three_literal_badge_urls(self):
        readme = (ENTRY_DIR / "README.md").read_text(encoding="utf-8")
        for url in BADGE_URLS:
            self.assertIn(url, readme, f"badge URL missing: {url}")
        self.assertNotIn("{owner}", readme)
        self.assertNotIn("{repo}", readme)

    def test_i7_license_has_spdx_line(self):
        license_text = (ENTRY_DIR / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", license_text)

    def test_i8_gitignore_does_not_ignore_entry_files(self):
        for name in ("main.py", "README.md", "LICENSE"):
            result = subprocess.run(
                ["git", "-C", str(ENTRY_DIR), "check-ignore", name],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 1,
                             f"{name} is ignored by .gitignore")

    def test_i9_license_has_mit_grant_text(self):
        license_text = (ENTRY_DIR / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Permission is hereby granted, free of charge",
                      license_text)

    def test_i10_badges_are_links_to_makefun(self):
        readme = (ENTRY_DIR / "README.md").read_text(encoding="utf-8")
        for url in BADGE_URLS:
            pattern = re.compile(
                r"\[!\[.*?\]\(" + re.escape(url) +
                r"\)\]\(https://make\.fun/[^)]+\)")
            self.assertRegex(readme, pattern,
                             f"badge {url} is not a link to a make.fun page")


class TestEdgeCases(unittest.TestCase):
    def test_e1_empty_text_rejected_by_gate(self):
        self.assertFalse(gate_valid(""))

    def test_e2_boundary_260_chars(self):
        self.assertTrue(gate_valid("x" * 259))
        self.assertTrue(gate_valid("x" * 260))
        self.assertFalse(gate_valid("x" * 261))

    def test_e3_message_boundary_200_chars(self):
        self.assertTrue(message_valid("To: Ben\n" + "y" * 200))
        self.assertFalse(message_valid("To: Ben\n" + "y" * 201))

    def test_e4_non_ascii_still_valid_utf8_char_vs_byte(self):
        text = "To: Ben\ncafé ☕"
        encoded = text.encode("utf-8")
        self.assertEqual(len(text), 14)
        self.assertNotEqual(len(encoded), len(text))
        self.assertTrue(gate_valid(text))
        # ... but the real entry is ASCII, so char == byte there (U6)
        self.assertEqual(len(ENTRY_TEXT.encode("utf-8")), len(ENTRY_TEXT))

    def test_e5_double_newline_and_trailing_newline_rejected(self):
        self.assertFalse(message_valid("To: Ben\n\nmessage here"))
        self.assertFalse(message_valid("To: Ben\nmessage here\n"))

    def test_e6_whitespace_only_rejected(self):
        self.assertFalse(gate_valid("   \n  "))
        self.assertFalse(gate_valid("   "))

    def test_e7_handle_and_full_name_rejected_in_to(self):
        self.assertFalse(message_valid("To: @benhandle\nhello there"))
        # two-word capitalised name before the comma = full name
        to_line = "To: Ben Smith, my friend"
        name_token = to_line[len("To: "):].split(",")[0].strip()
        words = name_token.split()
        is_full_name = (len(words) == 2 and words[0][0].isupper()
                        and words[1][0].isupper())
        self.assertTrue(is_full_name)

    def test_e8_three_runs_byte_identical(self):
        hashes = []
        for _ in range(3):
            run_entry(ENTRY_DIR)
            hashes.append(sha256_file(OUTPUT_PATH))
        self.assertEqual(len(set(hashes)), 1)

    def test_e9_clean_room_copy_only_main_py(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            shutil.copy2(ENTRY_DIR / "main.py", tmp_path / "main.py")
            if OUTPUT_PATH.exists():
                OUTPUT_PATH.unlink()
            result = subprocess.run(
                [sys.executable, "-P", "-s", "main.py"],
                cwd=str(tmp_path), capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(OUTPUT_PATH.exists())
            self.assertEqual(OUTPUT_PATH.read_bytes(),
                             ENTRY_TEXT.encode("utf-8"))

    def test_e10_no_network_imports_static_audit(self):
        source = (ENTRY_DIR / "main.py").read_text(encoding="utf-8")
        for banned in ("socket", "urllib", "requests", "http.client",
                       "subprocess", "os.environ"):
            self.assertNotIn(banned, source, f"network/env token: {banned}")

    def test_e11_no_bom_in_output(self):
        run_entry(ENTRY_DIR)
        raw = OUTPUT_PATH.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), "BOM present")
        self.assertFalse(raw.decode("utf-8").startswith("\ufeff"))

    def test_e12_main_py_reads_no_other_file(self):
        source = (ENTRY_DIR / "main.py").read_text(encoding="utf-8")
        self.assertNotIn("read_text", source)
        self.assertNotIn("read_bytes", source)
        self.assertNotRegex(source, r"open\([^)]*['\"]r['\"]")
        self.assertNotIn("Path(__file__)", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
