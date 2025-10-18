"""Tests for calibration input data schema."""

import json
from pathlib import Path

import jsonschema
import pytest

# Paths
SCHEMA_PATH = Path(__file__).parent.parent / "src" / "labor" / "calibration_input_schema.json"
EXAMPLE_PATH = Path(__file__).parent.parent / "examples" / "pressure_gauge_calibration_input.json"


@pytest.fixture
def input_schema():
    """Load the input data schema."""
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def example_input_data():
    """Load the example input data."""
    with EXAMPLE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class TestInputSchema:
    """Tests for input data JSON schema."""

    def test_schema_file_exists(self):
        """Test that schema file exists."""
        assert SCHEMA_PATH.exists(), f"Schema file not found: {SCHEMA_PATH}"

    def test_schema_is_valid_json(self, input_schema):
        """Test that schema is valid JSON."""
        assert isinstance(input_schema, dict)
        assert "$schema" in input_schema
        assert "type" in input_schema

    def test_schema_has_required_properties(self, input_schema):
        """Test that schema defines required properties."""
        assert "properties" in input_schema
        assert "required" in input_schema

        required_fields = input_schema["required"]
        assert "procedure_code" in required_fields
        assert "procedure_title" in required_fields
        assert "measurement_range" in required_fields
        assert "accuracy_requirement" in required_fields

    def test_schema_procedure_code_pattern(self, input_schema):
        """Test that procedure_code has proper pattern validation."""
        procedure_code = input_schema["properties"]["procedure_code"]
        assert "pattern" in procedure_code
        assert procedure_code["pattern"] == "^[A-Z]{3}-[A-Z]{3}-[A-Z]-[0-9]{2}$"

    def test_example_file_exists(self):
        """Test that example input file exists."""
        assert EXAMPLE_PATH.exists(), f"Example file not found: {EXAMPLE_PATH}"

    def test_example_validates_against_schema(self, input_schema, example_input_data):
        """Test that example data validates against schema."""
        try:
            jsonschema.validate(instance=example_input_data, schema=input_schema)
        except jsonschema.exceptions.ValidationError as e:
            pytest.fail(f"Example data does not validate: {e.message}")

    def test_example_has_all_sections(self, example_input_data):
        """Test that example has all major sections."""
        expected_sections = [
            "procedure_code",
            "procedure_title",
            "scope",
            "calibration_method",
            "equipment",
            "environmental_conditions",
            "preparation",
            "calibration_procedure",
            "uncertainty_budget",
            "results",
            "validation",
        ]

        for section in expected_sections:
            assert section in example_input_data, f"Missing section: {section}"

    def test_example_procedure_code_format(self, example_input_data):
        """Test that example procedure code matches expected format."""
        procedure_code = example_input_data["procedure_code"]
        assert procedure_code == "PET-KAL-M-01"

        # Should match pattern: XXX-XXX-X-NN
        parts = procedure_code.split("-")
        assert len(parts) == 4
        assert len(parts[0]) == 3  # PET
        assert len(parts[1]) == 3  # KAL
        assert len(parts[2]) == 1  # M
        assert len(parts[3]) == 2  # 01

    def test_example_has_uncertainty_budget(self, example_input_data):
        """Test that example includes uncertainty budget."""
        ub = example_input_data["uncertainty_budget"]

        assert "components" in ub
        assert len(ub["components"]) >= 3  # At least 3 components

        # Check first component structure
        first_component = ub["components"][0]
        assert "source" in first_component
        assert "value" in first_component
        assert "distribution" in first_component
        assert "sensitivity" in first_component
        assert "contribution" in first_component

        # Check summary values
        assert "coverage_factor" in ub
        assert ub["coverage_factor"] == 2.0
        assert "expanded_uncertainty" in ub

    def test_example_has_measurement_results(self, example_input_data):
        """Test that example includes measurement results."""
        results = example_input_data["results"]

        assert "measurement_points" in results
        points = results["measurement_points"]

        assert len(points) == 6  # 0%, 20%, 40%, 60%, 80%, 100%

        # Check first point structure
        first_point = points[0]
        assert "point" in first_point
        assert "result" in first_point

        # Check that results contain uncertainty
        assert "pm" in first_point["result"]  # ± symbol

    def test_example_has_validation_criteria(self, example_input_data):
        """Test that example includes validation criteria."""
        validation = example_input_data["validation"]

        assert "statement" in validation
        assert "validation_date" in validation
        assert "criteria" in validation

        criteria = validation["criteria"]
        assert len(criteria) >= 2  # At least 2 criteria

        # Check first criterion structure
        first_criterion = criteria[0]
        assert "criterion" in first_criterion
        assert "requirement" in first_criterion
        assert "result" in first_criterion

    def test_minimal_valid_input(self, input_schema):
        """Test that minimal valid input passes validation."""
        minimal_input = {
            "procedure_code": "PET-KAL-M-01",
            "procedure_title": "Test Calibration Procedure",
            "measurement_range": "0 - 100",
            "accuracy_requirement": "±0.1%",
        }

        try:
            jsonschema.validate(instance=minimal_input, schema=input_schema)
        except jsonschema.exceptions.ValidationError as e:
            pytest.fail(f"Minimal input should be valid: {e.message}")

    def test_invalid_procedure_code_rejected(self, input_schema):
        """Test that invalid procedure code is rejected."""
        invalid_input = {
            "procedure_code": "INVALID-CODE",  # Wrong format
            "procedure_title": "Test Calibration Procedure",
            "measurement_range": "0 - 100",
            "accuracy_requirement": "±0.1%",
        }

        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(instance=invalid_input, schema=input_schema)

    def test_missing_required_field_rejected(self, input_schema):
        """Test that missing required field is rejected."""
        invalid_input = {
            "procedure_code": "PET-KAL-M-01",
            # Missing procedure_title (required)
            "measurement_range": "0 - 100",
            "accuracy_requirement": "±0.1%",
        }

        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(instance=invalid_input, schema=input_schema)

    def test_schema_documentation(self, input_schema):
        """Test that schema includes documentation."""
        assert "title" in input_schema
        assert "description" in input_schema

        # Check that properties have descriptions
        properties = input_schema["properties"]
        for prop_name, prop_schema in properties.items():
            if isinstance(prop_schema, dict):
                assert "description" in prop_schema, f"Property {prop_name} missing description"
