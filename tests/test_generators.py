"""Tests for the Open Agent Spec generators."""
import pytest
from pathlib import Path
import tempfile
import shutil
from oas_cli.generators import (
    generate_agent_code,
    generate_readme,
    generate_requirements,
    generate_env_example,
    generate_prompt_template
)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_spec():
    """Return a sample valid spec for testing."""
    return {
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

def test_generate_agent_code(temp_dir, sample_spec):
    """Test that agent.py is generated correctly."""
    generate_agent_code(temp_dir, sample_spec, "test_agent", "TestAgentAgent")
    
    agent_file = temp_dir / "agent.py"
    assert agent_file.exists()
    
    content = agent_file.read_text()
    assert "from behavioral_contracts import behavioral_contract" in content
    assert "class TestAgentAgent:" in content
    assert "def analyze(" in content

def test_generate_readme(temp_dir, sample_spec):
    """Test that README.md is generated correctly."""
    generate_readme(temp_dir, sample_spec)
    
    readme_file = temp_dir / "README.md"
    assert readme_file.exists()
    
    content = readme_file.read_text()
    assert "# Test Agent" in content
    assert "## Tasks" in content
    assert "### Analyze" in content

def test_generate_requirements(temp_dir):
    """Test that requirements.txt is generated correctly."""
    generate_requirements(temp_dir)
    
    req_file = temp_dir / "requirements.txt"
    assert req_file.exists()
    
    content = req_file.read_text()
    assert "openai>=" in content
    assert "behavioral-contracts" in content
    assert "python-dotenv>=" in content

def test_generate_env_example(temp_dir):
    """Test that .env.example is generated correctly."""
    generate_env_example(temp_dir)
    
    env_file = temp_dir / ".env.example"
    assert env_file.exists()
    
    content = env_file.read_text()
    assert "OPENAI_API_KEY=" in content

def test_generate_prompt_template(temp_dir):
    """Test that the prompt template is generated correctly."""
    generate_prompt_template(temp_dir)
    
    prompt_file = temp_dir / "prompts" / "agent_prompt.jinja2"
    assert prompt_file.exists()
    
    content = prompt_file.read_text()
    assert "You are a professional AI agent" in content
    assert "TASK:" in content
    assert "INSTRUCTIONS:" in content 