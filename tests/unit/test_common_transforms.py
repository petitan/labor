"""Unit tests for common transform functions."""

from labor.transforms.common_transforms import (
    capitalize,
    join_with_comma,
    join_with_newline,
    join_with_separator,
    lowercase,
    uppercase,
)


class TestCommonTransforms:
    """Test common transform functions."""

    def test_join_with_separator_default(self) -> None:
        """Test join_with_separator with default separator."""
        result = join_with_separator(["a", "b", "c"])
        assert result == "a, b, c"

    def test_join_with_separator_custom(self) -> None:
        """Test join_with_separator with custom separator."""
        result = join_with_separator(["apple", "banana", "cherry"], " + ")
        assert result == "apple + banana + cherry"

    def test_join_with_separator_single_item(self) -> None:
        """Test join_with_separator with single item."""
        result = join_with_separator(["alone"])
        assert result == "alone"

    def test_join_with_separator_empty_list(self) -> None:
        """Test join_with_separator with empty list."""
        result = join_with_separator([])
        assert result == ""

    def test_join_with_separator_numbers(self) -> None:
        """Test join_with_separator with numbers."""
        result = join_with_separator([1, 2, 3], " - ")
        assert result == "1 - 2 - 3"

    def test_join_with_comma(self) -> None:
        """Test join_with_comma."""
        result = join_with_comma(["red", "green", "blue"])
        assert result == "red, green, blue"

    def test_join_with_newline(self) -> None:
        """Test join_with_newline."""
        result = join_with_newline(["line1", "line2", "line3"])
        assert result == "line1\\nline2\\nline3"

    def test_uppercase(self) -> None:
        """Test uppercase transform."""
        assert uppercase("hello") == "HELLO"
        assert uppercase("Hello World") == "HELLO WORLD"
        assert uppercase("ALREADY") == "ALREADY"

    def test_uppercase_with_numbers(self) -> None:
        """Test uppercase with numbers."""
        assert uppercase("test123") == "TEST123"

    def test_lowercase(self) -> None:
        """Test lowercase transform."""
        assert lowercase("HELLO") == "hello"
        assert lowercase("Hello World") == "hello world"
        assert lowercase("already") == "already"

    def test_lowercase_with_numbers(self) -> None:
        """Test lowercase with numbers."""
        assert lowercase("TEST123") == "test123"

    def test_capitalize(self) -> None:
        """Test capitalize transform."""
        assert capitalize("hello world") == "Hello world"
        assert capitalize("HELLO WORLD") == "Hello world"
        assert capitalize("already capitalized") == "Already capitalized"

    def test_capitalize_empty_string(self) -> None:
        """Test capitalize with empty string."""
        assert capitalize("") == ""

    def test_uppercase_non_string(self) -> None:
        """Test uppercase converts non-string to string."""
        assert uppercase(123) == "123"  # type: ignore[arg-type]

    def test_lowercase_non_string(self) -> None:
        """Test lowercase converts non-string to string."""
        assert lowercase(123) == "123"  # type: ignore[arg-type]

    def test_capitalize_non_string(self) -> None:
        """Test capitalize converts non-string to string."""
        assert capitalize(123) == "123"  # type: ignore[arg-type]
