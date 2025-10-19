"""Generic converter for calibration procedures using format configuration.

This module provides a universal converter that works with ANY calibration procedure type.
It reads format configuration from calibration_format.json and applies it to input data.
"""

import copy
import json
from pathlib import Path
from typing import Any


def get_nested_value(data: dict, json_path: str, default: Any = "") -> Any:
    """
    Get value from nested dictionary using dot notation.

    Args:
        data: Input dictionary
        json_path: Path like "scope.equipment_description" or "references"
        default: Default value if path not found

    Returns:
        Value at the path, or default if not found

    Examples:
        >>> get_nested_value({"a": {"b": "value"}}, "a.b")
        'value'
        >>> get_nested_value({"a": 1}, "x.y.z", "default")
        'default'
    """
    if not json_path:
        return default

    keys = json_path.split(".")
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current if current is not None else default


def set_nested_value(data: dict, json_path: str, value: Any) -> None:
    """
    Set value in nested dictionary using dot notation.

    Args:
        data: Dictionary to modify
        json_path: Path like "scope.equipment_description"
        value: Value to set
    """
    keys = json_path.split(".")
    current = data

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


def is_inline_array_substitution(content: str, placeholder: str, value: Any) -> bool:
    """
    Check if this is an inline array substitution case.

    An inline array substitution occurs when:
    1. The content is EXACTLY the placeholder (e.g., "{symbol}")
    2. The value is a list (inline array structure)

    Args:
        content: Template part content
        placeholder: Placeholder string (e.g., "{symbol}")
        value: Field value from input data

    Returns:
        True if this should be replaced with inline array

    Example:
        >>> is_inline_array_substitution("{symbol}", "{symbol}", [{"type": "math", "content": "x"}])
        True
        >>> is_inline_array_substitution("{symbol}", "{symbol}", "x")
        False
        >>> is_inline_array_substitution("Text {symbol}", "{symbol}", [{"type": "math"}])
        False
    """
    return content.strip() == placeholder and isinstance(value, list)


def convert_table_cell_value(value: Any) -> str | list[Any]:
    """
    Convert a value for table cell usage.

    Preserves inline array structure (lists) as-is for docjl rendering.
    Converts all other types to strings.

    Args:
        value: Cell value from input data

    Returns:
        Inline array (list) if value is a list, otherwise string

    Example:
        >>> convert_table_cell_value([{"type": "math", "content": "x"}])
        [{'type': 'math', 'content': 'x'}]
        >>> convert_table_cell_value("text")
        'text'
        >>> convert_table_cell_value(42)
        '42'
    """
    if isinstance(value, list):
        return value  # Preserve inline array structure
    return str(value)  # Convert to string for all other types


def replace_in_structure(obj: Any, placeholder: str, value: str) -> Any:
    """
    Recursively replace placeholder in any data structure.

    Args:
        obj: Object to search (dict, list, str, or primitive)
        placeholder: Placeholder to find (e.g., "{{ELJARAS_KOD}}")
        value: Value to replace with

    Returns:
        Object with replacements made
    """
    if isinstance(obj, dict):
        return {k: replace_in_structure(v, placeholder, value) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_in_structure(item, placeholder, value) for item in obj]
    elif isinstance(obj, str):
        return obj.replace(placeholder, str(value))
    else:
        return obj


def apply_transform(value: Any, transform: str, context: dict | None = None) -> str:
    """
    Apply transformation to a value.

    Args:
        value: Value to transform
        transform: Transform name
        context: Additional context for transformation (reserved for future use)

    Returns:
        Transformed string value
    """
    _ = context  # Reserved for future use
    if transform == "join_with_comma":
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value)

    elif transform == "standards_description":
        if isinstance(value, list):
            lines = []
            for std in value:
                name = std.get("name", "")
                accuracy = std.get("accuracy", "")
                lines.append(f"{name} (Pontosság: {accuracy})")
            return "\n".join(lines)
        return str(value)

    elif transform == "kmk_parameter_2_label":
        # value is coverage_factor
        k = value if value else 2.0
        return f"Bővített bizonytalanság (k={k})"

    return str(value)


