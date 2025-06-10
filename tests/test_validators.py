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

def test_invalid_task_input():
    """Test that invalid task input raises ValueError."""
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
                    "text": 123  # Should be string
                },
                "output": {
                    "summary": "string",
                    "key_points": "string"
                }
            }
        }
    }
    
    with pytest.raises(ValueError):
        validate_spec(spec)

def test_invalid_intelligence_config():
    """Test that invalid intelligence config raises ValueError."""
    spec = {
        "info": {
            "name": "test-agent",
            "description": "A test agent"
        },
        "intelligence": {
            "endpoint": "https://api.openai.com/v1",
            "model": "gpt-4",
            "config": {
                "temperature": 3.0,  # Should be between 0 and 2
                "max_tokens": 1000
            }
        }
    }
    
    with pytest.raises(ValueError):
        validate_spec(spec)

def test_custom_prompt_template():
    """Test that custom prompt templates are validated correctly."""
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
        "prompt_template": "Custom template content",
        "tasks": {
            "analyze": {
                "description": "Analyze the given input",
                "input": {
                    "text": "string"
                },
                "output": {
                    "summary": "string",
                    "key_points": "string"
                },
                "prompt_template": "Custom task template content"
            }
        }
    }
    
    agent_name, class_name = validate_spec(spec)
    assert agent_name == "test_agent"
    assert class_name == "TestAgent" 