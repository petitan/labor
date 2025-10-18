# Calibration Input Data Schema

## Overview

This document describes the JSON schema for **unformatted calibration procedure input data**. This schema defines the structure for calibration data before it is converted to the docjl format and subsequently to LaTeX/PDF.

## Purpose

The input schema serves as:
- **Data validation** layer before processing
- **Documentation** of required and optional fields
- **Type safety** for calibration procedure data
- **Integration contract** for external systems

## Schema Location

- **Schema file:** `src/labor/calibration_input_schema.json`
- **Example data:** `examples/pressure_gauge_calibration_input.json`
- **Tests:** `tests/test_input_schema.py`

## Schema URL

```
https://petitan.hu/schemas/calibration-input-v1.json
```

## Required Fields

The following fields are **required** for all calibration procedures:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `procedure_code` | string | Unique procedure identifier | `PET-KAL-M-01` |
| `procedure_title` | string | Full procedure title | `Analóg nyomásmérők kalibrálása` |
| `measurement_range` | string | Measurement range with units | `0 - 10 bar` |
| `accuracy_requirement` | string | Required accuracy | `±0.5% teljes skála` |

### Procedure Code Format

The procedure code must follow the pattern: `XXX-XXX-X-NN`

Where:
- `XXX` - Organization code (3 uppercase letters, e.g., `PET`)
- `XXX` - Department code (3 uppercase letters, e.g., `KAL`)
- `X` - Document type (1 uppercase letter, e.g., `M` for method)
- `NN` - Sequential number (2 digits, e.g., `01`)

**Examples:**
- `PET-KAL-M-01` - PeTitan Calibration Method 01
- `PET-KAL-E-05` - PeTitan Calibration Equipment 05

## Optional Sections

### Scope

Defines the scope and applicability of the procedure:

```json
{
  "scope": {
    "equipment_description": "Description of equipment...",
    "measurement_ranges": ["range 1", "range 2"],
    "procedure_type": "Comparison measurement",
    "applicable_to": ["Type A", "Type B"],
    "not_applicable_to": ["Type C"],
    "working_principle": "Description..."
  }
}
```

### Calibration Method

Defines the measurement principle and equations:

```json
{
  "calibration_method": {
    "method_description": "Method description...",
    "measurement_equation": "\\Delta p = p_{mért} - p_{ref}",
    "equation_variables": [
      {
        "symbol": "\\Delta p",
        "description": "Measurement error",
        "unit": "bar"
      }
    ],
    "influence_quantities": {
      "temperature": "±0.01 bar/°C",
      "pressure": "negligible",
      "humidity": "no direct effect"
    }
  }
}
```

### Equipment

Lists all equipment used in calibration:

```json
{
  "equipment": {
    "reference_standards": [
      {
        "name": "Fluke 719Pro",
        "serial_number": "12345678",
        "accuracy": "±0.025% FS",
        "calibration_valid_until": "2024-12-15"
      }
    ],
    "measuring_instruments": ["Instrument 1", "Instrument 2"],
    "auxiliary_equipment": ["Tool 1", "Tool 2"]
  }
}
```

### Environmental Conditions

Specifies required environmental parameters:

```json
{
  "environmental_conditions": {
    "temperature": {
      "min": 20,
      "max": 24,
      "notes": "Continuous monitoring required"
    },
    "humidity": {
      "min": 30,
      "max": 70,
      "notes": "Non-condensing"
    },
    "stabilization_time": "Minimum 2 hours"
  }
}
```

### Uncertainty Budget

Defines uncertainty components and calculations:

```json
{
  "uncertainty_budget": {
    "measurement_point": "10 bar measurement point",
    "components": [
      {
        "source": "Reference standard",
        "value": "0.0025 bar",
        "distribution": "normál",
        "sensitivity": "1.0",
        "contribution": "0.0025 bar"
      }
    ],
    "combined_uncertainty": "0.012 bar",
    "coverage_factor": 2.0,
    "expanded_uncertainty": "0.024 bar",
    "degrees_of_freedom": 50
  }
}
```

