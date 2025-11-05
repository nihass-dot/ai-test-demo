

# --- AI-Generated Test ---
import pytest
import os
from pathlib import Path
from main import find_code_files

@pytest.fixture
def temp_project_structure(tmp_path):
    """
    Creates a temporary directory structure for testing find_code_files.
    """
    # Code files
    (tmp_path / "app.py").write_text("print('hello')")
    (tmp_path / "frontend.js").write_text("console.log('hello')")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "component.ts").write_text("let x: number = 1;")
    (tmp_path / "src" / "backend").mkdir()
    (tmp_path / "src" / "backend" / "handler.java").write_text("public class Handler {}")
    (tmp_path / "src" / "backend" / "main.go").write_text("package main")
    (tmp_path / "utils").mkdir()
    (tmp_path / "utils" / "helper.rs").write_text("fn helper() {}")

    # Non-code files
    (tmp_path / "README.md").write_text("# Project")
    (tmp_path / "config.ini").write_text("[settings]")
    (tmp_path / "src" / "data.txt").write_text("some data")

    # Ignored directories and their contents
    (tmp_path / "venv").mkdir()
    (tmp_path / "venv" / "activate").write_text("#!/bin/bash")
    (tmp_path / "venv" / "ignored.py").write_text("import sys")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_suite.py").write_text("import pytest")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/main")
    (tmp_path / ".vscode").mkdir() # Not explicitly ignored, but should not be picked up if empty or contains non-code.
    (tmp_path / ".vscode" / "settings.json").write_text("{}")

    return tmp_path

def test_find_code_files_empty_directory(tmp_path):
    """Tests find_code_files returns an empty list for an empty directory."""
    assert find_code_files(root_dir=tmp_path) == []

def test_find_code_files_only_non_code_files(tmp_path):
    """Tests find_code_files returns an empty list for a directory with only non-code files."""
    (tmp_path / "README.md").write_text("...")
    (tmp_path / "image.png").write_bytes(b"")
    (tmp_path / "doc.pdf").write_bytes(b"")
    assert find_code_files(root_dir=tmp_path) == []

def test_find_code_files_includes_valid_code_files(temp_project_structure):
    """Tests find_code_files correctly identifies and includes all valid code files."""
    root_dir = temp_project_structure
    found_files = find_code_files(root_dir=root_dir)

    expected_files = [
        str(root_dir / "app.py"),
        str(root_dir / "frontend.js"),
        str(root_dir / "src" / "component.ts"),
        str(root_dir / "src" / "backend" / "handler.java"),
        str(root_dir / "src" / "backend" / "main.go"),
        str(root_dir / "utils" / "helper.rs"),
    ]

    assert sorted(found_files) == sorted(expected_files)

def test_find_code_files_ignores_specified_directories(temp_project_structure):
    """Tests find_code_files correctly ignores files within 'venv', 'tests', and '.git' directories."""
    root_dir = temp_project_structure
    found_files = find_code_files(root_dir=root_dir)

    # Check that files from ignored directories are not present
    assert str(root_dir / "venv" / "ignored.py") not in found_files
    assert str(root_dir / "tests" / "test_suite.py") not in found_files
    assert str(root_dir / ".git" / "HEAD") not in found_files

    # Also ensure no path segment contains the ignored directory names
    for file_path in found_files:
        assert "venv" not in Path(file_path).parts
        assert "tests" not in Path(file_path).parts
        assert ".git" not in Path(file_path).parts

def test_find_code_files_ignores_non_code_extensions(temp_project_structure):
    """Tests find_code_files correctly ignores files with non-code extensions."""
    root_dir = temp_project_structure
    found_files = find_code_files(root_dir=root_dir)

    assert str(root_dir / "README.md") not in found_files
    assert str(root_dir / "config.ini") not in found_files
    assert str(root_dir / "src" / "data.txt") not in found_files
    assert str(root_dir / ".vscode" / "settings.json") not in found_files

def test_find_code_files_with_custom_root_directory(tmp_path):
    """Tests find_code_files functions correctly when a custom root_dir is provided."""
    custom_root = tmp_path / "my_project"
    custom_root.mkdir()
    (custom_root / "component.vue").write_text("<template></template>") # This extension is not in `find_code_files`
    (custom_root / "source.py").write_text("def func(): pass")
    (custom_root / "nested_dir").mkdir()
    (custom_root / "nested_dir" / "script.js").write_text("alert('hello');")

    expected_files = [
        str(custom_root / "source.py"),
        str(custom_root / "nested_dir" / "script.js"),
    ]

    found_files = find_code_files(root_dir=custom_root)
    assert sorted(found_files) == sorted(expected_files)

# --- End AI-Generated Test ---
