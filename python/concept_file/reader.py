"""Read and write .concept files according to SPEC.md."""

import json
from pathlib import Path

MAGIC = "CNCP"
FORMAT_VERSION = 1


def read_concept(path):
    """Read a .concept file and return the parsed JSON body as a dict."""
    path = Path(path)
    raw = path.read_bytes()

    newline_pos = raw.index(b"\n")
    header_line = raw[:newline_pos].decode("utf-8")

    parts = header_line.split()
    if len(parts) != 3:
        raise ValueError(f"Invalid header line: {header_line}")
    magic, version_str, json_length_str = parts

    if magic != MAGIC:
        raise ValueError(f"Invalid magic: {magic!r}, expected {MAGIC!r}")

    version = int(version_str.lstrip("v"))
    if version > FORMAT_VERSION:
        raise ValueError(f"Unsupported format version: {version}")

    json_length = int(json_length_str)
    json_bytes = raw[newline_pos + 1 : newline_pos + 1 + json_length]

    return json.loads(json_bytes)


def write_concept(path, data):
    """Write a dict as a .concept file."""
    path = Path(path)
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    header_line = f"{MAGIC} v{FORMAT_VERSION} {len(json_bytes)}\n"
    path.write_bytes(header_line.encode("utf-8") + json_bytes)
