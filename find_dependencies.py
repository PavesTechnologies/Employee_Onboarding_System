import ast
import os
from collections import defaultdict

PROJECT_DIR = "Backend"

imports = defaultdict(set)

for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=path)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports[alias.name.split(".")[0]].add(path)

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports[node.module.split(".")[0]].add(path)

            except Exception as e:
                print(f"Error parsing {path}: {e}")

print("\n===== USED IMPORTS =====\n")

for module in sorted(imports):
    print(module)

print(f"\nTotal unique imports: {len(imports)}")