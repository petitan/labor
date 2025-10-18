"""Tests for generic converter module."""

import json
from pathlib import Path

import pytest

from labor.generic_converter import (
    apply_transform,
    convert_with_format,
    expand_repeatable_lists,
    expand_repeatable_tables,
    get_nested_value,
    replace_in_structure,
    set_nested_value,
    substitute_simple_placeholders,
)

# Paths
EMISSION_INPUT_PATH = Path(__file__).parent.parent / "examples" / "emission_calibration_input.json"
TEMPLATE_PATH = Path(__file__).parent.parent / "src" / "labor" / "calibration_template.json"
FORMAT_PATH = Path(__file__).parent.parent / "src" / "labor" / "calibration_format.json"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_nested_value_simple(self):
        """Test getting value from simple path."""
        data = {"procedure_code": "KE-GEM-E-10"}
        assert get_nested_value(data, "procedure_code") == "KE-GEM-E-10"

    def test_get_nested_value_nested(self):
        """Test getting value from nested path."""
        data = {"scope": {"equipment_description": "Test equipment"}}
        assert get_nested_value(data, "scope.equipment_description") == "Test equipment"

    def test_get_nested_value_missing(self):
        """Test getting value with missing path."""
        data = {"procedure_code": "TEST"}
        assert get_nested_value(data, "scope.missing", "default") == "default"

    def test_get_nested_value_array(self):
        """Test getting array value."""
        data = {"references": ["Ref1", "Ref2", "Ref3"]}
        assert get_nested_value(data, "references") == ["Ref1", "Ref2", "Ref3"]

    def test_set_nested_value_simple(self):
        """Test setting value with simple path."""
        data: dict[str, str] = {}
        set_nested_value(data, "procedure_code", "TEST-001")
        assert data == {"procedure_code": "TEST-001"}

    def test_set_nested_value_nested(self):
        """Test setting value with nested path."""
        data: dict[str, dict[str, str]] = {}
        set_nested_value(data, "scope.equipment_description", "Test")
        assert data == {"scope": {"equipment_description": "Test"}}

    def test_replace_in_structure_string(self):
        """Test replacing placeholder in string."""
        result = replace_in_structure("Code: {{CODE}}", "{{CODE}}", "TEST-001")
        assert result == "Code: TEST-001"

    def test_replace_in_structure_dict(self):
        """Test replacing placeholder in dict."""
        obj = {"title": "{{TITLE}}", "code": "{{CODE}}"}
        result = replace_in_structure(obj, "{{CODE}}", "TEST-001")
        assert result == {"title": "{{TITLE}}", "code": "TEST-001"}

    def test_replace_in_structure_list(self):
        """Test replacing placeholder in list."""
        obj = ["{{CODE}}", "Fixed", {"nested": "{{CODE}}"}]
        result = replace_in_structure(obj, "{{CODE}}", "TEST-001")
        assert result == ["TEST-001", "Fixed", {"nested": "TEST-001"}]

    def test_apply_transform_join_with_comma(self):
        """Test join_with_comma transform."""
        value = ["Ref1", "Ref2", "Ref3"]
        result = apply_transform(value, "join_with_comma")
        assert result == "Ref1, Ref2, Ref3"

    def test_apply_transform_standards_description(self):
        """Test standards_description transform."""
        value = [
            {"name": "Standard 1", "accuracy": "0.01%"},
            {"name": "Standard 2", "accuracy": "0.02%"},
        ]
        result = apply_transform(value, "standards_description")
        assert "Standard 1 (Pontosság: 0.01%)" in result
        assert "Standard 2 (Pontosság: 0.02%)" in result

    def test_apply_transform_kmk_parameter_2_label(self):
        """Test kmk_parameter_2_label transform."""
        result = apply_transform(2.0, "kmk_parameter_2_label")
        assert result == "Bővített bizonytalanság (k=2.0)"