### Results

Defines measurement points and results format:

```json
{
  "results": {
    "reporting_format": "Description of reporting format...",
    "measurement_points": [
      {
        "point": "0.0 bar (0%)",
        "result": "$\\Delta p = 0.00 \\pm 0.02$ bar"
      }
    ],
    "example_serial_number": "2024-001"
  }
}
```

### Validation

Procedure validation information:

```json
{
  "validation": {
    "statement": "Validation statement...",
    "validation_date": "2024-12-10",
    "criteria": [
      {
        "criterion": "Measurement uncertainty",
        "requirement": "$U < 0.05$ bar",
        "result": "✓ PASS ($U = 0.024$ bar)"
      }
    ]
  }
}
```

## Usage Examples

### Python Validation

```python
import json
import jsonschema

# Load schema
with open('src/labor/calibration_input_schema.json') as f:
    schema = json.load(f)

# Load input data
with open('my_calibration_data.json') as f:
    data = json.load(f)

# Validate
try:
    jsonschema.validate(instance=data, schema=schema)
    print("✓ Data is valid")
except jsonschema.ValidationError as e:
    print(f"✗ Validation error: {e.message}")
```

### Minimal Valid Example

```json
{
  "procedure_code": "PET-KAL-M-01",
  "procedure_title": "Temperature Sensor Calibration",
  "measurement_range": "0 - 100 °C",
  "accuracy_requirement": "±0.1 °C"
}
```

### Complete Example

See `examples/pressure_gauge_calibration_input.json` for a complete, real-world example.

## Data Types and Formats

### String Formats

- **Date:** ISO 8601 format (`YYYY-MM-DD`)
  - Example: `2025-01-15`
- **DateTime:** ISO 8601 format with time (`YYYY-MM-DDTHH:MM:SSZ`)
  - Example: `2024-11-15T14:30:00Z`
- **LaTeX:** LaTeX formatted strings for equations
  - Example: `\\Delta p = p_{\\text{mért}} - p_{\\text{ref}}`

### Enumerations

- **Distribution types:** `normál`, `egyenletes`, `háromszög`, `téglalap`

## Validation Rules

1. **Procedure code** must match pattern `^[A-Z]{3}-[A-Z]{3}-[A-Z]-[0-9]{2}$`
2. **Procedure title** must be 10-200 characters
3. **Version** must follow semantic versioning pattern `X.Y`
4. **Dates** must be valid ISO 8601 dates
5. **Arrays** must have at least 1 item where specified (`minItems: 1`)

## Integration with docjl

The input data is converted to docjl format through a converter function:

```python
from calibration_converter import convert_input_to_docjl

# Load input data
input_data = load_input_json('my_procedure.json')

# Convert to docjl format
docjl_data = convert_input_to_docjl(input_data)

# Convert to LaTeX
from docjl import MarkdownJsonToDocjl
converter = MarkdownJsonToDocjl()
latex = converter.convert(json.dumps(docjl_data))
```

## Testing

Run schema validation tests:

```bash
pytest tests/test_input_schema.py -v
```

Expected output:
```
15 passed in 0.30s
```

## Schema Versioning

- **Current version:** v1.0
- **Last updated:** 2025-10-18
- **Breaking changes:** Will increment major version
- **Backward compatible changes:** Will increment minor version

## Support

For questions or issues with the schema:
- Check example: `examples/pressure_gauge_calibration_input.json`
- Run tests: `pytest tests/test_input_schema.py -v`
- Review schema: `src/labor/calibration_input_schema.json`

## See Also

- [docjl Documentation](https://github.com/petitan/docjl)
- [ISO/IEC 17025:2018](https://www.iso.org/standard/66912.html)
- [JSON Schema Specification](https://json-schema.org/)
