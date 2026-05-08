#!/usr/bin/env python3
"""
Layer dependency linter for habit tracker.
Enforces layered architecture rules on the Python codebase.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Set, List, Tuple

# Layer dependency rules: layer -> set of layers it may import from
LAYER_RULES = {
    "types": {"types"},
    "config": {"types", "config"},
    "repo": {"types", "config", "repo"},
    "service": {"types", "config", "repo", "providers", "service"},
    "runtime": {"types", "config", "repo", "service", "providers", "runtime"},
    "ui": {"types", "config", "service", "runtime", "providers", "ui"},
    "providers": {"types", "config", "utils", "providers"},
    "utils": {"utils"},
}

# Maximum file size in lines
MAX_FILE_LINES = 300

# Source root
SRC_ROOT = Path(__file__).parent / "src"

def extract_imports(file_path: str) -> Set[str]:
    """Extract imported module names from a Python file."""
    imports = set()
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read(), filename=file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
    return imports

def get_layer(file_path: str) -> str:
    """Determine which layer a file belongs to based on its path."""
    rel_path = Path(file_path).relative_to(SRC_ROOT)
    parts = rel_path.parts
    
    if len(parts) < 2:
        return None
    
    # First directory should be a layer name
    if parts[0] in LAYER_RULES:
        return parts[0]
    
    return None

def map_import_to_layer(import_name: str) -> str:
    """Map an imported module name to its layer."""
    # Internal imports (from src/)
    if import_name in LAYER_RULES:
        return import_name
    
    # Check if it's a submodule import
    for layer in LAYER_RULES:
        if import_name.startswith(layer + "."):
            return layer
    
    # External imports don't belong to any layer
    return None

def check_file(file_path: str, errors: List[str]) -> None:
    """Check a single Python file for violations."""
    if not file_path.endswith(".py"):
        return
    
    # Get layer
    layer = get_layer(file_path)
    if not layer:
        errors.append(f"{file_path}: File does not belong to a recognized layer directory")
        return
    
    # Check file size
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        if len(lines) > MAX_FILE_LINES:
            errors.append(
                f"{file_path}:{len(lines)}: File exceeds {MAX_FILE_LINES} lines. "
                f"Split into smaller modules within the same layer."
            )
    except Exception as e:
        errors.append(f"{file_path}: Could not read file: {e}")
        return
    
    # Check imports
    imports = extract_imports(file_path)
    
    allowed_layers = LAYER_RULES[layer]
    
    for import_name in imports:
        import_layer = map_import_to_layer(import_name)
        
        # Skip external imports (not in our codebase)
        if import_layer is None:
            continue
        
        # Check if this import is allowed
        if import_layer not in allowed_layers:
            errors.append(
                f"{file_path}: Illegal import '{import_name}' from layer '{import_layer}'. "
                f"Layer '{layer}' may only import from: {', '.join(sorted(allowed_layers))}."
            )

def lint() -> int:
    """Run the linter. Returns 0 if clean, 1 if violations found."""
    errors = []
    
    # Find all Python files in src/
    if not SRC_ROOT.exists():
        print("Error: src/ directory not found", file=sys.stderr)
        return 1
    
    for root, dirs, files in os.walk(SRC_ROOT):
        # Skip __pycache__ and test directories
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                check_file(file_path, errors)
    
    if errors:
        for error in sorted(errors):
            print(error, file=sys.stderr)
        return 1
    
    print("✓ All checks passed", file=sys.stdout)
    return 0

if __name__ == "__main__":
    sys.exit(lint())