class TestPlaceholderSubstitution:
    """Tests for placeholder substitution."""

    def test_substitute_simple_placeholders(self):
        """Test simple placeholder substitution."""
        template = {"title": "{{ELJARAS_CIM}}", "code": "{{ELJARAS_KOD}}"}
        input_data = {"procedure_title": "Test Procedure", "procedure_code": "TEST-001"}
        format_config = {
            "simple_mappings": {
                "{{ELJARAS_CIM}}": "procedure_title",
                "{{ELJARAS_KOD}}": "procedure_code",
            }
        }

        result = substitute_simple_placeholders(template, input_data, format_config)
        assert result["title"] == "Test Procedure"
        assert result["code"] == "TEST-001"

    def test_substitute_array_mappings(self):
        """Test array placeholder substitution."""
        template = {"ranges": ["{{TARTOMANY_1}}", "{{TARTOMANY_2}}"]}
        input_data = {"scope": {"measurement_ranges": ["Range 1", "Range 2", "Range 3"]}}
        format_config = {
            "array_mappings": {
                "scope.measurement_ranges": {"placeholders": ["{{TARTOMANY_1}}", "{{TARTOMANY_2}}"]}
            }
        }

        result = substitute_simple_placeholders(template, input_data, format_config)
        assert result["ranges"] == ["Range 1", "Range 2"]

    def test_substitute_custom_mappings(self):
        """Test custom mappings with transforms."""
        template = {"references": "{{HIVATKOZASOK}}"}
        input_data = {"references": ["Ref1", "Ref2", "Ref3"]}
        format_config = {
            "custom_mappings": {
                "{{HIVATKOZASOK}}": {"source": "references", "transform": "join_with_comma"}
            }
        }

        result = substitute_simple_placeholders(template, input_data, format_config)
        assert result["references"] == "Ref1, Ref2, Ref3"


class TestRepeatableBlocks:
    """Tests for repeatable block expansion."""

    def test_expand_repeatable_tables(self):
        """Test expanding table with variable rows."""
        template = {
            "docjll": [
                {
                    "type": "table",
                    "caption": "Jelölések és mértékegységek",
                    "note": "ISMÉTELHETŐ",
                    "rows": [["{{JELOLES_1}}", "{{SZIMBOLUM_1}}", "{{EGYSEG_1}}"]],
                }
            ]
        }
        input_data = {
            "notations": [
                {"name": "CO", "symbol": "$CO$", "unit": "%"},
                {"name": "CO₂", "symbol": "$CO_2$", "unit": "%"},
                {"name": "HC", "symbol": "$HC$", "unit": "ppm"},
            ]
        }
        format_config = {
            "repeatable_blocks": {
                "notations": {
                    "type": "table",
                    "source": "notations",
                    "identification": {
                        "has_note_containing": "ISMÉTELHETŐ",
                        "has_caption_containing": "Jelölések",
                    },
                    "row_fields": ["name", "symbol", "unit"],
                }
            }
        }

        result = expand_repeatable_tables(template, input_data, format_config)
        rows = result["docjll"][0]["rows"]
        assert len(rows) == 3
        assert rows[0] == ["CO", "$CO$", "%"]
        assert rows[1] == ["CO₂", "$CO_2$", "%"]
        assert rows[2] == ["HC", "$HC$", "ppm"]

    def test_expand_repeatable_lists(self):
        """Test expanding list with variable items."""
        template = {
            "docjll": [
                {
                    "type": "list_unordered",
                    "items": [
                        [
                            {"type": "math", "content": "{{VALTOZO_1}}"},
                            {"type": "text", "content": "{{VALTOZO_1_LEIRAS}}"},
                        ]
                    ],
                }
            ]
        }
        input_data = {
            "calibration_method": {
                "equation_variables": [
                    {"symbol": "h", "description": "mérési hiba", "unit": "%"},
                    {"symbol": "X_m", "description": "mért érték", "unit": "%"},
                ]
            }
        }
        format_config = {
            "repeatable_blocks": {
                "equation_variables": {
                    "type": "list_unordered",
                    "source": "calibration_method.equation_variables",
                    "identification": {"has_items_containing": "{{VALTOZO"},
                    "item_template": [
                        {"type": "math", "content": "{symbol}"},
                        {"type": "text", "content": " -- {description} [{unit}]"},
                    ],
                }
            }
        }

        result = expand_repeatable_lists(template, input_data, format_config)
        items = result["docjll"][0]["items"]
        assert len(items) == 2
        assert items[0][0]["content"] == "h"
        assert items[0][1]["content"] == " -- mérési hiba [%]"
        assert items[1][0]["content"] == "X_m"
        assert items[1][1]["content"] == " -- mért érték [%]"


