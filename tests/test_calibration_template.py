"""Unit tests for calibration template structure validation."""

import json
from pathlib import Path

import pytest

# Test data paths
TEMPLATE_PATH = Path(__file__).parent.parent / "src" / "labor" / "calibration_template.json"
SCHEMA_PATH = Path(__file__).parent.parent / "src" / "labor" / "calibration_schema.json"


def test_template_file_exists():
    """Test that the template file exists."""
    assert TEMPLATE_PATH.exists(), f"Template file not found: {TEMPLATE_PATH}"


def test_template_is_valid_json():
    """Test that the template is valid JSON."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), "Template must be a JSON object"


def test_template_has_docjll_root():
    """Test that template has 'docjll' root key."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    assert "docjll" in data, "Template must have 'docjll' root key"


def test_template_docjll_is_array():
    """Test that 'docjll' is an array."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data["docjll"], list), "'docjll' must be an array"


def test_template_has_blocks():
    """Test that template has at least one block."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["docjll"]) > 0, "Template must have at least one block"


def test_all_blocks_are_objects():
    """Test that all blocks are objects."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    for i, block in enumerate(data["docjll"]):
        assert isinstance(block, dict), f"Block {i} must be an object"


def test_all_blocks_have_type():
    """Test that all blocks have a 'type' field."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    for i, block in enumerate(data["docjll"]):
        assert "type" in block, f"Block {i} must have a 'type' field"


def test_block_types_are_valid():
    """Test that all block types are valid docjl types."""
    valid_types = {
        "heading",
        "paragraph",
        "table",
        "list_ordered",
        "list_unordered",
        "equation",
        "code_block",
        "quote",
        "horizontal_rule",
        "image",
    }

    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    for i, block in enumerate(data["docjll"]):
        block_type = block.get("type")
        assert (
            block_type in valid_types
        ), f"Block {i} has invalid type '{block_type}'. Valid types: {valid_types}"


def test_template_has_placeholders():
    """Test that template contains placeholder variables."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        content = f.read()

    # Should contain at least some placeholder patterns
    assert (
        "{{" in content and "}}" in content
    ), "Template should contain placeholder variables in {{VARIABLE}} format"


def test_template_has_heading_blocks():
    """Test that template has heading blocks."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    heading_blocks = [b for b in data["docjll"] if b.get("type") == "heading"]
    assert len(heading_blocks) > 0, "Template should have at least one heading block"


def test_template_has_table_blocks():
    """Test that template has table blocks."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    table_blocks = [b for b in data["docjll"] if b.get("type") == "table"]
    assert len(table_blocks) > 0, "Template should have at least one table block"


def test_template_has_paragraph_blocks():
    """Test that template has paragraph blocks."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    paragraph_blocks = [b for b in data["docjll"] if b.get("type") == "paragraph"]
    assert len(paragraph_blocks) > 0, "Template should have at least one paragraph block"


def test_template_has_list_blocks():
    """Test that template has list blocks."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    list_blocks = [b for b in data["docjll"] if b.get("type") in ("list_ordered", "list_unordered")]
    assert len(list_blocks) > 0, "Template should have at least one list block"


def test_heading_blocks_have_required_fields():
    """Test that heading blocks have required fields."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    heading_blocks = [b for b in data["docjll"] if b.get("type") == "heading"]
    for block in heading_blocks:
        assert "level" in block, "Heading block must have 'level' field"
        assert "content" in block, "Heading block must have 'content' field"


def test_table_blocks_have_required_fields():
    """Test that table blocks have required fields."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    table_blocks = [b for b in data["docjll"] if b.get("type") == "table"]
    for block in table_blocks:
        assert (
            "headers" in block or "rows" in block
        ), "Table block must have 'headers' or 'rows' field"


@pytest.mark.skipif(not SCHEMA_PATH.exists(), reason="Schema file not created yet")
def test_schema_validates_template():
    """Test that the JSON schema validates the template."""
    import jsonschema

    with SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)

    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        template = json.load(f)

    # Should not raise ValidationError
    jsonschema.validate(template, schema)
