"""Calibration Converter - Universal calibration procedure document converter."""

import copy
import json
from typing import Any

from labor.transforms import TransformRegistry

from .base_converter import BaseConverter


class CalibrationConverter(BaseConverter):
    """
    Converter for calibration procedure documents.

    Supports:
    - Simple mappings: placeholder → json path
    - Array mappings: fixed-size arrays
    - Custom mappings: with transforms
    - Repeatable blocks: dynamic tables and lists
    - Inline array substitution: for complex formatting

    Compatible with both legacy format (simple_mappings, custom_mappings)
    and modern format (mappings with pipelines).

    Example:
        >>> converter = CalibrationConverter()
        >>> docjl = converter.convert(
        ...     'examples/pressure_gauge_calibration_input.json',
        ...     'src/labor/calibration_template.json',
        ...     'src/labor/calibration_format.json'
        ... )
    """

    def __init__(self) -> None:
        """Initialize Calibration converter."""
        super().__init__()

    # ==================== Inline Array Support ====================

    @staticmethod
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

    @staticmethod
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

    # ==================== Placeholder Substitution ====================

    def substitute_simple_placeholders(
        self, template_data: dict, input_data: dict, format_config: dict
    ) -> dict:
        """
        Substitute simple 1:1 placeholder mappings.

        Supports legacy format configuration:
        - simple_mappings: {"{{PLACEHOLDER}}": "json.path"}
        - array_mappings: {"json.path": {"placeholders": ["{{P1}}", "{{P2}}"]}}
        - custom_mappings: {"{{PLACEHOLDER}}": {"source": "path", "transform": "name"}}

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
            value = self.get_nested_value(input_data, json_path, "")
            result = self.replace_in_structure(result, placeholder, value)

        # Array mappings (fixed-size arrays)
        for json_path, config in format_config.get("array_mappings", {}).items():
            array_data = self.get_nested_value(input_data, json_path, [])
            placeholders = config.get("placeholders", [])

            for i, placeholder in enumerate(placeholders):
                value = array_data[i] if i < len(array_data) else ""
                result = self.replace_in_structure(result, placeholder, value)

        # Custom mappings (with transforms)
        for placeholder, config in format_config.get("custom_mappings", {}).items():
            source_type = config.get("source", "")

            if source_type == "static":
                value = config.get("value", "")
            else:
                value = self.get_nested_value(input_data, config.get("source", ""), "")

            transform = config.get("transform")
            if transform:
                try:
                    value = TransformRegistry.apply(transform, value, None)
                except ValueError as e:
                    print(f"⚠️  Transform error for {placeholder}: {e}")

            result = self.replace_in_structure(result, placeholder, str(value))

        return result

    # ==================== Repeatable Tables ====================

    @staticmethod
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
            "has_note_containing" not in identification
            or identification["has_note_containing"] in note
        )
        caption_match = (
            "has_caption_containing" not in identification
            or identification["has_caption_containing"] in caption
        )

        return note_match and caption_match

    def _find_table_block(self, docjll_blocks: list[dict], identification: dict) -> int | None:
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

            if self._matches_table_identification(block, identification):
                return i

        return None

    def _build_table_rows(self, source_data: list[dict], row_fields: list[str]) -> list[list[Any]]:
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
                row.append(self.convert_table_cell_value(value))
            new_rows.append(row)

        return new_rows

    def expand_repeatable_tables(
        self, template_data: dict, input_data: dict, format_config: dict
    ) -> dict:
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
            source_data = self.get_nested_value(input_data, source_path, [])
            if not source_data:
                continue

            # Find matching table block in template
            identification = block_config.get("identification", {})
            row_fields = block_config.get("row_fields", [])

            block_index = self._find_table_block(result.get("docjll", []), identification)
            if block_index is None:
                continue

            # Build and replace rows
            new_rows = self._build_table_rows(source_data, row_fields)
            result["docjll"][block_index]["rows"] = new_rows

        return result

    # ==================== Repeatable Lists ====================

    @staticmethod
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
        self, template_part: dict, item_data: dict
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

            if self.is_inline_array_substitution(content, placeholder, value):
                # Return inline array elements (list of dicts)
                return (value, None)

        # Normal placeholder replacement
        for field, value in item_data.items():
            placeholder = f"{{{field}}}"
            value_str = str(value) if not isinstance(value, list) else json.dumps(value)
            content = content.replace(placeholder, value_str)

        part["content"] = content
        return (None, part)

    def _build_list_item(self, item_template: list[dict], item_data: dict) -> list[dict]:
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
            inline_array, processed_part = self._process_template_part(template_part, item_data)

            if inline_array is not None:
                # Inline array substitution: extend with array elements
                new_item.extend(inline_array)
            elif processed_part is not None:
                # Normal part: append
                new_item.append(processed_part)

        return new_item

    def expand_repeatable_lists(
        self, template_data: dict, input_data: dict, format_config: dict
    ) -> dict:
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
            source_data = self.get_nested_value(input_data, source_path, [])
            if not source_data:
                continue

            # Find matching list block in template
            identification = block_config.get("identification", {})
            item_template = block_config.get("item_template", [])

            block_index = self._find_list_block(result.get("docjll", []), identification)
            if block_index is None:
                continue

            # Build new items from source data
            new_items = [
                self._build_list_item(item_template, item_data) for item_data in source_data
            ]

            # Replace items in result
            result["docjll"][block_index]["items"] = new_items

        return result

    # ==================== Main Conversion ====================

    def convert(self, input_json_path: str, template_json_path: str, format_json_path: str) -> dict:
        """
        Convert calibration input to docjl format.

        This is the main entry point for calibration conversion.

        Steps:
        1. Load input data, template, and format config
        2. Substitute simple placeholders
        3. Expand repeatable tables (dynamic row count)
        4. Expand repeatable lists (dynamic item count)
        5. Return final docjl

        Args:
            input_json_path: Path to calibration input (e.g., emission_calibration_input.json)
            template_json_path: Path to template (calibration_template.json)
            format_json_path: Path to format config (calibration_format.json)

        Returns:
            docjl format dictionary ready for LaTeX conversion

        Example:
            >>> from labor.converters import CalibrationConverter
            >>> converter = CalibrationConverter()
            >>> docjl = converter.convert(
            ...     'examples/pressure_gauge_calibration_input.json',
            ...     'src/labor/calibration_template.json',
            ...     'src/labor/calibration_format.json'
            ... )
            >>> # Convert to LaTeX:
            >>> from docjl import MarkdownJsonToDocjl
            >>> latex_converter = MarkdownJsonToDocjl()
            >>> latex = latex_converter.convert(json.dumps(docjl))
        """
        # Load files
        print(f"📖 Loading calibration input from {input_json_path}")
        input_data = self.load_json(input_json_path)

        print(f"📖 Loading calibration template from {template_json_path}")
        template_data = self.load_json(template_json_path)

        print(f"📖 Loading calibration format config from {format_json_path}")
        format_config = self.load_json(format_json_path)

        # Step 1: Substitute simple placeholders
        print("🔄 Substituting placeholders...")
        result = self.substitute_simple_placeholders(template_data, input_data, format_config)

        # Step 2: Expand repeatable tables
        print("🔄 Expanding repeatable tables...")
        result = self.expand_repeatable_tables(result, input_data, format_config)

        # Step 3: Expand repeatable lists
        print("🔄 Expanding repeatable lists...")
        result = self.expand_repeatable_lists(result, input_data, format_config)

        print("✅ Calibration conversion complete!")
        return result
