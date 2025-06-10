"""Tests for the Open Agent Spec validators."""
import pytest
from oas_cli.validators import validate_spec

def test_valid_spec():
    """Test that a valid spec returns the correct agent and class names."""
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
    
    agent_name, class_name = validate_spec(spec)
    assert agent_name == "test_agent"
    assert class_name == "TestAgent"

def test_missing_required_fields():
    """Test that missing required fields raise KeyError."""
    spec = {
        "info": {
            "name": "test-agent"
            # Missing description
        },
        "intelligence": {
            "endpoint": "https://api.openai.com/v1",
            "model": "gpt-4",
            "config": {}
        }
    }
    
    with pytest.raises(KeyError):
        validate_spec(spec)

def test_invalid_field_types():
    """Test that invalid field types raise ValueError."""
    spec = {
        "info": {
            "name": 123,  # Should be string
            "description": "A test agent"
        },
        "intelligence": {
            "endpoint": "https://api.openai.com/v1",
            "model": "gpt-4",
            "config": {}
        }
    }
    
    with pytest.raises(ValueError):
        validate_spec(spec) 