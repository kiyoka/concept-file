"""Summarize source code using tree-sitter for embedding."""

from pathlib import Path


# Map file extensions to tree-sitter language modules
LANGUAGE_MAP = {
    ".java": "java",
    ".py": "python",
}


def get_language(filename):
    """Detect language from file extension. Returns None if unsupported."""
    ext = Path(filename).suffix.lower()
    return LANGUAGE_MAP.get(ext)


def _load_parser(lang):
    """Load tree-sitter parser for the given language."""
    from tree_sitter import Language, Parser

    if lang == "java":
        import tree_sitter_java as ts_lang
    elif lang == "python":
        import tree_sitter_python as ts_lang
    else:
        return None

    language = Language(ts_lang.language())
    parser = Parser(language)
    return parser


def _summarize_java(tree, source_bytes):
    """Extract structural summary from Java source."""
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent

        if node.type == "package_declaration":
            pkg = source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
            lines.append(pkg.rstrip(";").strip())

        elif node.type in ("class_declaration", "interface_declaration", "enum_declaration"):
            # Extract class/interface/enum name
            name_node = node.child_by_field_name("name")
            kind = node.type.replace("_declaration", "")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                # Check for superclass/interfaces
                superclass = node.child_by_field_name("superclass")
                interfaces = node.child_by_field_name("interfaces")
                decl = f"{prefix}{kind} {name}"
                if superclass:
                    sc_text = source_bytes[superclass.start_byte:superclass.end_byte].decode("utf-8", errors="replace")
                    decl += f" extends {sc_text}"
                if interfaces:
                    if_text = source_bytes[interfaces.start_byte:interfaces.end_byte].decode("utf-8", errors="replace")
                    decl += f" implements {if_text}"
                lines.append(decl)

            # Visit children for methods and fields
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)

        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")
            type_node = node.child_by_field_name("type")
            params_node = node.child_by_field_name("parameters")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                ret_type = source_bytes[type_node.start_byte:type_node.end_byte].decode("utf-8", errors="replace") if type_node else "void"
                params = _extract_java_params(params_node, source_bytes) if params_node else ""
                lines.append(f"{prefix}method {name}({params}): {ret_type}")

        elif node.type == "constructor_declaration":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                params = _extract_java_params(params_node, source_bytes) if params_node else ""
                lines.append(f"{prefix}constructor {name}({params})")

        elif node.type == "field_declaration":
            type_node = node.child_by_field_name("type")
            declarator = node.child_by_field_name("declarator")
            if type_node and declarator:
                field_type = source_bytes[type_node.start_byte:type_node.end_byte].decode("utf-8", errors="replace")
                field_name = source_bytes[declarator.start_byte:declarator.end_byte].decode("utf-8", errors="replace")
                # Remove initializer if present
                if "=" in field_name:
                    field_name = field_name.split("=")[0].strip()
                lines.append(f"{prefix}field {field_name}: {field_type}")

        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


def _extract_java_params(params_node, source_bytes):
    """Extract parameter list from Java method parameters."""
    params = []
    for child in params_node.children:
        if child.type == "formal_parameter":
            type_node = child.child_by_field_name("type")
            name_node = child.child_by_field_name("name")
            if type_node and name_node:
                ptype = source_bytes[type_node.start_byte:type_node.end_byte].decode("utf-8", errors="replace")
                pname = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                params.append(f"{pname}: {ptype}")
    return ", ".join(params)


def _summarize_python(tree, source_bytes):
    """Extract structural summary from Python source."""
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent

        if node.type == "import_statement" or node.type == "import_from_statement":
            text = source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
            lines.append(f"{prefix}{text}")

        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            superclasses = node.child_by_field_name("superclasses")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                decl = f"{prefix}class {name}"
                if superclasses:
                    sc_text = source_bytes[superclasses.start_byte:superclasses.end_byte].decode("utf-8", errors="replace")
                    decl += sc_text
                lines.append(decl)

            # Extract docstring and methods
            body = node.child_by_field_name("body")
            if body:
                _extract_docstring(body, source_bytes, lines, indent + 1)
                for child in body.children:
                    visit(child, indent + 1)

        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            return_type = node.child_by_field_name("return_type")
            if name_node:
                name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="replace")
                params = source_bytes[params_node.start_byte:params_node.end_byte].decode("utf-8", errors="replace") if params_node else "()"
                decl = f"{prefix}def {name}{params}"
                if return_type:
                    rt_text = source_bytes[return_type.start_byte:return_type.end_byte].decode("utf-8", errors="replace")
                    decl += f" -> {rt_text}"
                lines.append(decl)

            # Extract docstring
            body = node.child_by_field_name("body")
            if body:
                _extract_docstring(body, source_bytes, lines, indent + 1)

        elif node.type == "decorated_definition":
            # Process decorators
            for child in node.children:
                if child.type == "decorator":
                    dec_text = source_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="replace")
                    lines.append(f"{prefix}{dec_text}")
                else:
                    visit(child, indent)

        else:
            for child in node.children:
                if child.type in ("class_definition", "function_definition", "decorated_definition",
                                  "import_statement", "import_from_statement"):
                    visit(child, indent)

    visit(root)
    return "\n".join(lines)


def _extract_docstring(body_node, source_bytes, lines, indent):
    """Extract docstring from the first statement of a body."""
    prefix = "  " * indent
    for child in body_node.children:
        if child.type == "expression_statement":
            expr = child.children[0] if child.children else None
            if expr and expr.type == "string":
                doc = source_bytes[expr.start_byte:expr.end_byte].decode("utf-8", errors="replace")
                # Clean up triple-quoted strings
                doc = doc.strip("\"'").strip()
                if doc:
                    lines.append(f"{prefix}\"{doc}\"")
            break
        elif child.type != "comment":
            break


def summarize(filename, source_text):
    """Summarize source code for embedding.

    Returns (embed_source, used_summarizer) where embed_source is the
    text to be used for embedding, and used_summarizer indicates whether
    tree-sitter summarization was applied.

    For unsupported languages, returns the original text with filename prepended.
    """
    lang = get_language(filename)
    basename = Path(filename).name

    if not lang:
        return f"{basename}\n{source_text}", False

    try:
        parser = _load_parser(lang)
        if not parser:
            return f"{basename}\n{source_text}", False

        source_bytes = source_text.encode("utf-8")
        tree = parser.parse(source_bytes)

        if lang == "java":
            summary = _summarize_java(tree, source_bytes)
        elif lang == "python":
            summary = _summarize_python(tree, source_bytes)
        else:
            return f"{basename}\n{source_text}", False

        if not summary.strip():
            return f"{basename}\n{source_text}", False

        return f"{basename}\n{summary}", True

    except ImportError:
        # tree-sitter language package not installed
        return f"{basename}\n{source_text}", False
    except Exception:
        # Parsing failed, fall back to raw text
        return f"{basename}\n{source_text}", False
