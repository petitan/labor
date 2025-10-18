# Labor Project - Calibration Workflow Documentation

## CRITICAL REMINDER FOR CLAUDE

**WHEN USER ASKS TO GENERATE PDF FROM INPUT DATA:**

1. **ALWAYS use the generic converter** - don't just convert template with placeholders!
2. **The complete workflow is:**
   - Load input JSON (e.g., `emission_calibration_input.json`)
   - Load format config JSON (`calibration_format.json`)
   - Load template JSON (`calibration_template.json`)
   - **Run generic converter to substitute placeholders with real data**
   - Convert substituted docjl to LaTeX
   - Compile to PDF with `TEXINPUTS=./latex//:`

3. **DON'T** just convert the template alone - that leaves {{PLACEHOLDERS}}!
4. **DO** use the generic converter first to get real data!
5. **UNIVERSAL**: The generic converter works with ANY calibration procedure type!

## Project Structure

```
labor/
├── examples/
│   ├── emission_calibration_input.json       # Emission input data
│   └── pressure_gauge_calibration_input.json # Pressure gauge input data
│
├── src/labor/
│   ├── calibration_template.json             # General template with {{PLACEHOLDERS}}
│   ├── calibration_format.json               # Universal format configuration
│   ├── calibration_input_schema.json         # JSON schema for input validation
│   ├── generic_converter.py                  # Universal converter: input + format + template → docjl
│   └── emission_converter.py                 # Legacy converter (deprecated - use generic_converter.py)
│
├── latex/
│   └── petitanmk.cls                         # Custom LaTeX document class
│
└── tests/
    ├── test_calibration_template.py          # Template structure tests
    ├── test_emission_calibration.py          # Emission data tests
    ├── test_input_schema.py                  # Schema validation tests
    └── test_integration_docjl.py             # PDF generation tests
```

## Complete Workflow Steps

### Step 1: Input Data Preparation
- Input JSON contains unformatted calibration procedure data
- Must validate against `calibration_input_schema.json`
- Example: `examples/emission_calibration_input.json`

### Step 2: Placeholder Substitution (UNIVERSAL)
```python
from labor.generic_converter import convert_with_format

# Convert input data to docjl format with substituted placeholders
# Works with ANY calibration procedure type!
docjl_data = convert_with_format(
    'examples/emission_calibration_input.json',
    'src/labor/calibration_template.json',
    'src/labor/calibration_format.json'
)
```

### Step 3: LaTeX Generation
```python
from docjl import MarkdownJsonToDocjl
import json

converter = MarkdownJsonToDocjl()
latex = converter.convert(json.dumps(docjl_data))

with open('output.tex', 'w', encoding='utf-8') as f:
    f.write(latex)
```

### Step 4: PDF Compilation
```bash
export TEXINPUTS=./latex//:
pdflatex -interaction=nonstopmode output.tex
```

## Key Files and Their Purpose

### `calibration_template.json`
- **General template** used for ALL calibration types
- Contains {{PLACEHOLDERS}} like `{{PROCEDURE_CODE}}`, `{{ELJARAS_CIM}}`
- docjl format with `docjll` key (NOT `blocks`!)
- 70 blocks defining document structure

### `generic_converter.py` (RECOMMENDED)
- **Universal converter** works with ANY calibration procedure type
- **Configuration-driven**: No hardcoded procedure-specific logic
- **Reads format rules** from `calibration_format.json`
- **Three-step process:**
  1. Substitute simple placeholders (1:1 mappings)
  2. Expand repeatable tables (dynamic row generation)
  3. Expand repeatable lists (dynamic item generation)
- **LaTeX escaping** handled by docjl library
- Returns docjl format ready for LaTeX conversion

### `emission_converter.py` (LEGACY - DEPRECATED)
- Old emission-specific converter
- Use `generic_converter.py` instead!

### Input JSON Schema
- Required fields: `procedure_code`, `procedure_title`, `measurement_range`, `accuracy_requirement`
- Optional sections: scope, calibration_method, equipment, uncertainty_budget, results, validation
- Procedure code pattern: `^[A-Z]{2,3}-[A-Z]{3}-[A-Z]-[0-9]{2}$` (relaxed for emission data)

## LaTeX Special Character Escaping

**CRITICAL:** Input data may contain LaTeX special characters that must be escaped:

- `%` → `\%` (comment character)
- `&` → `\&` (alignment character)
- `#` → `\#` (parameter character)
- `_` → `\_` (subscript character)

**Exception:** Don't escape if string contains:
- `$` (already LaTeX math)
- `\\` (already LaTeX command)
- Starts with `\` (already LaTeX command)

The `emission_converter.py` handles this automatically.

## PDF Compilation Requirements

1. **TEXINPUTS environment variable** must include `./latex//:` to find `petitanmk.cls`
2. **petitanmk.cls** class file must be in `latex/` directory
3. Use `export TEXINPUTS=./latex//:` before running pdflatex
4. Or inline: `TEXINPUTS=./latex//: pdflatex file.tex` (note the space after colon!)

## Example: Complete PDF Generation (UNIVERSAL)

