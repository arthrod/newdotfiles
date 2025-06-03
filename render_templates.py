#!/usr/bin/env python3
"""Render Jinja2 templates with default values for development."""

import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_templates():
    """Render all template files with default values."""
    # Template files that need rendering
    template_files = [
        "src/{{ package_name | default('newdotfiles') }}/__init__.py",
        "src/{{ package_name | default('newdotfiles') }}/cli.py", 
        "pyproject.toml"
    ]
    
    # Create Jinja2 environment
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape()
    )
    
    for template_file in template_files:
        if Path(template_file).exists():
            print(f"Rendering {template_file}")
            
            # Load and render template
            template = env.get_template(template_file)
            rendered = template.render()
            
            # Write back to file
            with open(template_file, 'w') as f:
                f.write(rendered)
            
            print(f"✓ Rendered {template_file}")

if __name__ == "__main__":
    render_templates()