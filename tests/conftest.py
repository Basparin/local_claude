#!/usr/bin/env python3
"""
Pytest configuration and fixtures for LocalClaude tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from core.cli_engine import CLIEngine


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_settings(temp_workspace):
    """Create test settings with temporary workspace"""
    settings = Settings()
    settings.workspace_dir = temp_workspace
    return settings


@pytest.fixture
def test_cli(test_settings):
    """Create a CLI engine instance for testing"""
    return CLIEngine(test_settings)


@pytest.fixture
def sample_python_file(temp_workspace):
    """Create a sample Python file for testing"""
    file_path = Path(temp_workspace) / "sample.py"
    content = '''#!/usr/bin/env python3
"""
Sample Python file for testing
"""

def hello_world():
    """Simple hello world function"""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_project_structure(temp_workspace):
    """Create a sample project structure for testing"""
    project_path = Path(temp_workspace) / "sample_project"
    
    # Create directories
    (project_path / "src").mkdir(parents=True)
    (project_path / "tests").mkdir()
    (project_path / "docs").mkdir()
    
    # Create files
    (project_path / "README.md").write_text("# Sample Project")
    (project_path / "requirements.txt").write_text("requests>=2.25.0")
    (project_path / "src" / "__init__.py").write_text("")
    (project_path / "src" / "main.py").write_text("print('Hello from main')")
    (project_path / "tests" / "__init__.py").write_text("")
    (project_path / "tests" / "test_main.py").write_text("import unittest")
    
    return project_path


# Test configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )