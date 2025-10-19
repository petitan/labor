"""Base Converter - Common functionality for all document converters."""

import json
from pathlib import Path
from typing import Any


class BaseConverter:
    """
    Base class for document converters.

    Provides common functionality:
    - Loading/saving JSON files
    - Nested value getter/setter
    - Recursive placeholder replacement
    - Template structure manipulation

    Subclasses should implement:
    - convert(): Main conversion logic
    - substitute_placeholders(): Placeholder replacement strategy
    """

    def __init__(self) -> None:
        """Initialize base converter."""
        pass

    # ==================== File I/O ====================

    @staticmethod
    def load_json(filepath: str | Path) -> dict[Any, Any]:
        """
        Load JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Loaded JSON data as dict

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        filepath = Path(filepath)
        with filepath.open(encoding="utf-8") as f:
            data: dict[Any, Any] = json.load(f)
            return data

    @staticmethod
    def save_json(data: dict, filepath: str | Path) -> None:
        """
        Save JSON file with pretty formatting.

        Args:
            data: Data to save
            filepath: Output path
        """
        filepath = Path(filepath)
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ==================== Nested Access ====================

    @staticmethod
    def get_nested_value(data: dict, json_path: str, default: Any = "") -> Any:
        """
        Get value from nested dictionary using dot notation.

        Supports array indexing: "items[0]", "chapters.ch01.data"

        Args:
            data: Input dictionary
            json_path: Path like "scope.equipment_description" or "items[0]"
            default: Default value if path not found

        Returns:
            Value at the path, or default if not found

        Examples:
            >>> get_nested_value({"a": {"b": "value"}}, "a.b")
            'value'
            >>> get_nested_value({"a": [1, 2, 3]}, "a[1]")
            2
            >>> get_nested_value({"x": 1}, "y.z", "default")
            'default'
        """
        if not json_path:
            return default

        # Handle array indexing: "items[0]" → ["items", 0]
        import re

        keys = []
        for part in json_path.split("."):
            match = re.match(r"(\w+)\[(\d+)\]", part)
            if match:
                keys.append(match.group(1))  # array name
                keys.append(int(match.group(2)))  # index
            else:
                keys.append(part)

        current = data
        for key in keys:
            if (
                isinstance(current, dict)
                and key in current
                or isinstance(current, list)
                and isinstance(key, int)
                and 0 <= key < len(current)
            ):
                current = current[key]
            else:
                return default

        return current if current is not None else default

    @staticmethod
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

    # ==================== Placeholder Replacement ====================

    @staticmethod
    def replace_in_structure(obj: Any, placeholder: str, value: str) -> Any:
        """
        Recursively replace placeholder in any data structure.

        Handles:
        - Dictionaries (recursively)
        - Lists (recursively)
        - Strings (direct replacement)
        - Primitives (unchanged)

        Args:
            obj: Object to search (dict, list, str, or primitive)
            placeholder: Placeholder to find (e.g., "{{COMPANY_NAME}}")
            value: Value to replace with

        Returns:
            Object with replacements made

        Example:
            >>> replace_in_structure({"title": "{{NAME}}"}, "{{NAME}}", "Foo")
            {'title': 'Foo'}
        """
        if isinstance(obj, dict):
            return {
                k: BaseConverter.replace_in_structure(v, placeholder, value) for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [BaseConverter.replace_in_structure(item, placeholder, value) for item in obj]
        elif isinstance(obj, str):
            return obj.replace(placeholder, str(value))
        else:
            return obj

    # ==================== Template Manipulation ====================

    @staticmethod
    def merge_docjl_blocks(template1: dict, template2: dict) -> dict:
        """
        Merge two docjl templates by concatenating their blocks.

        Args:
            template1: First template {"docjll": [...]}
            template2: Second template {"docjll": [...]}

        Returns:
            Merged template with combined blocks

        Example:
            >>> t1 = {"docjll": [{"type": "heading", "content": "Ch1"}]}
            >>> t2 = {"docjll": [{"type": "heading", "content": "Ch2"}]}
            >>> merge_docjl_blocks(t1, t2)
            {'docjll': [{'type': 'heading', 'content': 'Ch1'},
                        {'type': 'heading', 'content': 'Ch2'}]}
        """
        blocks1 = template1.get("docjll", [])
        blocks2 = template2.get("docjll", [])
        return {"docjll": blocks1 + blocks2}

    # ==================== Conversion Interface ====================

    def convert(self, input_json_path: str, template_json_path: str, format_json_path: str) -> dict:
        """
        Convert input data to docjl format.

        This is the main entry point. Subclasses MUST implement this method.

        Args:
            input_json_path: Path to input data
            template_json_path: Path to template
            format_json_path: Path to format configuration

        Returns:
            docjl format dictionary

        Raises:
            NotImplementedError: If subclass doesn't implement this
        """
        raise NotImplementedError("Subclasses must implement convert()")

    def substitute_placeholders(
        self, template_data: dict, input_data: dict, format_config: dict
    ) -> dict:
        """
        Substitute placeholders in template with input data.

        This is converter-specific logic. Subclasses SHOULD implement this.

        Args:
            template_data: Template with placeholders
            input_data: Input data
            format_config: Format configuration

        Returns:
            Template with placeholders replaced

        Raises:
            NotImplementedError: If subclass doesn't implement this
        """
        raise NotImplementedError("Subclasses should implement substitute_placeholders()")
