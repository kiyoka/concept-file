"""Tests for summarizer fallback behavior on unsupported languages."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from concept_file.summarizer import summarize, _TEXT_EXTENSIONS, _FALLBACK_HEAD_LINES


class TestTextFileFallback:
    """Text files (.md, .txt, etc.) should return full text."""

    def test_markdown_full_text(self):
        text = "# Title\n\n" + "paragraph\n" * 50
        result, used = summarize("README.md", text)
        assert not used
        assert result == f"README.md\n{text}"

    def test_txt_full_text(self):
        text = "line\n" * 50
        result, used = summarize("notes.txt", text)
        assert not used
        assert result == f"notes.txt\n{text}"

    def test_rst_full_text(self):
        text = "Title\n=====\n\n" + "content\n" * 50
        result, used = summarize("doc.rst", text)
        assert not used
        assert result == f"doc.rst\n{text}"

    def test_text_extensions_set(self):
        for ext in [".md", ".txt", ".rst"]:
            assert ext in _TEXT_EXTENSIONS


class TestHeadLinesFallback:
    """Unsupported non-text files should return first N lines only."""

    def test_long_file_truncated(self):
        lines = [f"line {i}" for i in range(100)]
        text = "\n".join(lines)
        result, used = summarize("parse.y", text)
        assert not used
        expected_head = "\n".join(lines[:_FALLBACK_HEAD_LINES])
        assert result == f"parse.y\n{expected_head}"

    def test_short_file_unchanged(self):
        text = "short content\n"
        result, used = summarize("Makefile.in", text)
        assert not used
        assert result == f"Makefile.in\n{text.splitlines()[0]}"

    def test_makefile(self):
        lines = [f"target{i}:" for i in range(50)]
        text = "\n".join(lines)
        result, used = summarize("Makefile.in", text)
        assert not used
        result_lines = result.split("\n")
        # filename + 20 lines
        assert len(result_lines) == _FALLBACK_HEAD_LINES + 1

    def test_configure_script(self):
        lines = ["#!/bin/sh", "# configure script"] + [f"echo {i}" for i in range(50)]
        text = "\n".join(lines)
        result, used = summarize("configure", text)
        assert not used
        assert "#!/bin/sh" in result
        assert "configure" in result

    def test_gitignore(self):
        lines = [f"*.o", "build/", "dist/"] + [f"pattern{i}" for i in range(50)]
        text = "\n".join(lines)
        result, used = summarize(".gitignore", text)
        assert not used
        result_lines = result.split("\n")
        assert result_lines[0] == ".gitignore"
        assert len(result_lines) == _FALLBACK_HEAD_LINES + 1

    def test_bat_file(self):
        lines = ["@echo off", "rem Build script"] + [f"echo step{i}" for i in range(50)]
        text = "\n".join(lines)
        result, used = summarize("make.bat", text)
        assert not used
        assert "@echo off" in result