def substitute_simple_placeholders(
    template_data: dict, input_data: dict, format_config: dict
) -> dict:
    """
    Substitute simple 1:1 placeholder mappings.

    Args:
        template_data: Template with placeholders
        input_data: Input calibration data
        format_config: Format configuration

    Returns:
        Template with simple placeholders replaced
    """
    result = copy.deepcopy(template_data)

    # Simple mappings
    for placeholder, json_path in format_config.get("simple_mappings", {}).items():
        value = get_nested_value(input_data, json_path, "")
        result = replace_in_structure(result, placeholder, value)

    # Array mappings (fixed-size arrays)
    for json_path, config in format_config.get("array_mappings", {}).items():
        array_data = get_nested_value(input_data, json_path, [])
        placeholders = config.get("placeholders", [])

        for i, placeholder in enumerate(placeholders):
            value = array_data[i] if i < len(array_data) else ""
            result = replace_in_structure(result, placeholder, value)

    # Custom mappings (with transforms)
    for placeholder, config in format_config.get("custom_mappings", {}).items():
        source_type = config.get("source", "")

        if source_type == "static":
            value = config.get("value", "")
        else:
            value = get_nested_value(input_data, config.get("source", ""), "")

        transform = config.get("transform")
        if transform:
            value = apply_transform(value, transform, input_data)

        result = replace_in_structure(result, placeholder, value)

    return result


def _matches_table_identification(block: dict, identification: dict) -> bool:
    """
    Check if table block matches identification criteria.

    Args:
        block: Table block to check
        identification: Identification criteria (has_note_containing, has_caption_containing)

    Returns:
        True if block matches all criteria
    """
    note = block.get("note", "")
    caption = block.get("caption", "")

    note_match = (
        "has_note_containing" not in identification or identification["has_note_containing"] in note
    )
    caption_match = (
        "has_caption_containing" not in identification
        or identification["has_caption_containing"] in caption
    )

    return note_match and caption_match


def _find_table_block(docjll_blocks: list[dict], identification: dict) -> int | None:
    """
    Find matching table block index in docjll based on identification criteria.

    Args:
        docjll_blocks: List of docjll blocks
        identification: Identification criteria

    Returns:
        Index of matching block, or None if not found
    """
    for i, block in enumerate(docjll_blocks):
        if block.get("type") != "table":
            continue

        if _matches_table_identification(block, identification):
            return i

    return None


def _build_table_rows(source_data: list[dict], row_fields: list[str]) -> list[list[Any]]:
    """
    Build table rows from source data.

    Args:
        source_data: List of data items
        row_fields: Field names for each column

    Returns:
        List of table rows (each row is a list of cell values)
    """
    new_rows: list[list[Any]] = []

    for item in source_data:
        row: list[str | list[Any]] = []
        for field in row_fields:
            value = item.get(field, "")
            row.append(convert_table_cell_value(value))
        new_rows.append(row)

    return new_rows


def expand_repeatable_tables(template_data: dict, input_data: dict, format_config: dict) -> dict:
    """
    Expand tables with variable number of rows based on input data.

    Args:
        template_data: Template with table blocks
        input_data: Input calibration data
        format_config: Format configuration

    Returns:
        Template with expanded table rows
    """
    result = copy.deepcopy(template_data)

    for _block_name, block_config in format_config.get("repeatable_blocks", {}).items():
        if block_config.get("type") != "table":
            continue

        # Get source data
        source_path = block_config.get("source", "")
        source_data = get_nested_value(input_data, source_path, [])
        if not source_data:
            continue

        # Find matching table block in template
        identification = block_config.get("identification", {})
        row_fields = block_config.get("row_fields", [])

        block_index = _find_table_block(result.get("docjll", []), identification)
        if block_index is None:
            continue

        # Build and replace rows
        new_rows = _build_table_rows(source_data, row_fields)
        result["docjll"][block_index]["rows"] = new_rows

    return result


def _find_list_block(docjll_blocks: list[dict], identification: dict) -> int | None:
    """
    Find matching list block index in docjll based on identification criteria.

    Args:
        docjll_blocks: List of docjll blocks
        identification: Identification criteria (e.g., has_items_containing)

    Returns:
        Index of matching block, or None if not found
    """
    for i, block in enumerate(docjll_blocks):
        if block.get("type") != "list_unordered":
            continue

        # Check identification criteria
        items = block.get("items", [])
        items_str = json.dumps(items)

        if (
            "has_items_containing" in identification
            and identification["has_items_containing"] in items_str
        ):
            return i

    return None


