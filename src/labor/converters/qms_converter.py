"""QMS Converter - ISO 17025 Quality Management System document converter."""

import copy
from typing import Any

from labor.transforms import TransformRegistry

from .base_converter import BaseConverter


class QMSConverter(BaseConverter):
    """
    Converter for ISO 17025 QMS documents.

    Supports:
    - Simple mappings: "{{PLACEHOLDER}}": "json.path"
    - Transform pipelines: "{{PLACEHOLDER}}": {"source": "...", "pipeline": [...]}
    - Transform chains: Multiple transforms applied sequentially
    - Global + chapter merge: Automatic handling of modular data

    Example:
        >>> converter = QMSConverter()
        >>> docjl = converter.convert(
        ...     'qms/build/QMS_full_input.json',
        ...     'qms/build/QMS_full_template.json',
        ...     'qms/build/QMS_full_format.json'
        ... )
    """

    def __init__(self) -> None:
        """Initialize QMS converter."""
        super().__init__()

    def replace_list_placeholder(self, obj: Any, placeholder: str, value: list | dict) -> Any:
        """
        Replace placeholder with list/dict value in data structure.

        This handles special cases where a placeholder represents an entire list
        (e.g., items field in list_unordered block) or a dict (e.g., table structure).

        Special handling for table blocks:
        If a parent dict has 'type': 'table' and 'content' is a dict (table structure),
        the content dict's fields are merged into the parent dict.

        Args:
            obj: Object to search
            placeholder: Placeholder string
            value: List or dict value to replace with

        Returns:
            Object with placeholder replaced by list/dict

        Example:
            >>> block = {"type": "list_unordered", "items": "{{STANDARDS}}"}
            >>> replace_list_placeholder(block, "{{STANDARDS}}", ["item1", "item2"])
            {'type': 'list_unordered', 'items': ['item1', 'item2']}

            >>> block = {"type": "table", "content": "{{TABLE}}"}
            >>> replace_list_placeholder(block, "{{TABLE}}", {"headers": [...], "rows": [...]})
            {'type': 'table', 'headers': [...], 'rows': [...]}
        """
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if v == placeholder:
                    # Special case: table block with dict content
                    if k == "content" and isinstance(value, dict) and obj.get("type") == "table":
                        # Merge dict fields into parent (skip 'content' key)
                        for key, val in value.items():
                            if key != "type":  # Don't override parent's type
                                result[key] = val
                    else:
                        result[k] = value
                else:
                    result[k] = self.replace_list_placeholder(v, placeholder, value)

            # If we skipped 'content' due to merge, don't include it
            if "content" not in result and "content" in obj:
                # Content was merged, that's OK
                pass

            return result
        elif isinstance(obj, list):
            return [self.replace_list_placeholder(item, placeholder, value) for item in obj]
        elif isinstance(obj, str) and obj == placeholder:
            # Exact match: replace with list/dict
            return value
        elif isinstance(obj, str) and placeholder in obj:
            # Partial match: can't replace (would break structure)
            print(f"⚠️  Warning: Placeholder {placeholder} in string context: {obj[:50]}")
            return obj
        else:
            return obj

    def apply_transform_pipeline(self, value: Any, pipeline: list[dict]) -> Any:
        """
        Apply a chain of transforms to a value.

        Each transform in the pipeline is applied sequentially,
        with the output of one becoming the input to the next.

        Args:
            value: Initial value
            pipeline: List of transform steps, each with:
                     {"transform": "name", "params": {...}}

        Returns:
            Final transformed value

        Example:
            >>> pipeline = [
            ...     {"transform": "format_standard_list"},
            ...     {"transform": "join_with_newline"}
            ... ]
            >>> value = [{"code": "ISO 17025", "title_hun": "Requirements"}]
            >>> result = apply_transform_pipeline(value, pipeline)
            >>> # Result: "**ISO 17025** -- Requirements*"
        """
        current_value = value

        for step in pipeline:
            transform_name = step.get("transform")
            params = step.get("params", {})

            if not transform_name:
                continue

            try:
                current_value = TransformRegistry.apply(
                    transform_name, current_value, params if params else None
                )
            except ValueError as e:
                print(f"⚠️  Transform error in pipeline '{transform_name}': {e}")
                print(f"   Skipping transform, keeping value: {current_value}")
                continue

        return current_value

    def substitute_placeholders(
        self, template_data: dict, input_data: dict, format_config: dict
    ) -> dict:
        """
        Substitute QMS placeholders using mappings configuration.

        Supports two mapping types:

        1. Simple mapping:
           "{{PLACEHOLDER}}": "json.path"

        2. Transform pipeline:
           "{{PLACEHOLDER}}": {
               "source": "json.path",
               "pipeline": [
                   {"transform": "transform1", "params": {...}},
                   {"transform": "transform2"}
               ]
           }

        Args:
            template_data: Template with placeholders
            input_data: QMS input data (merged global + chapters)
            format_config: Format configuration with "mappings" key

        Returns:
            Template with all placeholders replaced

        Example format config:
            {
              "mappings": {
                "{{COMPANY}}": "global.company.name",
                "{{STANDARDS}}": {
                  "source": "global.documents.standards",
                  "pipeline": [
                    {"transform": "format_standard_list"},
                    {"transform": "join_with_newline"}
                  ]
                }
              }
            }
        """
        result = copy.deepcopy(template_data)
        mappings = format_config.get("mappings", {})

        for placeholder, config in mappings.items():
            # Case 1: Simple string mapping
            if isinstance(config, str):
                json_path = config
                value = self.get_nested_value(input_data, json_path, "")
                result = self.replace_in_structure(result, placeholder, str(value))

            # Case 2: Complex mapping with transforms
            elif isinstance(config, dict):
                source_path = config.get("source", "")
                value = self.get_nested_value(input_data, source_path, "")

                # Apply single transform (legacy support)
                if "transform" in config:
                    transform_name = config["transform"]
                    params = {}

                    # Extract common transform parameters
                    for param_key in ["separator", "prefix", "suffix"]:
                        if param_key in config:
                            params[param_key] = config[param_key]

                    try:
                        value = TransformRegistry.apply(
                            transform_name, value, params if params else None
                        )
                    except ValueError as e:
                        print(f"⚠️  Transform error for {placeholder}: {e}")

                # Apply transform pipeline (new style)
                elif "pipeline" in config:
                    pipeline = config["pipeline"]
                    value = self.apply_transform_pipeline(value, pipeline)

                # Special handling for list and dict values
                # If value is a list and placeholder is in an "items" field, replace with the list directly
                if isinstance(value, list):
                    result = self.replace_list_placeholder(result, placeholder, value)
                elif isinstance(value, dict):
                    # If value is a dict (e.g., table structure), replace with the dict directly
                    result = self.replace_list_placeholder(result, placeholder, value)
                else:
                    result = self.replace_in_structure(result, placeholder, str(value))

        return result

    def convert(self, input_json_path: str, template_json_path: str, format_json_path: str) -> dict:
        """
        Convert QMS input to docjl format.

        This is the main entry point for QMS conversion.

        Steps:
        1. Load input data (merged global + chapters)
        2. Load template (merged chapter templates)
        3. Load format config (merged chapter formats)
        4. Substitute all placeholders using Transform Registry
        5. Return final docjl

        Args:
            input_json_path: Path to QMS input data (e.g., qms/build/QMS_full_input.json)
            template_json_path: Path to template (e.g., qms/build/QMS_full_template.json)
            format_json_path: Path to format config (e.g., qms/build/QMS_full_format.json)

        Returns:
            docjl format dictionary ready for LaTeX conversion

        Example:
            >>> from converters import QMSConverter
            >>> converter = QMSConverter()
            >>> docjl = converter.convert(
            ...     'qms/build/QMS_full_input.json',
            ...     'qms/build/QMS_full_template.json',
            ...     'qms/build/QMS_full_format.json'
            ... )
            >>> # Convert to LaTeX:
            >>> from docjl import MarkdownJsonToDocjl
            >>> latex_converter = MarkdownJsonToDocjl()
            >>> latex = latex_converter.convert(json.dumps(docjl))
        """
        # Load files
        print(f"📖 Loading QMS input data from {input_json_path}")
        input_data = self.load_json(input_json_path)

        print(f"📖 Loading QMS template from {template_json_path}")
        template_data = self.load_json(template_json_path)

        print(f"📖 Loading QMS format config from {format_json_path}")
        format_config = self.load_json(format_json_path)

        # Substitute placeholders
        print("🔄 Substituting placeholders with Transform Registry...")
        result = self.substitute_placeholders(template_data, input_data, format_config)

        # Note: QMS doesn't use repeatable blocks yet (unlike calibration)
        # If needed in the future, we can add expand_repeatable_tables/lists here

        print("✅ QMS conversion complete!")
        return result
