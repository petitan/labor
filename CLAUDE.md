# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based QMS (Quality Management System) document generation system for ISO 17025:2018 compliance. The system converts structured JSON data into LaTeX documents via the docjl format, using a modular architecture with plugin-based transforms and converters.

## Development Environment

### Setup Commands

```bash
# Virtual environment (Python 3.12 required)
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### Testing Commands

```bash
# Run all tests with coverage
pytest

# Run tests with HTML coverage report
pytest --cov --cov-report=html
# View: htmlcov/index.html

# Run specific test file
pytest tests/test_generic_converter.py -xvs

# Run specific test function
pytest tests/test_integration_docjl.py::test_docjl_conversion -xvs
```

### Code Quality Commands

```bash
# Linting (auto-fix enabled)
ruff check --fix .

# Formatting
ruff format .

# Type checking
mypy src

# Run all pre-commit hooks manually
pre-commit run --all-files
```

## Architecture Overview

### Core Components

1. **QMS Module** (`src/labor/qms/`)
   - Modular QMS document system with global + chapter-specific data
   - Build script merges data, templates, and format configs
   - Executable: `build_qms.py` (run from qms directory)

2. **Converters** (`src/labor/converters/`)
   - Plugin-based converter system
   - `BaseConverter`: Common functionality (file I/O, nested data access, placeholder replacement)
   - `QMSConverter`: QMS-specific conversion logic
   - Converters integrate with Transform Registry for data transformations

3. **Transforms** (`src/labor/transforms/`)
   - `TransformRegistry`: Plugin-based transformation system
   - `formatting_helpers.py`: Reusable docjl inline array generators (make_bold_prefix, make_info_box_content, etc.)
   - `common_transforms.py`: General transforms (join, case conversion)
   - `qms_transforms.py`: QMS-specific transforms (format_standard_list, format_document_list)

### Data Flow

```
1. Build Phase:
   global/QMS_global_data.json + chapters/QMS_ch0X_data.json
   → build_qms.py
   → build/QMS_full_input.json + QMS_full_template.json + QMS_full_format.json

2. Conversion Phase:
   build/QMS_full_*.json
   → QMSConverter (uses TransformRegistry)
   → build/QMS_output.json (docjl format)

3. LaTeX Generation:
   QMS_output.json
   → docjl library
   → .tex file
   → pdflatex → PDF
```

## QMS Workflow

### Building QMS Documents

```bash
# 1. Build merged QMS files
cd src/labor/qms
python3 build_qms.py

# 2. Convert to docjl format
cd /home/petitan/labor/src/labor
python3 qms/convert.py

# Output: qms/build/QMS_output.json
```

### QMS File Structure

- `global/QMS_global_data.json`: Shared data (company info, personnel, documents)
- `chapters/QMS_ch0X_data.json`: Chapter-specific content
- `templates/QMS_ch0X_template.json`: docjl structure templates
- `formats/QMS_ch0X_format.json`: Placeholder mapping configs
- `assets/`: Pre-generated figures (PDF/PNG)
- `build/`: Generated output files

## Transform Registry Usage

### Listing Available Transforms

```python
from transforms import TransformRegistry

# List all registered transforms
transforms = TransformRegistry.list_transforms()
# Returns: ['capitalize', 'format_document_list', 'join_with_separator', ...]
```

### Applying Transforms

```python
# Simple transform
result = TransformRegistry.apply('join_with_separator', ['a', 'b'], {'separator': ' + '})
# → 'a + b'

# In format config (JSON)
{
  "mappings": {
    "{{PLACEHOLDER}}": {
      "source": "global.data.field",
      "pipeline": [
        {"transform": "join_with_separator", "params": {"separator": " + "}}
      ]
    }
  }
}
```

### Registering Custom Transforms

```python
from transforms import TransformRegistry

def my_transform(value, params=None):
    # Transform logic
    return processed_value

TransformRegistry.register('my_transform', my_transform)
```

## Formatting Helpers

Helper functions generate docjl inline arrays (formatted text elements):

```python
from transforms import make_bold_prefix, make_info_box_content

# Bold prefix + text
result = make_bold_prefix("NAR-87", "Document title", " -- ")
# → [{'type': 'bold', 'content': 'NAR-87'}, {'type': 'text', 'content': ' -- Document title'}]

# Info box with label-value pairs
fields = {'Label1': 'Value1', 'Label2': 'Value2'}
result = make_info_box_content(fields)
# Generates docjl inline array with bold labels and text values
```

## Important Patterns

### Nested Data Access

The converters use dot-notation for nested data access:

```python
# In format config
"source": "global.company.name"  # Access global.company.name from merged data
"source": "chapters.ch01.scope.objectives"  # Access chapter-specific data
```

### Box Styles (tcolorbox)

Supported box types for formatted content blocks:
- `nahinfo` (blue) - Information, examples
- `nahreq` (green) - Requirements
- `nahalert` (red) - Warnings, common errors
- `nahvalid` (purple) - Validation, audit evidence
- `nahsec` (orange) - Security, data protection

### Running Tests Efficiently

- Use `-xvs` flags: stop on first failure, verbose output, no capture
- Long-running tests may involve PDF generation (5+ minutes)
- Coverage reports are generated in `htmlcov/`

## Configuration

### Ruff Settings (pyproject.toml)
- Target: Python 3.12
- Line length: 100
- Auto-fix enabled for most issues
- Tests excluded from ARG (unused arguments) checks

### MyPy Settings
- Strict type checking enabled
- Tests allow untyped definitions
- Python 3.12 target

### Pytest Settings
- Coverage source: `src/`
- HTML and terminal coverage reports
- Verbose output by default

## Common Issues

### Virtual Environment
Always activate venv before running commands:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Path Issues
- QMS build script must run from `src/labor/qms/` directory
- Converters expect paths relative to project root

### PDF Generation
- Requires pdflatex installed on system
- Asset files must exist in `qms/assets/` before build
- Two pdflatex runs needed for references
