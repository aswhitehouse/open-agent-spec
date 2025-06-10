"""Validation functions for Open Agent Spec."""
from typing import Tuple

def validate_spec(spec_data: dict) -> Tuple[str, str]:
    """Validate the Open Agent Spec structure and return agent name and class name.
    
    Args:
        spec_data: The parsed YAML spec data
        
    Returns:
        Tuple of (agent_name, class_name)
        
    Raises:
        KeyError: If required fields are missing
        ValueError: If field types are invalid
    """
    try:
        # Check required fields first
        if "info" not in spec_data:
            raise KeyError("Missing required field: info")
        if "intelligence" not in spec_data:
            raise KeyError("Missing required field: intelligence")
            
        info = spec_data["info"]
        intelligence = spec_data["intelligence"]
        
        # Check required info fields
        if "name" not in info:
            raise KeyError("Missing required field: info.name")
        if "description" not in info:
            raise KeyError("Missing required field: info.description")
            
        # Check required intelligence fields
        if "endpoint" not in intelligence:
            raise KeyError("Missing required field: intelligence.endpoint")
        if "model" not in intelligence:
            raise KeyError("Missing required field: intelligence.model")
        if "config" not in intelligence:
            raise KeyError("Missing required field: intelligence.config")
            
        # Validate field types
        if not isinstance(info["name"], str):
            raise ValueError("info.name must be a string")
        if not isinstance(info["description"], str):
            raise ValueError("info.description must be a string")
        if not isinstance(intelligence["endpoint"], str):
            raise ValueError("intelligence.endpoint must be a string")
        if not isinstance(intelligence["model"], str):
            raise ValueError("intelligence.model must be a string")
        if not isinstance(intelligence["config"], dict):
            raise ValueError("intelligence.config must be a dictionary")
            
        agent_name = info["name"].replace("-", "_")
        class_name = agent_name.title().replace("_", "") + "Agent"
        return agent_name, class_name
        
    except KeyError as e:
        raise KeyError(f"Missing required field in spec: {e}")
    except Exception as e:
        raise ValueError(f"Invalid spec format: {e}") 