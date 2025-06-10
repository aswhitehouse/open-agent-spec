"""File generation functions for Open Agent Spec."""
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import json
import openai
from jinja2 import Template
from behavioral_contracts import behavioral_contract
from .utils import map_yaml_type

log = logging.getLogger("oas")

def generate_agent_code(output: Path, spec_data: Dict[str, Any], agent_name: str, class_name: str) -> None:
    """Generate the agent.py file."""
    if (output / "agent.py").exists():
        log.warning("agent.py already exists and will be overwritten")
    
    # Extract task definitions
    tasks = spec_data.get("tasks", {})
    if not tasks:
        log.warning("No tasks defined in spec file")
        return

    # Generate task functions and class methods
    task_functions = []
    class_methods = []
    
    for task_name, task_def in tasks.items():
        # Convert task name to snake_case for function name
        func_name = task_name.replace("-", "_")

        inputs = task_def.get("input", {})
        outputs = task_def.get("output", {})

        # Generate input parameters
        input_params = []
        for param_name, param_type in inputs.items():
            input_params.append(f"{param_name}: {map_yaml_type(param_type)}")

        # Optional runtime parameters
        input_params.extend(["memory: str | None = None", "indicators_summary: str | None = None"])
        
        # Generate return type annotation
        output_type = "Dict[str, Any]"
        if task_def.get("output"):
            output_type = "Dict[str, Any]"  # Could be made more specific based on output schema
        
        # Generate function docstring
        param_lines = [f"        {param_name}: {param_type}" for param_name, param_type in task_def.get("input", {}).items()]
        param_lines.append("        memory: Optional[str] = None")
        param_lines.append("        indicators_summary: Optional[str] = None")

        docstring = f'''"""Process {task_name} task.

    Args:
{chr(10).join(param_lines)}

    Returns:
        {output_type}
    """'''
        
        # Generate function code
        output_json = json.dumps(outputs)

        contract_cfg = task_def.get('contract') or {
            "version": "1.1",
            "description": task_def.get('description', ''),
            "role": agent_name
        }

        task_func = f'''
@behavioral_contract(**{json.dumps(contract_cfg)})
def {func_name}({', '.join(input_params)}) -> {output_type}:
    {docstring}

    task_def = {
        "output": {output_json}
    }

    template_path = Path(__file__).parent / "prompts" / "{task_name}_prompt.jinja2"
    if not template_path.exists():
        template_path = Path(__file__).parent / "prompts" / "agent_prompt.jinja2"

    template = Template(template_path.read_text())
    prompt = template.render(
        input={{ {', '.join(f'"{p}": {p}' for p in inputs.keys())} }},
        memory=memory,
        indicators_summary=indicators_summary
    )

    client = openai.OpenAI(
        base_url="{spec_data['intelligence']['endpoint']}",
        api_key=openai.api_key
    )

    response = client.chat.completions.create(
        model="{spec_data['intelligence']['model']}",
        messages=[
            {{"role": "system", "content": "You are a professional {agent_name}."}},
            {{"role": "user", "content": prompt}}
        ],
        temperature={spec_data['intelligence']['config']['temperature']},
        max_tokens={spec_data['intelligence']['config']['max_tokens']}
    )
    
    result = response.choices[0].message.content

    # Parse the response into the expected output format
    output_dict = {{}}
    output_fields = list(outputs.keys())
    
    # Split response into lines and process each line
    lines = result.strip().split('\\n')
    current_key = None
    current_value = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line starts a new field
        for key in output_fields:
            if line.startswith(key + ":"):
                # Save previous field if exists
                if current_key and current_value:
                    output_dict[current_key] = ' '.join(current_value).strip()
                # Start new field
                current_key = key
                current_value = [line[len(key)+1:].strip()]
                break
        else:
            # If no new field found, append to current value
            if current_key:
                current_value.append(line)
    
    # Save the last field
    if current_key and current_value:
        output_dict[current_key] = ' '.join(current_value).strip()
    
    # Validate all required fields are present
    missing_fields = [field for field in output_fields if field not in output_dict]
    if missing_fields:
        print(f"Warning: Missing output fields: {{missing_fields}}")
        for field in missing_fields:
            output_dict[field] = ""  # Provide empty string for missing fields
    
    return output_dict
'''
        task_functions.append(task_func)
        
        # Generate corresponding class method
        class_method = f'''
    def {func_name}(self, {', '.join(input_params)}) -> {output_type}:
        """Process {task_name} task."""
        return {func_name}({', '.join(param.split(':')[0].split('=')[0].strip() for param in input_params)})
'''
        class_methods.append(class_method)

    # Generate the complete agent code
    first_task_name = next(iter(tasks.keys())) if tasks else None
    agent_code = f'''from typing import Dict, Any, Optional
from pathlib import Path
import openai
import json
from jinja2 import Template
from behavioral_contracts import behavioral_contract

ROLE = "{agent_name.title()}"

{chr(10).join(task_functions)}

class {class_name}:
    def __init__(self, api_key: str | None = None):
        self.model = "{spec_data['intelligence']['model']}"
        if api_key:
            openai.api_key = api_key

{chr(10).join(class_methods)}

def main():
    agent = {class_name}()
    # Example usage
    if "{first_task_name}":
        result = getattr(agent, "{first_task_name}".replace("-", "_"))(
            {', '.join(f'{k}="example_{k}"' for k in tasks[first_task_name].get('input', {}))}
        )
        print(json.dumps(result, indent=2))
    else:
        print("No tasks defined in the spec file")

if __name__ == "__main__":
    main()
'''
    (output / "agent.py").write_text(agent_code)
    log.info("agent.py created")
    log.debug(f"Agent class name generated: {class_name}")

