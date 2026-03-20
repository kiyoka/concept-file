"""Tests for concept-embed CLI tool."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

CLI_DIR = Path(__file__).resolve().parent.parent / "cli"
CONCEPT_EMBED = str(CLI_DIR / "concept-embed")
EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

PYTHON_PATH_ENV = {
    "PYTHONPATH": str(Path(__file__).resolve().parent.parent / "python"),
    "PATH": "",
}

def run_embed(*args, input_text=None, env_extra=None):
    """Helper to run concept-embed and return CompletedProcess."""
    import os
    env = {**os.environ, **PYTHON_PATH_ENV}
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, CONCEPT_EMBED, *args],
        input=input_text,
        capture_output=True,
        text=True,
        env=env,
    )


def read_concept_file(path):
    """Read a .concept file and return parsed JSON body."""
    raw = Path(path).read_bytes()
    newline_pos = raw.index(b"\n")
    header_line = raw[:newline_pos].decode("utf-8")
    parts = header_line.split()
    assert parts[0] == "CNCP"
    json_length = int(parts[2])
    json_bytes = raw[newline_pos + 1 : newline_pos + 1 + json_length]
    return json.loads(json_bytes), header_line


class TestBasicOutput:
    """Test basic .concept file generation with --no-embed."""

    def test_from_stdin(self, tmp_path):
        out = tmp_path / "test.concept"
        result = run_embed(
            "--name", "test",
            "--no-embed",
            "-o", str(out),
            input_text="Hello, world!",
        )
        assert result.returncode == 0
        assert out.exists()
        data, header = read_concept_file(out)
        assert data["concept"] == "test"
        assert data["version"] == "1.0"
        assert data["text"] == "Hello, world!"
        assert "created_at" in data
        assert "embedding" not in data

    def test_from_text_arg(self, tmp_path):
        out = tmp_path / "test.concept"
        result = run_embed(
            "--name", "test",
            "--text", "Some text content",
            "--no-embed",
            "-o", str(out),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert data["text"] == "Some text content"

    def test_with_language(self, tmp_path):
        out = tmp_path / "test.concept"
        result = run_embed(
            "--name", "test",
            "--text", "こんにちは",
            "--language", "ja",
            "--no-embed",
            "-o", str(out),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert data["language"] == "ja"

    def test_with_keywords(self, tmp_path):
        out = tmp_path / "test.concept"
        result = run_embed(
            "--name", "test",
            "--text", "Hello",
            "--keywords", "greeting", "english",
            "--no-embed",
            "-o", str(out),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert data["keywords"] == ["greeting", "english"]

    def test_with_source_url(self, tmp_path):
        out = tmp_path / "test.concept"
        result = run_embed(
            "--name", "test",
            "--text", "Hello",
            "--source-url", "https://example.com",
            "--no-embed",
            "-o", str(out),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert data["provenance"]["source_url"] == "https://example.com"


class TestFileFormat:
    """Test .concept file format compliance."""

    def test_header_format(self, tmp_path):
        out = tmp_path / "test.concept"
        run_embed(
            "--name", "test",
            "--text", "Hello",
            "--no-embed",
            "-o", str(out),
        )
        header = out.read_bytes().split(b"\n", 1)[0].decode("utf-8")
        parts = header.split()
        assert len(parts) == 3
        assert parts[0] == "CNCP"
        assert parts[1] == "v1"
        assert parts[2].isdigit()

    def test_json_length_matches(self, tmp_path):
        out = tmp_path / "test.concept"
        run_embed(
            "--name", "test",
            "--text", "Hello, world!",
            "--no-embed",
            "-o", str(out),
        )
        raw = out.read_bytes()
        newline_pos = raw.index(b"\n")
        header = raw[:newline_pos].decode("utf-8")
        declared_len = int(header.split()[2])
        actual_json = raw[newline_pos + 1:]
        assert len(actual_json) == declared_len

    def test_utf8_text(self, tmp_path):
        out = tmp_path / "test.concept"
        run_embed(
            "--name", "日本語テスト",
            "--text", "これはUTF-8のテストです。絵文字🎉も含む。",
            "--no-embed",
            "-o", str(out),
        )
        data, _ = read_concept_file(out)
        assert data["concept"] == "日本語テスト"
        assert "🎉" in data["text"]


class TestErrorHandling:
    """Test error cases."""

    def test_empty_text(self, tmp_path):
        out = tmp_path / "test.concept"
        result = run_embed(
            "--name", "test",
            "--no-embed",
            "-o", str(out),
            input_text="",
        )
        assert result.returncode != 0
        assert "empty text" in result.stderr.lower()

    def test_missing_name(self, tmp_path):
        out = tmp_path / "test.concept"
        result = run_embed(
            "--text", "Hello",
            "--no-embed",
            "-o", str(out),
        )
        assert result.returncode != 0

    def test_missing_output(self):
        result = run_embed(
            "--name", "test",
            "--text", "Hello",
            "--no-embed",
        )
        assert result.returncode != 0


class TestTreeSitterIntegration:
    """Test --source-file option with tree-sitter summarization."""

    def test_python_source_file(self, tmp_path):
        src = tmp_path / "hello.py"
        src.write_text("def greet(name):\n    return f'Hello, {name}!'\n")
        out = tmp_path / "hello.py.concept"
        result = run_embed(
            "--name", "hello.py",
            "--source-file", str(src),
            "--no-embed",
            "-o", str(out),
            input_text=src.read_text(),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert "embed_source" in data
        assert "greet" in data["embed_source"]
        # Original text preserved
        assert data["text"] == src.read_text()

    def test_java_source_file(self, tmp_path):
        src = tmp_path / "Hello.java"
        src.write_text(
            "public class Hello {\n"
            "    public String greet() {\n"
            "        return \"Hello!\";\n"
            "    }\n"
            "}\n"
        )
        out = tmp_path / "Hello.java.concept"
        result = run_embed(
            "--name", "Hello.java",
            "--source-file", str(src),
            "--no-embed",
            "-o", str(out),
            input_text=src.read_text(),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert "embed_source" in data
        assert "Hello" in data["embed_source"]

    def test_unsupported_extension_fallback(self, tmp_path):
        src = tmp_path / "data.xyz"
        src.write_text("some unknown format data\n")
        out = tmp_path / "data.xyz.concept"
        result = run_embed(
            "--name", "data.xyz",
            "--source-file", str(src),
            "--no-embed",
            "-o", str(out),
            input_text=src.read_text(),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        # Fallback: embed_source should be null
        assert "embed_source" in data
        assert data["embed_source"] is None

    def test_text_preserved_with_source_file(self, tmp_path):
        src = tmp_path / "calc.py"
        source_code = "def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n"
        src.write_text(source_code)
        out = tmp_path / "calc.py.concept"
        result = run_embed(
            "--name", "calc.py",
            "--source-file", str(src),
            "--no-embed",
            "-o", str(out),
            input_text=source_code,
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert data["text"] == source_code
        assert data["embed_source"] != data["text"]

    def test_source_file_reads_file_not_text_arg(self, tmp_path):
        """--source-file should read the file directly for summarization,
        not use --text content."""
        src = tmp_path / "User.java"
        src.write_text(
            "public class User {\n"
            "    private String name;\n"
            "    public String getName() { return name; }\n"
            "}\n"
        )
        out = tmp_path / "User.java.concept"
        result = run_embed(
            "--name", "User",
            "--text", "some unrelated text",
            "--source-file", str(src),
            "--no-embed",
            "-o", str(out),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        # text should be the --text argument
        assert data["text"] == "some unrelated text"
        # embed_source should be from the actual file, not from --text
        assert "class User" in data["embed_source"]
        assert "getName" in data["embed_source"]
        assert "some unrelated text" not in data["embed_source"]


class TestExistingExamples:
    """Test against existing example .concept files."""

    @pytest.mark.parametrize("lang,filename", [
        ("java", "Greeter.java"),
        ("python", "calculator.py"),
        ("go", "hello.go"),
        ("rust", "point.rs"),
        ("javascript", "hello.js"),
    ])
    def test_regenerate_example(self, tmp_path, lang, filename):
        src = EXAMPLES_DIR / "tree-sitter-test" / lang / filename
        if not src.exists():
            pytest.skip(f"Example file not found: {src}")
        out = tmp_path / f"{filename}.concept"
        result = run_embed(
            "--name", filename,
            "--source-file", str(src),
            "--no-embed",
            "-o", str(out),
            input_text=src.read_text(),
        )
        assert result.returncode == 0
        data, _ = read_concept_file(out)
        assert data["concept"] == filename
        assert data["text"] == src.read_text()
        assert "embed_source" in data
