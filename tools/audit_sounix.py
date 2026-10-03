#!/usr/bin/env python3
"""Read-only scanner: lists risky command and code patterns in Sounix's Python files.
Usage: python3 audit_sounix.py ~/sounix            (add --all to include low-risk notes)
It changes nothing. Paste the output to get it reviewed.
"""
import ast
import re
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
show_all = "--all" in sys.argv
root = Path(args[0] if args else ".").expanduser()
SKIP = {"venv", ".venv", ".git", "__pycache__", "node_modules"}
SUBPROCESS = {"run", "Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"}
SECRET = re.compile(r"(password|passwd|secret|token|api[_-]?key)\w*\s*=\s*[\"'][^\"']{6,}[\"']", re.I)
findings = []


def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def built(node):
    """True if the expression is assembled from pieces (f-string, + or %, .format)."""
    if isinstance(node, (ast.JoinedStr, ast.BinOp)):
        return True
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format")


def dynamic(node):
    return not isinstance(node, ast.Constant)


class Scanner(ast.NodeVisitor):
    def __init__(self, path, lines):
        self.path, self.lines = path, lines

    def add(self, sev, node, message):
        text = self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else ""
        findings.append((sev, str(self.path.relative_to(root)), node.lineno, message, text[:110]))

    def visit_Call(self, node):
        name = dotted(node.func)
        shell = any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True
                    for k in node.keywords)
        if name.split(".")[0] == "subprocess" and name.split(".")[-1] in SUBPROCESS and node.args:
            first = node.args[0]
            if shell and built(first):
                self.add("HIGH", node, "shell=True with a command built from text: command injection")
            elif shell:
                self.add("MED", node, "shell=True: avoid unless truly needed")
            elif built(first):
                self.add("MED", node, "command is one built string: use a list of arguments instead")
            elif isinstance(first, (ast.List, ast.Tuple)):
                names = [ast.unparse(e) for e in first.elts if dynamic(e)]
                if names and show_all:
                    self.add("INFO", node, "argument(s) from variables: " + ", ".join(names)
                             + " (make sure input can't start with '-')")
            elif dynamic(first):
                self.add("LOW", node, f"command comes from `{ast.unparse(first)}`: check it is never user-controlled")
        elif name in {"os.system", "os.popen", "commands.getoutput"}:
            self.add("HIGH", node, f"{name} runs through a shell")
        elif name in {"eval", "exec"} and node.args and dynamic(node.args[0]):
            self.add("HIGH", node, f"{name}() on non-constant text: arbitrary code execution")
        elif name in {"pickle.load", "pickle.loads", "marshal.load", "marshal.loads"}:
            self.add("MED", node, f"{name} on untrusted data can run code")
        elif name == "yaml.load" and not any(k.arg == "Loader" for k in node.keywords):
            self.add("MED", node, "yaml.load without a safe Loader: use yaml.safe_load")
        elif name == "tempfile.mktemp":
            self.add("LOW", node, "tempfile.mktemp is racy: use NamedTemporaryFile or mkstemp")
        elif name == "os.chmod" and len(node.args) > 1 and ast.unparse(node.args[1]) in {"0o777", "511"}:
            self.add("MED", node, "chmod 777 makes the file world-writable")
        elif name.endswith("_create_unverified_context") or any(
                k.arg == "verify" and isinstance(k.value, ast.Constant) and k.value.value is False
                for k in node.keywords):
            self.add("MED", node, "TLS certificate checking is turned off")
        self.generic_visit(node)


for path in sorted(root.rglob("*.py")):
    if SKIP & set(path.relative_to(root).parts):
        continue
    try:
        source = path.read_text(errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError) as error:
        findings.append(("INFO", str(path.relative_to(root)), 0, f"could not parse: {error}", ""))
        continue
    lines = source.splitlines()
    Scanner(path, lines).visit(tree)
    for number, line in enumerate(lines, 1):
        if SECRET.search(line):
            masked = re.sub(r"([\"'])[^\"']{6,}([\"'])", r"\1***\2", line.strip())
            findings.append(("MED", str(path.relative_to(root)), number, "possible hard-coded secret", masked[:110]))

order = {"HIGH": 0, "MED": 1, "LOW": 2, "INFO": 3}
findings.sort(key=lambda f: (order[f[0]], f[1], f[2]))
counts = {k: sum(1 for f in findings if f[0] == k) for k in order}
for sev, file, line, message, text in findings:
    print(f"{sev:<5} {file}:{line}  {message}")
    if text:
        print(f"        {text}")
print(f"\n{counts['HIGH']} high, {counts['MED']} medium, {counts['LOW']} low"
      + (f", {counts['INFO']} info" if show_all else "")
      + f"  (scanned {root})")