def generate_readme(output: Path, spec_data: Dict[str, Any]) -> None:
    """Generate the README.md file."""
    if (output / "README.md").exists():
        log.warning("README.md already exists and will be overwritten")
    
    # Generate task documentation
    task_docs = []
    for task_name, task_def in spec_data.get("tasks", {}).items():
        task_docs.append(f"### {task_name.title()}\n")
        task_docs.append(f"{task_def.get('description', '')}\n")
        
        task_docs.append("#### Input:")
        for param_name, param_type in task_def.get("input", {}).items():
            task_docs.append(f"- {param_name}: {param_type}")
        
        task_docs.append("\n#### Output:")
        for param_name, param_type in task_def.get("output", {}).items():
            task_docs.append(f"- {param_name}: {param_type}")
        task_docs.append("")
    
    readme_content = f"""# {spec_data['info']['name'].title().replace('-', ' ')}

{spec_data['info']['description']}

## Usage

```bash
pip install -r requirements.txt
cp .env.example .env
python agent.py
```

## Tasks

{chr(10).join(task_docs)}

## Example Usage

```python
from agent import {spec_data['info']['name'].title().replace('-', '')}Agent

agent = {spec_data['info']['name'].title().replace('-', '')}Agent()
# Example usage
task_name = "{next(iter(spec_data.get('tasks', {}).keys()), '')}"
if task_name:
    result = getattr(agent, task_name.replace("-", "_"))(
        {', '.join(f'{k}="example_{k}"' for k in spec_data['tasks'][task_name].get('input', {}))}
    )
    print(result)
```
"""
    (output / "README.md").write_text(readme_content)
    log.info("README.md created")

def generate_requirements(output: Path) -> None:
    """Generate the requirements.txt file."""
    if (output / "requirements.txt").exists():
        log.warning("requirements.txt already exists and will be overwritten")
    
    requirements = """openai>=1.0.0
behavioral-contracts>=0.1.0
python-dotenv>=0.19.0
"""
    (output / "requirements.txt").write_text(requirements)
    log.info("requirements.txt created")

def generate_env_example(output: Path) -> None:
    """Generate the .env.example file."""
    if (output / ".env.example").exists():
        log.warning(".env.example already exists and will be overwritten")
    
    env_content = "OPENAI_API_KEY=your-api-key-here\n"
    (output / ".env.example").write_text(env_content)
    log.info(".env.example created")

def generate_prompt_template(output: Path, spec_data: Dict[str, Any]) -> None:
    """Generate prompt template files, using custom templates when provided."""
    prompts_dir = output / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    default_content = """You are a professional AI agent designed to process tasks according to the Open Agent Spec.

TASK:
Process the following task:

{% for key, value in input.items() %}
{{ key }}: {{ value }}
{% endfor %}

{% if memory %}
MEMORY:\n{{ memory }}
{% endif %}

{% if indicators_summary %}
INDICATORS:\n{{ indicators_summary }}
{% endif %}

"""

    # Top-level template
    prompt_content = spec_data.get("prompt_template", default_content)
    (prompts_dir / "agent_prompt.jinja2").write_text(prompt_content)
    log.info("agent_prompt.jinja2 created" + (" (custom)" if "prompt_template" in spec_data else " (default)"))

    # Task-specific templates
    for task_name, task_def in spec_data.get("tasks", {}).items():
        if "prompt_template" in task_def:
            file_path = prompts_dir / f"{task_name}_prompt.jinja2"
            file_path.write_text(task_def["prompt_template"])
            log.info(f"{file_path.name} created (custom)")