class TestFullConversion:
    """Tests for full conversion with real data."""

    def test_convert_emission_data(self):
        """Test converting emission calibration data."""
        # This test requires all files to exist
        if not all([EMISSION_INPUT_PATH.exists(), TEMPLATE_PATH.exists(), FORMAT_PATH.exists()]):
            pytest.skip("Required files not found")

        docjl_data = convert_with_format(
            str(EMISSION_INPUT_PATH), str(TEMPLATE_PATH), str(FORMAT_PATH)
        )

        # Check basic structure
        assert "docjll" in docjl_data
        assert len(docjl_data["docjll"]) == 70  # Template has 70 blocks

        # Check no placeholders remain
        docjl_str = json.dumps(docjl_data)
        placeholder_count = docjl_str.count("{{")
        assert placeholder_count == 0, f"Found {placeholder_count} remaining placeholders"

    def test_convert_emission_notations_table(self):
        """Test that notations table is expanded correctly."""
        if not all([EMISSION_INPUT_PATH.exists(), TEMPLATE_PATH.exists(), FORMAT_PATH.exists()]):
            pytest.skip("Required files not found")

        docjl_data = convert_with_format(
            str(EMISSION_INPUT_PATH), str(TEMPLATE_PATH), str(FORMAT_PATH)
        )

        # Find notations table
        notations_table = None
        for block in docjl_data["docjll"]:
            if block.get("type") == "table" and "Jelölések" in block.get("caption", ""):
                notations_table = block
                break

        assert notations_table is not None
        assert len(notations_table["rows"]) == 7  # Emission data has 7 notations

    def test_convert_emission_equation_variables(self):
        """Test that equation variables list is expanded correctly."""
        if not all([EMISSION_INPUT_PATH.exists(), TEMPLATE_PATH.exists(), FORMAT_PATH.exists()]):
            pytest.skip("Required files not found")

        docjl_data = convert_with_format(
            str(EMISSION_INPUT_PATH), str(TEMPLATE_PATH), str(FORMAT_PATH)
        )

        # Find equation variables list
        eq_vars_list = None
        for block in docjl_data["docjll"]:
            if block.get("type") == "list_unordered":
                items = block.get("items", [])
                # Check if first item contains math
                if (
                    items
                    and len(items) >= 6
                    and isinstance(items[0], list)
                    and len(items[0]) > 0
                    and items[0][0].get("type") == "math"
                ):
                    eq_vars_list = block
                    break

        assert eq_vars_list is not None
        assert len(eq_vars_list["items"]) == 6  # Emission data has 6 equation variables

    def test_convert_emission_measurement_results(self):
        """Test that measurement results table is expanded correctly."""
        if not all([EMISSION_INPUT_PATH.exists(), TEMPLATE_PATH.exists(), FORMAT_PATH.exists()]):
            pytest.skip("Required files not found")

        docjl_data = convert_with_format(
            str(EMISSION_INPUT_PATH), str(TEMPLATE_PATH), str(FORMAT_PATH)
        )

        # Find measurement results table
        results_table = None
        for block in docjl_data["docjll"]:
            if block.get("type") == "table" and "eredmény" in block.get("caption", "").lower():
                results_table = block
                break

        assert results_table is not None
        assert len(results_table["rows"]) == 6  # Emission data has 6 measurement points

    def test_convert_emission_validation_criteria(self):
        """Test that validation criteria table is expanded correctly."""
        if not all([EMISSION_INPUT_PATH.exists(), TEMPLATE_PATH.exists(), FORMAT_PATH.exists()]):
            pytest.skip("Required files not found")

        docjl_data = convert_with_format(
            str(EMISSION_INPUT_PATH), str(TEMPLATE_PATH), str(FORMAT_PATH)
        )

        # Find validation criteria table
        validation_table = None
        for block in docjl_data["docjll"]:
            if block.get("type") == "table":
                caption = block.get("caption", "")
                if "kritérium" in caption.lower() or "Validál" in caption:
                    validation_table = block
                    break

        assert validation_table is not None
        assert len(validation_table["rows"]) == 5  # Emission data has 5 validation criteria
