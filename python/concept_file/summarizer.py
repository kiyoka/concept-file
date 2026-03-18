"""Summarize source code using tree-sitter for embedding."""

from pathlib import Path


# Map file extensions to (tree-sitter module name, language key)
LANGUAGE_MAP = {
    # Java
    ".java": "java",
    # Python
    ".py": "python",
    # JavaScript
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    # TypeScript
    ".ts": "typescript",
    ".tsx": "typescript_tsx",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # C
    ".c": "c",
    ".h": "c",
    # C++
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".cc": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".hh": "cpp",
    # C#
    ".cs": "c_sharp",
    # Ruby
    ".rb": "ruby",
    # PHP
    ".php": "php",
    # Swift
    ".swift": "swift",
    # Kotlin
    ".kt": "kotlin",
    ".kts": "kotlin",
    # Scala
    ".scala": "scala",
    # Haskell
    ".hs": "haskell",
    # Elixir
    ".ex": "elixir",
    ".exs": "elixir",
    # Lua
    ".lua": "lua",
    # Bash
    ".sh": "bash",
    ".bash": "bash",
    # HTML
    ".html": "html",
    ".htm": "html",
    # CSS
    ".css": "css",
    # JSON
    ".json": "json",
    # YAML
    ".yaml": "yaml",
    ".yml": "yaml",
    # TOML
    ".toml": "toml",
    # Zig
    ".zig": "zig",
    # OCaml
    ".ml": "ocaml",
    ".mli": "ocaml",
    # Objective-C
    ".m": "objc",
}


def get_language(filename):
    """Detect language from file extension. Returns None if unsupported."""
    ext = Path(filename).suffix.lower()
    return LANGUAGE_MAP.get(ext)


def _load_parser(lang):
    """Load tree-sitter parser for the given language."""
    from tree_sitter import Language, Parser

    ts_mod = _import_ts_module(lang)
    if not ts_mod:
        return None

    if lang == "typescript":
        language = Language(ts_mod.language_typescript())
    elif lang == "typescript_tsx":
        language = Language(ts_mod.language_tsx())
    elif lang == "php":
        language = Language(ts_mod.language_php())
    elif lang == "ocaml":
        language = Language(ts_mod.language_ocaml())
    else:
        language = Language(ts_mod.language())
    parser = Parser(language)
    return parser


def _import_ts_module(lang):
    """Dynamically import a tree-sitter language module."""
    module_map = {
        "java": "tree_sitter_java",
        "python": "tree_sitter_python",
        "javascript": "tree_sitter_javascript",
        "typescript": "tree_sitter_typescript",
        "typescript_tsx": "tree_sitter_typescript",
        "go": "tree_sitter_go",
        "rust": "tree_sitter_rust",
        "c": "tree_sitter_c",
        "cpp": "tree_sitter_cpp",
        "c_sharp": "tree_sitter_c_sharp",
        "ruby": "tree_sitter_ruby",
        "php": "tree_sitter_php",
        "swift": "tree_sitter_swift",
        "kotlin": "tree_sitter_kotlin",
        "scala": "tree_sitter_scala",
        "haskell": "tree_sitter_haskell",
        "elixir": "tree_sitter_elixir",
        "lua": "tree_sitter_lua",
        "bash": "tree_sitter_bash",
        "html": "tree_sitter_html",
        "css": "tree_sitter_css",
        "json": "tree_sitter_json",
        "yaml": "tree_sitter_yaml",
        "toml": "tree_sitter_toml",
        "zig": "tree_sitter_zig",
        "ocaml": "tree_sitter_ocaml",
        "objc": "tree_sitter_objc",
    }
    mod_name = module_map.get(lang)
    if not mod_name:
        return None
    try:
        import importlib
        return importlib.import_module(mod_name)
    except ImportError:
        return None


def _node_text(node, source_bytes):
    """Get text content of a node."""
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


# ─── Java ──────────────────────────────────────────────────────────────

