"""Unit tests for BaseConverter."""

import json
from pathlib import Path
from typing import Any

import pytest

from labor.converters.base_converter import BaseConverter


class TestBaseConverter:
    """Test BaseConverter functionality."""

    def test_load_json_valid_file(self, tmp_path: Path) -> None:
        """Test loading a valid JSON file."""
        test_data = {"key": "value", "number": 42}
        test_file = tmp_path / "test.json"
        test_file.write_text(json.dumps(test_data), encoding="utf-8")

        result = BaseConverter.load_json(test_file)
        assert result == test_data

    def test_load_json_nonexistent_file(self) -> None:
        """Test loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            BaseConverter.load_json("/nonexistent/path/file.json")

    def test_load_json_invalid_json(self, tmp_path: Path) -> None:
        """Test loading invalid JSON raises JSONDecodeError."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("{ invalid json }", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            BaseConverter.load_json(test_file)

    def test_save_json(self, tmp_path: Path) -> None:
        """Test saving JSON file."""
        test_data = {"key": "value", "nested": {"number": 42}}
        test_file = tmp_path / "output.json"

        BaseConverter.save_json(test_data, test_file)

        # Verify file exists and contains correct data
        assert test_file.exists()
        loaded = json.loads(test_file.read_text(encoding="utf-8"))
        assert loaded == test_data

    def test_save_json_unicode(self, tmp_path: Path) -> None:
        """Test saving JSON with unicode characters."""
        test_data = {"hungarian": "árvíztűrő tükörfúrógép"}
        test_file = tmp_path / "unicode.json"

        BaseConverter.save_json(test_data, test_file)

        loaded = json.loads(test_file.read_text(encoding="utf-8"))
        assert loaded == test_data

    def test_get_nested_value_simple(self) -> None:
        """Test getting nested value with simple path."""
        data = {"a": {"b": "value"}}
        result = BaseConverter.get_nested_value(data, "a.b")
        assert result == "value"

    def test_get_nested_value_deep(self) -> None:
        """Test getting deeply nested value."""
        data = {"level1": {"level2": {"level3": "deep"}}}
        result = BaseConverter.get_nested_value(data, "level1.level2.level3")
        assert result == "deep"

    def test_get_nested_value_array_index(self) -> None:
        """Test getting value with array indexing."""
        data = {"items": ["first", "second", "third"]}
        result = BaseConverter.get_nested_value(data, "items[1]")
        assert result == "second"

    def test_get_nested_value_nested_array(self) -> None:
        """Test getting value from nested array."""
        data = {"outer": {"inner": [10, 20, 30]}}
        result = BaseConverter.get_nested_value(data, "outer.inner[2]")
        assert result == 30

    def test_get_nested_value_not_found(self) -> None:
        """Test getting non-existent path returns default."""
        data = {"a": "value"}
        result = BaseConverter.get_nested_value(data, "b.c", default="default")
        assert result == "default"

    def test_get_nested_value_empty_path(self) -> None:
        """Test empty path returns default."""
        data = {"a": "value"}
        result = BaseConverter.get_nested_value(data, "", default="default")
        assert result == "default"

    def test_get_nested_value_array_out_of_bounds(self) -> None:
        """Test array index out of bounds returns default."""
        data = {"items": [1, 2]}
        result = BaseConverter.get_nested_value(data, "items[5]", default="default")
        assert result == "default"

    def test_get_nested_value_none_value(self) -> None:
        """Test None value returns default."""
        data = {"key": None}
        result = BaseConverter.get_nested_value(data, "key", default="default")
        assert result == "default"

    def test_set_nested_value_simple(self) -> None:
        """Test setting simple nested value."""
        data: dict = {}
        BaseConverter.set_nested_value(data, "a.b", "value")
        assert data == {"a": {"b": "value"}}

    def test_set_nested_value_deep(self) -> None:
        """Test setting deeply nested value."""
        data: dict = {}
        BaseConverter.set_nested_value(data, "level1.level2.level3", "deep")
        assert data == {"level1": {"level2": {"level3": "deep"}}}

    def test_set_nested_value_existing_path(self) -> None:
        """Test setting value in existing path."""
        data = {"a": {"b": "old"}}
        BaseConverter.set_nested_value(data, "a.b", "new")
        assert data == {"a": {"b": "new"}}

    def test_replace_in_structure_string(self) -> None:
        """Test replacing placeholder in string."""
        result = BaseConverter.replace_in_structure("Hello {{NAME}}", "{{NAME}}", "World")
        assert result == "Hello World"

    def test_replace_in_structure_dict(self) -> None:
        """Test replacing placeholder in dictionary."""
        obj = {"title": "{{TITLE}}", "content": "Text with {{TITLE}}"}
        result = BaseConverter.replace_in_structure(obj, "{{TITLE}}", "MyTitle")
        assert result == {"title": "MyTitle", "content": "Text with MyTitle"}

    def test_replace_in_structure_list(self) -> None:
        """Test replacing placeholder in list."""
        obj = ["{{NAME}}", "static", "{{NAME}} again"]
        result = BaseConverter.replace_in_structure(obj, "{{NAME}}", "Test")
        assert result == ["Test", "static", "Test again"]

    def test_replace_in_structure_nested(self) -> None:
        """Test replacing placeholder in nested structure."""
        obj = {"level1": {"level2": [{"text": "{{PLACEHOLDER}}"}]}}
        result = BaseConverter.replace_in_structure(obj, "{{PLACEHOLDER}}", "Value")
        assert result == {"level1": {"level2": [{"text": "Value"}]}}

    def test_replace_in_structure_primitives(self) -> None:
        """Test replacing placeholder preserves primitives."""
        assert BaseConverter.replace_in_structure(42, "{{X}}", "Y") == 42
        assert BaseConverter.replace_in_structure(True, "{{X}}", "Y") is True
        assert BaseConverter.replace_in_structure(None, "{{X}}", "Y") is None

    def test_merge_docjl_blocks_both_have_blocks(self) -> None:
        """Test merging two templates with blocks."""
        t1 = {"docjll": [{"type": "heading", "content": "Ch1"}]}
        t2 = {"docjll": [{"type": "heading", "content": "Ch2"}]}
        result = BaseConverter.merge_docjl_blocks(t1, t2)

        assert result == {
            "docjll": [
                {"type": "heading", "content": "Ch1"},
                {"type": "heading", "content": "Ch2"},
            ]
        }

    def test_merge_docjl_blocks_empty_first(self) -> None:
        """Test merging when first template is empty."""
        t1: dict[str, Any] = {"docjll": []}
        t2: dict[str, Any] = {"docjll": [{"type": "heading", "content": "Ch2"}]}
        result = BaseConverter.merge_docjl_blocks(t1, t2)

        assert result == {"docjll": [{"type": "heading", "content": "Ch2"}]}

    def test_merge_docjl_blocks_empty_second(self) -> None:
        """Test merging when second template is empty."""
        t1: dict[str, Any] = {"docjll": [{"type": "heading", "content": "Ch1"}]}
        t2: dict[str, Any] = {"docjll": []}
        result = BaseConverter.merge_docjl_blocks(t1, t2)

        assert result == {"docjll": [{"type": "heading", "content": "Ch1"}]}

    def test_merge_docjl_blocks_missing_docjll_key(self) -> None:
        """Test merging when docjll key is missing."""
        t1: dict[str, Any] = {}
        t2: dict[str, Any] = {"docjll": [{"type": "heading", "content": "Ch2"}]}
        result = BaseConverter.merge_docjl_blocks(t1, t2)

        assert result == {"docjll": [{"type": "heading", "content": "Ch2"}]}

    def test_convert_not_implemented(self) -> None:
        """Test that convert() raises NotImplementedError."""
        converter = BaseConverter()
        with pytest.raises(NotImplementedError, match="Subclasses must implement convert"):
            converter.convert("input.json", "template.json", "format.json")

    def test_substitute_placeholders_not_implemented(self) -> None:
        """Test that substitute_placeholders() raises NotImplementedError."""
        converter = BaseConverter()
        with pytest.raises(
            NotImplementedError, match="Subclasses should implement substitute_placeholders"
        ):
            converter.substitute_placeholders({}, {}, {})
