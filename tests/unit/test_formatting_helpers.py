"""Unit tests for formatting helper functions."""

from labor.transforms.formatting_helpers import (
    combine_inline_arrays,
    make_bold_label_value,
    make_bold_prefix,
    make_bold_text,
    make_info_box_content,
    make_italic_text,
    make_plain_text,
)


class TestFormattingHelpers:
    """Test formatting helper functions."""

    def test_make_bold_label_value_default_separator(self) -> None:
        """Test make_bold_label_value with default separator."""
        result = make_bold_label_value("Label", "Value")
        expected = [
            {"type": "bold", "content": "Label:"},
            {"type": "text", "content": " Value"},
        ]
        assert result == expected

    def test_make_bold_label_value_custom_separator(self) -> None:
        """Test make_bold_label_value with custom separator."""
        result = make_bold_label_value("Count", "42", separator=" =")
        expected = [
            {"type": "bold", "content": "Count ="},
            {"type": "text", "content": " 42"},
        ]
        assert result == expected

    def test_make_bold_prefix_default_separator(self) -> None:
        """Test make_bold_prefix with default separator."""
        result = make_bold_prefix("NAR-87", "Document title")
        expected = [
            {"type": "bold", "content": "NAR-87"},
            {"type": "text", "content": " -- Document title"},
        ]
        assert result == expected

    def test_make_bold_prefix_custom_separator(self) -> None:
        """Test make_bold_prefix with custom separator."""
        result = make_bold_prefix("ISO 17025", "Requirements", " - ")
        expected = [
            {"type": "bold", "content": "ISO 17025"},
            {"type": "text", "content": " - Requirements"},
        ]
        assert result == expected

    def test_make_info_box_content_single_field(self) -> None:
        """Test make_info_box_content with single field."""
        fields = {"Label": "Value"}
        result = make_info_box_content(fields)
        expected = [
            {"type": "bold", "content": "Label:"},
            {"type": "text", "content": " Value"},
        ]
        assert result == expected

    def test_make_info_box_content_multiple_fields(self) -> None:
        """Test make_info_box_content with multiple fields."""
        fields = {"Label1": "Value1", "Label2": "Value2", "Label3": "Value3"}
        result = make_info_box_content(fields)
        expected = [
            {"type": "bold", "content": "Label1:"},
            {"type": "text", "content": " Value1\n\n"},
            {"type": "bold", "content": "Label2:"},
            {"type": "text", "content": " Value2\n\n"},
            {"type": "bold", "content": "Label3:"},
            {"type": "text", "content": " Value3"},  # No trailing newline
        ]
        assert result == expected

    def test_make_info_box_content_empty_dict(self) -> None:
        """Test make_info_box_content with empty dict."""
        result = make_info_box_content({})
        assert result == []

    def test_make_bold_text(self) -> None:
        """Test make_bold_text."""
        result = make_bold_text("Important")
        expected = [{"type": "bold", "content": "Important"}]
        assert result == expected

    def test_make_italic_text(self) -> None:
        """Test make_italic_text."""
        result = make_italic_text("Note")
        expected = [{"type": "italic", "content": "Note"}]
        assert result == expected

    def test_make_plain_text(self) -> None:
        """Test make_plain_text."""
        result = make_plain_text("Regular text")
        expected = [{"type": "text", "content": "Regular text"}]
        assert result == expected

    def test_combine_inline_arrays_two_arrays(self) -> None:
        """Test combine_inline_arrays with two arrays."""
        array1 = [{"type": "bold", "content": "Bold"}]
        array2 = [{"type": "text", "content": " text"}]
        result = combine_inline_arrays(array1, array2)
        expected = [
            {"type": "bold", "content": "Bold"},
            {"type": "text", "content": " text"},
        ]
        assert result == expected

    def test_combine_inline_arrays_multiple_arrays(self) -> None:
        """Test combine_inline_arrays with multiple arrays."""
        bold_part = make_bold_text("Bold")
        italic_part = make_italic_text("Italic")
        separator = [{"type": "text", "content": " and "}]

        result = combine_inline_arrays(bold_part, separator, italic_part)
        expected = [
            {"type": "bold", "content": "Bold"},
            {"type": "text", "content": " and "},
            {"type": "italic", "content": "Italic"},
        ]
        assert result == expected

    def test_combine_inline_arrays_empty_arrays(self) -> None:
        """Test combine_inline_arrays with empty arrays."""
        result = combine_inline_arrays([], [], [])
        assert result == []

    def test_combine_inline_arrays_single_array(self) -> None:
        """Test combine_inline_arrays with single array."""
        array = [{"type": "bold", "content": "Test"}]
        result = combine_inline_arrays(array)
        assert result == array