def _summarize_java(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "package_declaration":
            lines.append(_node_text(node, source_bytes).rstrip(";").strip())
        elif node.type in ("class_declaration", "interface_declaration", "enum_declaration"):
            name_node = node.child_by_field_name("name")
            kind = node.type.replace("_declaration", "")
            if name_node:
                decl = f"{prefix}{kind} {_node_text(name_node, source_bytes)}"
                sc = node.child_by_field_name("superclass")
                ifaces = node.child_by_field_name("interfaces")
                if sc:
                    decl += f" extends {_node_text(sc, source_bytes)}"
                if ifaces:
                    decl += f" implements {_node_text(ifaces, source_bytes)}"
                lines.append(decl)
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")
            type_node = node.child_by_field_name("type")
            params_node = node.child_by_field_name("parameters")
            if name_node:
                ret = _node_text(type_node, source_bytes) if type_node else "void"
                params = _extract_java_params(params_node, source_bytes) if params_node else ""
                lines.append(f"{prefix}method {_node_text(name_node, source_bytes)}({params}): {ret}")
        elif node.type == "constructor_declaration":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            if name_node:
                params = _extract_java_params(params_node, source_bytes) if params_node else ""
                lines.append(f"{prefix}constructor {_node_text(name_node, source_bytes)}({params})")
        elif node.type == "field_declaration":
            type_node = node.child_by_field_name("type")
            declarator = node.child_by_field_name("declarator")
            if type_node and declarator:
                fname = _node_text(declarator, source_bytes).split("=")[0].strip()
                lines.append(f"{prefix}field {fname}: {_node_text(type_node, source_bytes)}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


def _extract_java_params(params_node, source_bytes):
    params = []
    for child in params_node.children:
        if child.type == "formal_parameter":
            t = child.child_by_field_name("type")
            n = child.child_by_field_name("name")
            if t and n:
                params.append(f"{_node_text(n, source_bytes)}: {_node_text(t, source_bytes)}")
    return ", ".join(params)


# ─── Python ────────────────────────────────────────────────────────────

def _summarize_python(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type in ("import_statement", "import_from_statement"):
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            superclasses = node.child_by_field_name("superclasses")
            if name_node:
                decl = f"{prefix}class {_node_text(name_node, source_bytes)}"
                if superclasses:
                    decl += _node_text(superclasses, source_bytes)
                lines.append(decl)
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
                params = _node_text(params_node, source_bytes) if params_node else "()"
                decl = f"{prefix}def {_node_text(name_node, source_bytes)}{params}"
                if return_type:
                    decl += f" -> {_node_text(return_type, source_bytes)}"
                lines.append(decl)
            body = node.child_by_field_name("body")
            if body:
                _extract_docstring(body, source_bytes, lines, indent + 1)
        elif node.type == "decorated_definition":
            for child in node.children:
                if child.type == "decorator":
                    lines.append(f"{prefix}{_node_text(child, source_bytes)}")
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
    prefix = "  " * indent
    for child in body_node.children:
        if child.type == "expression_statement":
            expr = child.children[0] if child.children else None
            if expr and expr.type == "string":
                doc = _node_text(expr, source_bytes).strip("\"'").strip()
                if doc:
                    lines.append(f'{prefix}"{doc}"')
            break
        elif child.type != "comment":
            break


# ─── JavaScript ────────────────────────────────────────────────────────

def _summarize_javascript(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type in ("import_statement",):
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                decl = f"{prefix}class {_node_text(name_node, source_bytes)}"
                for child in node.children:
                    if child.type == "class_heritage":
                        decl += f" {_node_text(child, source_bytes)}"
                lines.append(decl)
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "method_definition":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            if name_node:
                params = _node_text(params_node, source_bytes) if params_node else "()"
                lines.append(f"{prefix}method {_node_text(name_node, source_bytes)}{params}")
        elif node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            if name_node:
                params = _node_text(params_node, source_bytes) if params_node else "()"
                lines.append(f"{prefix}function {_node_text(name_node, source_bytes)}{params}")
        elif node.type == "lexical_declaration" or node.type == "variable_declaration":
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = child.child_by_field_name("name")
                    value_node = child.child_by_field_name("value")
                    if name_node and value_node and value_node.type in ("arrow_function", "function"):
                        params = ""
                        p = value_node.child_by_field_name("parameters")
                        if p:
                            params = _node_text(p, source_bytes)
                        lines.append(f"{prefix}const {_node_text(name_node, source_bytes)}{params}")
        elif node.type == "export_statement":
            for child in node.children:
                visit(child, indent)
        else:
            for child in node.children:
                if child.type in ("class_declaration", "function_declaration", "export_statement",
                                  "import_statement", "lexical_declaration", "variable_declaration"):
                    visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── TypeScript (reuses JS with type annotations) ─────────────────────

def _summarize_typescript(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type in ("import_statement",):
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                decl = f"{prefix}class {_node_text(name_node, source_bytes)}"
                for child in node.children:
                    if child.type == "class_heritage":
                        decl += f" {_node_text(child, source_bytes)}"
                lines.append(decl)
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "interface_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}interface {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "type_alias_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}type {_node_text(name_node, source_bytes)}")
        elif node.type == "enum_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}enum {_node_text(name_node, source_bytes)}")
        elif node.type in ("method_definition", "method_signature"):
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            ret = node.child_by_field_name("return_type")
            if name_node:
                params = _node_text(params_node, source_bytes) if params_node else "()"
                decl = f"{prefix}method {_node_text(name_node, source_bytes)}{params}"
                if ret:
                    rt = _node_text(ret, source_bytes).lstrip(": ")
                    decl += f": {rt}"
                lines.append(decl)
        elif node.type == "property_signature":
            name_node = node.child_by_field_name("name")
            type_node = node.child_by_field_name("type")
            if name_node:
                decl = f"{prefix}prop {_node_text(name_node, source_bytes)}"
                if type_node:
                    t = _node_text(type_node, source_bytes).lstrip(": ")
                    decl += f": {t}"
                lines.append(decl)
        elif node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            ret = node.child_by_field_name("return_type")
            if name_node:
                params = _node_text(params_node, source_bytes) if params_node else "()"
                decl = f"{prefix}function {_node_text(name_node, source_bytes)}{params}"
                if ret:
                    rt = _node_text(ret, source_bytes).lstrip(": ")
                    decl += f": {rt}"
                lines.append(decl)
        elif node.type in ("lexical_declaration", "variable_declaration"):
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = child.child_by_field_name("name")
                    value_node = child.child_by_field_name("value")
                    if name_node and value_node and value_node.type in ("arrow_function", "function"):
                        params = ""
                        p = value_node.child_by_field_name("parameters")
                        if p:
                            params = _node_text(p, source_bytes)
                        lines.append(f"{prefix}const {_node_text(name_node, source_bytes)}{params}")
        elif node.type == "export_statement":
            for child in node.children:
                visit(child, indent)
        else:
            for child in node.children:
                if child.type in ("class_declaration", "function_declaration", "export_statement",
                                  "import_statement", "interface_declaration", "type_alias_declaration",
                                  "enum_declaration", "lexical_declaration", "variable_declaration"):
                    visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Go ────────────────────────────────────────────────────────────────

def _summarize_go(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "package_clause":
            lines.append(_node_text(node, source_bytes))
        elif node.type == "import_declaration":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            result = node.child_by_field_name("result")
            if name_node:
                decl = f"{prefix}func {_node_text(name_node, source_bytes)}"
                if params:
                    decl += _node_text(params, source_bytes)
                if result:
                    decl += f" {_node_text(result, source_bytes)}"
                lines.append(decl)
        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")
            receiver = node.child_by_field_name("receiver")
            params = node.child_by_field_name("parameters")
            result = node.child_by_field_name("result")
            if name_node:
                decl = f"{prefix}func "
                if receiver:
                    decl += f"{_node_text(receiver, source_bytes)} "
                decl += _node_text(name_node, source_bytes)
                if params:
                    decl += _node_text(params, source_bytes)
                if result:
                    decl += f" {_node_text(result, source_bytes)}"
                lines.append(decl)
        elif node.type == "type_declaration":
            for child in node.children:
                if child.type == "type_spec":
                    name_node = child.child_by_field_name("name")
                    type_node = child.child_by_field_name("type")
                    if name_node:
                        if type_node and type_node.type == "struct_type":
                            lines.append(f"{prefix}struct {_node_text(name_node, source_bytes)}")
                            for field in type_node.children:
                                if field.type == "field_declaration_list":
                                    for f in field.children:
                                        if f.type == "field_declaration":
                                            lines.append(f"{prefix}  {_node_text(f, source_bytes)}")
                        elif type_node and type_node.type == "interface_type":
                            lines.append(f"{prefix}interface {_node_text(name_node, source_bytes)}")
                            for spec in type_node.children:
                                if spec.type in ("method_spec", "type_elem"):
                                    lines.append(f"{prefix}  {_node_text(spec, source_bytes)}")
                        else:
                            lines.append(f"{prefix}type {_node_text(name_node, source_bytes)}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Rust ──────────────────────────────────────────────────────────────

def _summarize_rust(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "use_declaration":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "function_item":
            name_node = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            ret = node.child_by_field_name("return_type")
            if name_node:
                decl = f"{prefix}fn {_node_text(name_node, source_bytes)}"
                if params:
                    decl += _node_text(params, source_bytes)
                if ret:
                    decl += f" -> {_node_text(ret, source_bytes)}"
                lines.append(decl)
        elif node.type == "struct_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}struct {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    if child.type == "field_declaration":
                        lines.append(f"{prefix}  {_node_text(child, source_bytes)}")
        elif node.type == "enum_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}enum {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    if child.type == "enum_variant":
                        lines.append(f"{prefix}  {_node_text(child, source_bytes)}")
        elif node.type == "trait_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}trait {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "impl_item":
            trait_node = node.child_by_field_name("trait")
            type_node = node.child_by_field_name("type")
            if type_node:
                decl = f"{prefix}impl "
                if trait_node:
                    decl += f"{_node_text(trait_node, source_bytes)} for "
                decl += _node_text(type_node, source_bytes)
                lines.append(decl)
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "type_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}type {_node_text(name_node, source_bytes)}")
        elif node.type == "mod_item":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}mod {_node_text(name_node, source_bytes)}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── C ─────────────────────────────────────────────────────────────────

def _summarize_c(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "preproc_include":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "function_definition":
            declarator = node.child_by_field_name("declarator")
            type_node = node.child_by_field_name("type")
            if declarator:
                ret = _node_text(type_node, source_bytes) if type_node else ""
                lines.append(f"{prefix}{ret} {_node_text(declarator, source_bytes)}")
        elif node.type == "declaration":
            text = _node_text(node, source_bytes).rstrip(";")
            if "(" in text:  # function declaration
                lines.append(f"{prefix}{text}")
        elif node.type == "struct_specifier":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}struct {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    if child.type == "field_declaration":
                        lines.append(f"{prefix}  {_node_text(child, source_bytes).rstrip(';')}")
        elif node.type == "enum_specifier":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}enum {_node_text(name_node, source_bytes)}")
        elif node.type == "type_definition":
            lines.append(f"{prefix}{_node_text(node, source_bytes).rstrip(';')}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── C++ ───────────────────────────────────────────────────────────────

def _summarize_cpp(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "preproc_include":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "namespace_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}namespace {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "class_specifier":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}class {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "struct_specifier":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}struct {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "function_definition":
            declarator = node.child_by_field_name("declarator")
            type_node = node.child_by_field_name("type")
            if declarator:
                ret = _node_text(type_node, source_bytes) if type_node else ""
                lines.append(f"{prefix}{ret} {_node_text(declarator, source_bytes)}")
        elif node.type == "field_declaration":
            lines.append(f"{prefix}{_node_text(node, source_bytes).rstrip(';')}")
        elif node.type == "template_declaration":
            for child in node.children:
                visit(child, indent)
        elif node.type == "enum_specifier":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}enum {_node_text(name_node, source_bytes)}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── C# ───────────────────────────────────────────────────────────────

def _summarize_c_sharp(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "using_directive":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "namespace_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}namespace {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}class {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "interface_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}interface {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "struct_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}struct {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "enum_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}enum {_node_text(name_node, source_bytes)}")
        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")
            type_node = node.child_by_field_name("type")
            params = node.child_by_field_name("parameters")
            if name_node:
                ret = _node_text(type_node, source_bytes) if type_node else "void"
                p = _node_text(params, source_bytes) if params else "()"
                lines.append(f"{prefix}method {_node_text(name_node, source_bytes)}{p}: {ret}")
        elif node.type == "constructor_declaration":
            name_node = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            if name_node:
                p = _node_text(params, source_bytes) if params else "()"
                lines.append(f"{prefix}constructor {_node_text(name_node, source_bytes)}{p}")
        elif node.type == "property_declaration":
            name_node = node.child_by_field_name("name")
            type_node = node.child_by_field_name("type")
            if name_node:
                t = _node_text(type_node, source_bytes) if type_node else ""
                lines.append(f"{prefix}property {_node_text(name_node, source_bytes)}: {t}")
        elif node.type == "field_declaration":
            lines.append(f"{prefix}{_node_text(node, source_bytes).rstrip(';').strip()}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Ruby ──────────────────────────────────────────────────────────────

def _summarize_ruby(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "class":
            name_node = node.child_by_field_name("name")
            superclass = node.child_by_field_name("superclass")
            if name_node:
                decl = f"{prefix}class {_node_text(name_node, source_bytes)}"
                if superclass:
                    decl += f" < {_node_text(superclass, source_bytes)}"
                lines.append(decl)
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "module":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}module {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "method":
            name_node = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            if name_node:
                decl = f"{prefix}def {_node_text(name_node, source_bytes)}"
                if params:
                    decl += _node_text(params, source_bytes)
                lines.append(decl)
        elif node.type == "singleton_method":
            name_node = node.child_by_field_name("name")
            obj = node.child_by_field_name("object")
            if name_node:
                decl = f"{prefix}def "
                if obj:
                    decl += f"{_node_text(obj, source_bytes)}."
                decl += _node_text(name_node, source_bytes)
                lines.append(decl)
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── PHP ───────────────────────────────────────────────────────────────

def _summarize_php(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "namespace_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}namespace {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent)
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}class {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "interface_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}interface {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "trait_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}trait {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "method_declaration":
            name_node = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            if name_node:
                p = _node_text(params, source_bytes) if params else "()"
                lines.append(f"{prefix}method {_node_text(name_node, source_bytes)}{p}")
        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            if name_node:
                p = _node_text(params, source_bytes) if params else "()"
                lines.append(f"{prefix}function {_node_text(name_node, source_bytes)}{p}")
        elif node.type == "property_declaration":
            lines.append(f"{prefix}{_node_text(node, source_bytes).rstrip(';').strip()}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Swift ─────────────────────────────────────────────────────────────

def _summarize_swift(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "import_declaration":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}class {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "protocol_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}protocol {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "struct_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}struct {_node_text(name_node, source_bytes)}")
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "enum_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}enum {_node_text(name_node, source_bytes)}")
        elif node.type == "function_declaration":
            # Capture the full signature line
            text = _node_text(node, source_bytes)
            sig = text.split("{")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif node.type == "property_declaration":
            text = _node_text(node, source_bytes)
            sig = text.split("{")[0].split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Kotlin ────────────────────────────────────────────────────────────

def _summarize_kotlin(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "import_header":
            lines.append(f"{prefix}{_node_text(node, source_bytes).strip()}")
        elif node.type == "package_header":
            lines.append(_node_text(node, source_bytes).strip())
        elif node.type == "class_declaration":
            text = _node_text(node, source_bytes)
            sig = text.split("{")[0].strip()
            lines.append(f"{prefix}{sig}")
            body = node.child_by_field_name("body") or _find_child_type(node, "class_body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "object_declaration":
            text = _node_text(node, source_bytes)
            sig = text.split("{")[0].strip()
            lines.append(f"{prefix}{sig}")
            body = _find_child_type(node, "class_body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "function_declaration":
            text = _node_text(node, source_bytes)
            sig = text.split("{")[0].split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif node.type == "property_declaration":
            text = _node_text(node, source_bytes)
            sig = text.split("=")[0].split("by")[0].strip()
            if "\n" not in sig:
                lines.append(f"{prefix}{sig}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Scala ─────────────────────────────────────────────────────────────

def _summarize_scala(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "package_clause":
            lines.append(_node_text(node, source_bytes))
        elif node.type == "import_declaration":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type in ("class_definition", "trait_definition", "object_definition"):
            text = _node_text(node, source_bytes)
            sig = text.split("{")[0].strip()
            lines.append(f"{prefix}{sig}")
            body = node.child_by_field_name("body") or _find_child_type(node, "template_body")
            if body:
                for child in body.children:
                    visit(child, indent + 1)
        elif node.type == "function_definition":
            text = _node_text(node, source_bytes)
            sig = text.split("{")[0].split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif node.type == "val_definition" or node.type == "var_definition":
            text = _node_text(node, source_bytes)
            sig = text.split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Haskell ───────────────────────────────────────────────────────────

def _summarize_haskell(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "header":
            text = _node_text(node, source_bytes).strip()
            lines.append(text)
        elif node.type == "import":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "signature":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "data_type":
            text = _node_text(node, source_bytes)
            sig = text.split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif node.type == "newtype":
            text = _node_text(node, source_bytes)
            sig = text.split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif node.type == "type_alias":
            text = _node_text(node, source_bytes)
            sig = text.split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif node.type in ("class", "instance"):
            text = _node_text(node, source_bytes)
            sig = text.split("where")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif node.type in ("imports", "declarations"):
            for child in node.children:
                visit(child, indent)
        elif node.type == "haskell":
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Elixir ────────────────────────────────────────────────────────────

def _summarize_elixir(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "call":
            text = _node_text(node, source_bytes)
            first_line = text.split("\n")[0].strip()
            if first_line.startswith(("defmodule ", "defprotocol ", "defimpl ")):
                name = first_line.split("do")[0].strip()
                lines.append(f"{prefix}{name}")
                for child in node.children:
                    if child.type == "do_block":
                        for c in child.children:
                            visit(c, indent + 1)
            elif first_line.startswith(("def ", "defp ", "defmacro ", "defmacrop ")):
                sig = first_line.split("do")[0].strip().rstrip(",")
                lines.append(f"{prefix}{sig}")
            elif first_line.startswith(("use ", "import ", "alias ", "require ")):
                lines.append(f"{prefix}{first_line}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Lua ───────────────────────────────────────────────────────────────

def _summarize_lua(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            params = node.child_by_field_name("parameters")
            if name_node:
                p = _node_text(params, source_bytes) if params else "()"
                lines.append(f"{prefix}function {_node_text(name_node, source_bytes)}{p}")
        elif node.type == "variable_declaration":
            for child in node.children:
                if child.type == "assignment_statement":
                    for sub in child.children:
                        if sub.type == "variable_list":
                            vtext = _node_text(sub, source_bytes)
                        if sub.type == "expression_list":
                            for expr in sub.children:
                                if expr.type == "function_definition":
                                    params = expr.child_by_field_name("parameters")
                                    p = _node_text(params, source_bytes) if params else "()"
                                    lines.append(f"{prefix}function {vtext}{p}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Bash ──────────────────────────────────────────────────────────────

def _summarize_bash(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}function {_node_text(name_node, source_bytes)}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── HTML ──────────────────────────────────────────────────────────────

def _summarize_html(tree, source_bytes):
    lines = []
    root = tree.root_node
    tags_of_interest = {"head", "title", "body", "header", "nav", "main", "footer",
                        "section", "article", "aside", "form", "table", "script", "style"}

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "element":
            start_tag = None
            for child in node.children:
                if child.type == "start_tag":
                    start_tag = child
                    break
            if start_tag:
                tag_name = ""
                attrs = []
                for child in start_tag.children:
                    if child.type == "tag_name":
                        tag_name = _node_text(child, source_bytes)
                    elif child.type == "attribute":
                        attrs.append(_node_text(child, source_bytes))
                if tag_name.lower() in tags_of_interest:
                    attr_str = f" {' '.join(attrs)}" if attrs else ""
                    lines.append(f"{prefix}<{tag_name}{attr_str}>")
                    for child in node.children:
                        if child.type == "element":
                            visit(child, indent + 1)
                    return
        for child in node.children:
            visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── CSS ───────────────────────────────────────────────────────────────

def _summarize_css(tree, source_bytes):
    lines = []
    root = tree.root_node

    for child in root.children:
        if child.type == "rule_set":
            for sub in child.children:
                if sub.type == "selectors":
                    lines.append(_node_text(sub, source_bytes))
        elif child.type == "media_statement":
            text = _node_text(child, source_bytes)
            sig = text.split("{")[0].strip()
            lines.append(sig)
        elif child.type == "import_statement":
            lines.append(_node_text(child, source_bytes))

    return "\n".join(lines)


# ─── JSON ──────────────────────────────────────────────────────────────

def _summarize_json(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "pair":
            key_node = node.child_by_field_name("key")
            if key_node:
                lines.append(f"{prefix}{_node_text(key_node, source_bytes)}")

    if root.children and root.children[0].type == "object":
        for child in root.children[0].children:
            visit(child)

    return "\n".join(lines)


# ─── YAML ──────────────────────────────────────────────────────────────

def _summarize_yaml(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "block_mapping_pair":
            key_node = node.child_by_field_name("key")
            value_node = node.child_by_field_name("value")
            if key_node:
                lines.append(f"{prefix}{_node_text(key_node, source_bytes)}")
            if value_node:
                for child in value_node.children:
                    if child.type == "block_mapping":
                        for sub in child.children:
                            visit(sub, indent + 1)
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── TOML ──────────────────────────────────────────────────────────────

def _summarize_toml(tree, source_bytes):
    lines = []
    root = tree.root_node

    for child in root.children:
        if child.type == "table":
            for sub in child.children:
                if sub.type in ("bare_key", "dotted_key", "quoted_key"):
                    lines.append(f"[{_node_text(sub, source_bytes)}]")
        elif child.type == "pair":
            for sub in child.children:
                if sub.type in ("bare_key", "dotted_key", "quoted_key"):
                    lines.append(_node_text(sub, source_bytes))

    return "\n".join(lines)


# ─── Zig ───────────────────────────────────────────────────────────────

def _summarize_zig(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        text = _node_text(node, source_bytes)
        if node.type in ("TopLevelDecl",):
            first_line = text.split("{")[0].split("=")[0].strip()
            lines.append(f"{prefix}{first_line}")
        elif node.type == "FnProto":
            sig = text.split("{")[0].strip()
            lines.append(f"{prefix}{sig}")
        elif "fn " in text[:50] and node.type in ("VarDecl", "ContainerDecl"):
            sig = text.split("{")[0].split("=")[0].strip()
            lines.append(f"{prefix}{sig}")
        for child in node.children:
            visit(child, indent)

    # Zig tree-sitter may use different node names; use generic approach
    for child in root.children:
        text = _node_text(child, source_bytes)
        first_line = text.split("\n")[0].strip()
        if any(first_line.startswith(kw) for kw in ("pub ", "fn ", "const ", "var ", "test ")):
            sig = text.split("{")[0].split("=")[0].strip()
            if "\n" not in sig:
                lines.append(sig)

    return "\n".join(lines)


# ─── OCaml ─────────────────────────────────────────────────────────────

def _summarize_ocaml(tree, source_bytes):
    lines = []
    root = tree.root_node

    for child in root.children:
        text = _node_text(child, source_bytes)
        if child.type in ("value_definition", "type_definition", "module_definition",
                          "module_type_definition", "open_module", "exception_definition"):
            sig = text.split("=")[0].strip()
            lines.append(sig)
        elif child.type == "external":
            lines.append(text.rstrip())

    return "\n".join(lines)


# ─── Objective-C ───────────────────────────────────────────────────────

def _summarize_objc(tree, source_bytes):
    lines = []
    root = tree.root_node

    def visit(node, indent=0):
        prefix = "  " * indent
        if node.type == "preproc_include" or node.type == "preproc_import":
            lines.append(f"{prefix}{_node_text(node, source_bytes)}")
        elif node.type == "class_interface":
            name_node = node.child_by_field_name("name")
            superclass = node.child_by_field_name("superclass")
            if name_node:
                decl = f"{prefix}@interface {_node_text(name_node, source_bytes)}"
                if superclass:
                    decl += f" : {_node_text(superclass, source_bytes)}"
                lines.append(decl)
            for child in node.children:
                visit(child, indent + 1)
        elif node.type == "protocol_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                lines.append(f"{prefix}@protocol {_node_text(name_node, source_bytes)}")
            for child in node.children:
                visit(child, indent + 1)
        elif node.type == "method_declaration":
            text = _node_text(node, source_bytes).rstrip(";").strip()
            lines.append(f"{prefix}{text}")
        elif node.type == "property_declaration":
            text = _node_text(node, source_bytes).rstrip(";").strip()
            lines.append(f"{prefix}{text}")
        elif node.type == "function_definition":
            declarator = node.child_by_field_name("declarator")
            type_node = node.child_by_field_name("type")
            if declarator:
                ret = _node_text(type_node, source_bytes) if type_node else ""
                lines.append(f"{prefix}{ret} {_node_text(declarator, source_bytes)}")
        else:
            for child in node.children:
                visit(child, indent)

    visit(root)
    return "\n".join(lines)


# ─── Helper ───────────────────────────────────────────────────────────

def _find_child_type(node, type_name):
    """Find a child node by type name."""
    for child in node.children:
        if child.type == type_name:
            return child
    return None


# ─── Dispatch table ───────────────────────────────────────────────────

_SUMMARIZERS = {
    "java": _summarize_java,
    "python": _summarize_python,
    "javascript": _summarize_javascript,
    "typescript": _summarize_typescript,
    "typescript_tsx": _summarize_typescript,
    "go": _summarize_go,
    "rust": _summarize_rust,
    "c": _summarize_c,
    "cpp": _summarize_cpp,
    "c_sharp": _summarize_c_sharp,
    "ruby": _summarize_ruby,
    "php": _summarize_php,
    "swift": _summarize_swift,
    "kotlin": _summarize_kotlin,
    "scala": _summarize_scala,
    "haskell": _summarize_haskell,
    "elixir": _summarize_elixir,
    "lua": _summarize_lua,
    "bash": _summarize_bash,
    "html": _summarize_html,
    "css": _summarize_css,
    "json": _summarize_json,
    "yaml": _summarize_yaml,
    "toml": _summarize_toml,
    "zig": _summarize_zig,
    "ocaml": _summarize_ocaml,
    "objc": _summarize_objc,
}


# ─── Public API ───────────────────────────────────────────────────────

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

        summarizer = _SUMMARIZERS.get(lang)
        if not summarizer:
            return f"{basename}\n{source_text}", False

        summary = summarizer(tree, source_bytes)

        if not summary.strip():
            return f"{basename}\n{source_text}", False

        return f"{basename}\n{summary}", True

    except ImportError:
        return f"{basename}\n{source_text}", False
    except Exception:
        return f"{basename}\n{source_text}", False