def _process_template_part(
    template_part: dict, item_data: dict
) -> tuple[list[dict] | None, dict | None]:
    """
    Process a single template part with item data.

    Args:
        template_part: Template part to process
        item_data: Data for this item

    Returns:
        Tuple of (inline_array_elements, processed_part)
        - If inline array substitution: (array_elements, None)
        - If normal substitution: (None, processed_part)
    """
    part = copy.deepcopy(template_part)

    if "content" not in part:
        return (None, part)

    content = part["content"]

    # Check for inline array substitution
    for field, value in item_data.items():
        placeholder = f"{{{field}}}"

        if is_inline_array_substitution(content, placeholder, value):
            # Return inline array elements (list of dicts)
            return (value, None)

    # Normal placeholder replacement
    for field, value in item_data.items():
        placeholder = f"{{{field}}}"
        value_str = str(value) if not isinstance(value, list) else json.dumps(value)
        content = content.replace(placeholder, value_str)

    part["content"] = content
    return (None, part)


def _build_list_item(item_template: list[dict], item_data: dict) -> list[dict]:
    """
    Build a list item from template and data.

    Args:
        item_template: Template for list item
        item_data: Data for this item

    Returns:
        Processed list item (list of dicts)
    """
    new_item = []

    for template_part in item_template:
        inline_array, processed_part = _process_template_part(template_part, item_data)

        if inline_array is not None:
            # Inline array substitution: extend with array elements
            new_item.extend(inline_array)
        elif processed_part is not None:
            # Normal part: append
            new_item.append(processed_part)

    return new_item


def expand_repeatable_lists(template_data: dict, input_data: dict, format_config: dict) -> dict:
    """
    Expand unordered lists with variable number of items based on input data.

    Args:
        template_data: Template with list blocks
        input_data: Input calibration data
        format_config: Format configuration

    Returns:
        Template with expanded list items
    """
    result = copy.deepcopy(template_data)

    for _block_name, block_config in format_config.get("repeatable_blocks", {}).items():
        if block_config.get("type") != "list_unordered":
            continue

        # Get source data
        source_path = block_config.get("source", "")
        source_data = get_nested_value(input_data, source_path, [])
        if not source_data:
            continue

        # Find matching list block in template
        identification = block_config.get("identification", {})
        item_template = block_config.get("item_template", [])

        block_index = _find_list_block(result.get("docjll", []), identification)
        if block_index is None:
            continue

        # Build new items from source data
        new_items = [_build_list_item(item_template, item_data) for item_data in source_data]

        # Replace items in result
        result["docjll"][block_index]["items"] = new_items

    return result


def convert_with_format(
    input_json_path: str, template_json_path: str, format_json_path: str
) -> dict:
    """
    Convert calibration input to docjl format using format configuration.

    This is the main entry point for the generic converter. It works with ANY
    calibration procedure type by reading mapping rules from the format file.

    Args:
        input_json_path: Path to calibration input data (e.g., emission_calibration_input.json)
        template_json_path: Path to docjl template (calibration_template.json)
        format_json_path: Path to format configuration (calibration_format.json)

    Returns:
        docjl format with all placeholders substituted and arrays expanded

    Example:
        >>> docjl_data = convert_with_format(
        ...     'examples/emission_calibration_input.json',
        ...     'src/labor/calibration_template.json',
        ...     'src/labor/calibration_format.json'
        ... )
        >>> # Now convert to LaTeX:
        >>> from docjl import MarkdownJsonToDocjl
        >>> converter = MarkdownJsonToDocjl()
        >>> latex = converter.convert(json.dumps(docjl_data))
    """
    # Load files
    with Path(input_json_path).open(encoding="utf-8") as f:
        input_data = json.load(f)

    with Path(template_json_path).open(encoding="utf-8") as f:
        template_data = json.load(f)

    with Path(format_json_path).open(encoding="utf-8") as f:
        format_config = json.load(f)

    # Step 1: Substitute simple placeholders
    result = substitute_simple_placeholders(template_data, input_data, format_config)

    # Step 2: Expand repeatable tables
    result = expand_repeatable_tables(result, input_data, format_config)

    # Step 3: Expand repeatable lists
    result = expand_repeatable_lists(result, input_data, format_config)

    return result
