"""Tests for the Open Agent Spec CLI commands."""
import pytest
from pathlib import Path
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from oas_cli.main import app

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_spec_file(temp_dir):
    """Create a sample spec file for testing."""
    spec = {
        "info": {
            "name": "test-agent",
            "description": "A test agent"
        },
        "intelligence": {
            "endpoint": "https://api.openai.com/v1",
            "model": "gpt-4",
            "config": {
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        "tasks": {
            "analyze": {
                "description": "Analyze the given input",
                "input": {
                    "text": "string"
                },
                "output": {
                    "summary": "string",
                    "key_points": "string"
                }
            }
        }
    }
    
    spec_file = temp_dir / "test_agent.yaml"
    with open(spec_file, "w") as f:
        yaml.dump(spec, f)
    return spec_file

@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()

def test_init_command(runner, temp_dir, sample_spec_file):
    """Test the init command creates all required files."""
    output_dir = temp_dir / "output"
    result = runner.invoke(app, ["init", "--spec", str(sample_spec_file), "--output", str(output_dir)])
    
    assert result.exit_code == 0
    assert (output_dir / "agent.py").exists()
    assert (output_dir / "README.md").exists()
    assert (output_dir / "requirements.txt").exists()
    assert (output_dir / ".env.example").exists()
    assert (output_dir / "prompts" / "agent_prompt.jinja2").exists()

def test_init_dry_run(runner, temp_dir, sample_spec_file):
    """Test the init command with --dry-run doesn't create files."""
    output_dir = temp_dir / "output"
    result = runner.invoke(app, ["init", "--spec", str(sample_spec_file), "--output", str(output_dir), "--dry-run"])
    
    assert result.exit_code == 0
    assert not output_dir.exists()

def test_update_command(runner, temp_dir, sample_spec_file):
    """Test the update command updates existing files."""
    # First create the initial files
    output_dir = temp_dir / "output"
    runner.invoke(app, ["init", "--spec", str(sample_spec_file), "--output", str(output_dir)])
    
    # Modify the spec file
    with open(sample_spec_file, "r") as f:
        spec = yaml.safe_load(f)
    spec["tasks"]["analyze"]["description"] = "Updated description"
    with open(sample_spec_file, "w") as f:
        yaml.dump(spec, f)
    
    # Run update
    result = runner.invoke(app, ["update", "--spec", str(sample_spec_file), "--output", str(output_dir)])
    
    assert result.exit_code == 0
    content = (output_dir / "agent.py").read_text()
    assert "Updated description" in content

def test_update_nonexistent_dir(runner, temp_dir, sample_spec_file):
    """Test the update command fails on nonexistent directory."""
    output_dir = temp_dir / "nonexistent"
    result = runner.invoke(app, ["update", "--spec", str(sample_spec_file), "--output", str(output_dir)])
    
    print(repr(result.output))
    assert result.exit_code == 1
    # Normalize the output by removing newlines and extra spaces
    normalized_output = " ".join(result.output.split())
    assert "does not exist" in normalized_output 