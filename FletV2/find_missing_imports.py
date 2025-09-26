# find_missing_imports.py
# Save in your workspace root and run: python find_missing_imports.py
import ast
import os
import sys
from collections import defaultdict

# Add parent directory to path for Shared imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ALWAYS import this in any Python file that deals with subprocess or console I/O

root = os.getcwd()
ignore_dirs = {"flet_venv", ".venv", "__pycache__", ".git", "dist", "build"}
imports: dict[str, set[str]] = defaultdict(set)

def add_import(name, fn):
    top = name.split('.')[0]
    imports[top].add(fn)

for dirpath, dirnames, filenames in os.walk(root):
    # skip big folders
    dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=path)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    add_import(n.name, path)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    add_import(node.module, path)

# now test imports using this interpreter
missing = {}
for mod, files in sorted(imports.items()):
    # ignore stdlib-ish obvious names and local relative ones
    if mod in {"os", "sys", "re", "json", "typing", "pathlib", "itertools", "subprocess", "shutil", "collections", "logging", "datetime", "math", "glob", "inspect"}:
        continue
    try:
        __import__(mod)
    except Exception as e:
        missing[mod] = (str(e), list(files)[:5])  # sample files where used

# print results
if not missing:
    print("No missing top-level imports detected (from those scanned).")
    sys.exit(0)

print("MISSING MODULES (top-level name) and sample file(s) where used:\n")
for mod,(err, files) in missing.items():
    print(f"{mod}  -->  {err}")
    for f in files:
        print(f"   used in: {os.path.relpath(f, root)}")
    print()
print("----\nCount:", len(missing))
