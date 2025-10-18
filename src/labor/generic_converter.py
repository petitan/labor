"""Generic converter for calibration procedures using format configuration.

This module provides a universal converter that works with ANY calibration procedure type.
It reads format configuration from calibration_format.json and applies it to input data.
"""

import json
import copy
from pathlib import Path
from typing import Any, Dict, List, Union


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

    keys = json_path.split('.')
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
    keys = json_path.split('.')
    current = data

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


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


def apply_transform(value: Any, transform: str, context: dict = None) -> str:
    """
    Apply transformation to a value.

    Args:
        value: Value to transform
        transform: Transform name
        context: Additional context for transformation

    Returns:
        Transformed string value
    """
    if transform == "join_with_comma":
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value)

    elif transform == "standards_description":
        if isinstance(value, list):
            lines = []
            for std in value:
                name = std.get('name', '')
                accuracy = std.get('accuracy', '')
                lines.append(f"{name} (Pontosság: {accuracy})")
            return "\n".join(lines)
        return str(value)

    elif transform == "kmk_parameter_2_label":
        # value is coverage_factor
        k = value if value else 2.0
        return f"Bővített bizonytalanság (k={k})"

    return str(value)


def substitute_simple_placeholders(template_data: dict, input_data: dict, format_config: dict) -> dict:
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

    for block_name, block_config in format_config.get("repeatable_blocks", {}).items():
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

        for i, block in enumerate(result.get('docjll', [])):
            if block.get('type') != 'table':
                continue

            # Check identification criteria
            note = block.get('note', '')
            caption = block.get('caption', '')

            matches = True
            if 'has_note_containing' in identification:
                if identification['has_note_containing'] not in note:
                    matches = False
            if 'has_caption_containing' in identification:
                if identification['has_caption_containing'] not in caption:
                    matches = False

            if not matches:
                continue

            # Found matching table - expand rows
            new_rows = []
            for item in source_data:
                row = []
                for field in row_fields:
                    value = item.get(field, "")
                    # Megőrizzük az inline array struktúrát (lista)
                    # Ha value lista (inline array), akkor NEM konvertáljuk string-re!
                    if isinstance(value, list):
                        row.append(value)  # Inline array megőrzése
                    else:
                        row.append(str(value))  # String konverzió csak nem-lista esetén
                new_rows.append(row)

            result['docjll'][i]['rows'] = new_rows
            break

    return result


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

    for block_name, block_config in format_config.get("repeatable_blocks", {}).items():
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

        for i, block in enumerate(result.get('docjll', [])):
            if block.get('type') != 'list_unordered':
                continue

            # Check identification criteria
            items = block.get('items', [])
            items_str = json.dumps(items)

            matches = True
            if 'has_items_containing' in identification:
                if identification['has_items_containing'] not in items_str:
                    matches = False

            if not matches:
                continue

            # Found matching list - expand items
            new_items = []
            for item_data in source_data:
                # Build item from template
                new_item = []
                for template_part in item_template:
                    part = copy.deepcopy(template_part)

                    # Replace {field} placeholders with actual data
                    if 'content' in part:
                        content = part['content']
                        for field, value in item_data.items():
                            content = content.replace(f"{{{field}}}", str(value))
                        part['content'] = content

                    new_item.append(part)

                new_items.append(new_item)

            result['docjll'][i]['items'] = new_items
            break

    return result


def convert_with_format(
    input_json_path: str,
    template_json_path: str,
    format_json_path: str
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
    with open(input_json_path, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    with open(template_json_path, 'r', encoding='utf-8') as f:
        template_data = json.load(f)

    with open(format_json_path, 'r', encoding='utf-8') as f:
        format_config = json.load(f)

    # Step 1: Substitute simple placeholders
    result = substitute_simple_placeholders(template_data, input_data, format_config)

    # Step 2: Expand repeatable tables
    result = expand_repeatable_tables(result, input_data, format_config)

    # Step 3: Expand repeatable lists
    result = expand_repeatable_lists(result, input_data, format_config)

    return result
