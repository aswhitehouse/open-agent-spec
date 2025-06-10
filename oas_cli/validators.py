"""Validation functions for Open Agent Spec."""
from typing import Tuple, Dict, Any

def validate_task(task_name: str, task_def: Dict[str, Any]) -> None:
    """Validate a task definition.
    
    Args:
        task_name: Name of the task
        task_def: Task definition dictionary
        
    Raises:
        KeyError: If required fields are missing
        ValueError: If field types are invalid
    """
    if "description" not in task_def:
        raise KeyError(f"Missing required field: tasks.{task_name}.description")
    if not isinstance(task_def["description"], str):
        raise ValueError(f"tasks.{task_name}.description must be a string")
        
    # Validate input/output if present
    if "input" in task_def:
        if not isinstance(task_def["input"], dict):
            raise ValueError(f"tasks.{task_name}.input must be a dictionary")
        for param_name, param_type in task_def["input"].items():
            if not isinstance(param_type, str):
                raise ValueError(f"tasks.{task_name}.input.{param_name} type must be a string")
                
    if "output" in task_def:
        if not isinstance(task_def["output"], dict):
            raise ValueError(f"tasks.{task_name}.output must be a dictionary")
        for param_name, param_type in task_def["output"].items():
            if not isinstance(param_type, str):
                raise ValueError(f"tasks.{task_name}.output.{param_name} type must be a string")
                
    # Validate prompt template if present
    if "prompt_template" in task_def:
        if not isinstance(task_def["prompt_template"], str):
            raise ValueError(f"tasks.{task_name}.prompt_template must be a string")

def validate_intelligence_config(config: Dict[str, Any]) -> None:
    """Validate intelligence configuration.
    
    Args:
        config: Intelligence configuration dictionary
        
    Raises:
        ValueError: If config values are invalid
    """
    if not isinstance(config, dict):
        raise ValueError("intelligence.config must be a dictionary")
        
    if "temperature" in config:
        if not isinstance(config["temperature"], (int, float)):
            raise ValueError("intelligence.config.temperature must be a number")
        if not 0 <= config["temperature"] <= 2:
            raise ValueError("intelligence.config.temperature must be between 0 and 2")
            
    if "max_tokens" in config:
        if not isinstance(config["max_tokens"], int):
            raise ValueError("intelligence.config.max_tokens must be an integer")
        if config["max_tokens"] <= 0:
            raise ValueError("intelligence.config.max_tokens must be positive")

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
            
        # Validate intelligence config
        validate_intelligence_config(intelligence["config"])
            
        # Validate tasks if present
        if "tasks" in spec_data:
            if not isinstance(spec_data["tasks"], dict):
                raise ValueError("tasks must be a dictionary")
            for task_name, task_def in spec_data["tasks"].items():
                validate_task(task_name, task_def)
                
        # Validate top-level prompt template if present
        if "prompt_template" in spec_data:
            if not isinstance(spec_data["prompt_template"], str):
                raise ValueError("prompt_template must be a string")
            
        agent_name = info["name"].replace("-", "_")

        # Normalize class name and avoid double "Agent" suffix
        class_base = "".join(word.capitalize() for word in agent_name.split("_"))
        if class_base.lower().endswith("agent"):
            class_name = class_base
        else:
            class_name = class_base + "Agent"

        return agent_name, class_name
        
    except KeyError as e:
        raise KeyError(f"Missing required field in spec: {e}")
    except Exception as e:
        raise ValueError(f"Invalid spec format: {e}") 