```python
import json
import sys
sys.path.insert(0, 'src')

from labor.generic_converter import convert_with_format
from docjl import MarkdownJsonToDocjl

# Step 1: Convert input to docjl with generic converter
# Works with emission, pressure gauge, or ANY calibration procedure!
docjl_data = convert_with_format(
    'examples/emission_calibration_input.json',    # Input data
    'src/labor/calibration_template.json',         # Template structure
    'src/labor/calibration_format.json'            # Format configuration
)

# Step 2: Convert to LaTeX
converter = MarkdownJsonToDocjl()
latex = converter.convert(json.dumps(docjl_data))

# Step 3: Save LaTeX
with open('calibration_output.tex', 'w', encoding='utf-8') as f:
    f.write(latex)

print('✓ LaTeX saved: calibration_output.tex')
print(f'  0 placeholders remaining')
```

Then compile:
```bash
export TEXINPUTS=./latex//:
pdflatex -interaction=nonstopmode emission_calibration_final.tex
```

Result: `emission_calibration_final.pdf` (6 pages, ~158 KB)

## Test Status

- **Total tests:** 87
- **Passing:** 87
- **Skipped:** 2 (PDF generation tests without petitanmk.cls)
- **Coverage:** 96% generic_converter.py, 60% overall

## Common Mistakes to Avoid

1. ❌ **Converting template directly without substitution**
   - This leaves {{PLACEHOLDERS}} in the output
   - Always use converter first!

2. ❌ **Forgetting TEXINPUTS**
   - PDF compilation will fail: "File petitanmk.cls not found"
   - Always set: `export TEXINPUTS=./latex//:`

3. ❌ **Not escaping special characters**
   - LaTeX will fail on `%`, `&`, `#`, `_` in data
   - Use `escape_latex()` function in converter

4. ❌ **Wrong template key name**
   - Template uses `docjll` key, not `blocks`
   - Check: `assert "docjll" in template`

## Emission Calibration Specifics

- **Procedure code:** `KE-GEM-E-10` (non-standard pattern)
- **Gas components:** CO, CO₂, HC (propane C₃H₈)
- **Reference standards:** 6 certified gas mixtures
- **Measurement points:** 6 (2 per component)
- **Special characters:** CO₂ (subscript), C₃H₈ (subscript)
- **Regulatory references:** KHVM rendelet, ILAC G8-09/2019, EA-4/02, ISO/IEC 17025:2018

## Quick Reference Commands

```bash
# Run all tests
venv/bin/pytest tests/ -v

# Run emission tests only
venv/bin/pytest tests/test_emission_calibration.py -v

# Validate input against schema
venv/bin/python -c "
import json
import jsonschema
schema = json.load(open('src/labor/calibration_input_schema.json'))
data = json.load(open('examples/emission_calibration_input.json'))
jsonschema.validate(data, schema)
print('✓ Valid')
"

# Generate emission PDF (complete workflow)
venv/bin/python -c "
import json, sys
sys.path.insert(0, 'src')
from labor.emission_converter import convert_emission_to_docjl
from docjl import MarkdownJsonToDocjl

docjl_data = convert_emission_to_docjl(
    'examples/emission_calibration_input.json',
    'src/labor/calibration_template.json'
)
converter = MarkdownJsonToDocjl()
latex = converter.convert(json.dumps(docjl_data))
with open('emission_output.tex', 'w', encoding='utf-8') as f:
    f.write(latex)
" && export TEXINPUTS=./latex//: && pdflatex -interaction=nonstopmode emission_output.tex

# Check PDF
pdfinfo emission_output.pdf
pdftotext emission_output.pdf - | grep "KE-GEM-E-10"
```

## Dependencies

- **Python:** 3.12
- **docjl:** Editable install from `/home/petitan/docjl`
- **jsonschema:** >=4.0.0
- **pytest:** For testing
- **LaTeX:** pdflatex with Hungarian babel support

## File Locations

- **Virtual environment:** `venv/`
- **Source code:** `src/labor/`
- **Tests:** `tests/`
- **Examples:** `examples/`
- **LaTeX class:** `latex/petitanmk.cls`
- **Documentation:** `docs/`

## Remember!

**THE WORKFLOW IS ALWAYS:**
1. Input JSON + Format JSON + Template JSON → **Generic Converter** → docjl with real data
2. docjl → MarkdownJsonToDocjl → LaTeX
3. LaTeX → pdflatex (with TEXINPUTS) → PDF

**NEVER skip step 1!** Always use the **generic_converter.py** to substitute placeholders!

## Generic Converter Architecture

**Key Innovation**: Universal, configuration-driven converter that works with ANY calibration procedure type.

**Three inputs:**
1. **Input JSON**: Calibration data (procedure-specific)
2. **Format JSON**: Mapping rules (universal for all procedures)
3. **Template JSON**: Document structure with placeholders

**Three-step processing:**
1. **Simple substitution**: {{PLACEHOLDER}} → value (via `simple_mappings`, `array_mappings`, `custom_mappings`)
2. **Table expansion**: Dynamic row generation (via `repeatable_blocks` type=table)
3. **List expansion**: Dynamic item generation (via `repeatable_blocks` type=list_unordered)

**Benefits:**
- ✅ **No hardcoded logic**: All mappings in configuration file
- ✅ **Procedure-agnostic**: Works with emission, pressure gauge, or future procedure types
- ✅ **No "caption searching cheating"**: Uses explicit block identification
- ✅ **Maintainable**: Change mappings without touching code
