"""Common transform functions - universal utilities."""

from .registry import TransformRegistry


def join_with_separator(items: list, separator: str = ", ") -> str:
    """
    Join list items with custom separator.

    Args:
        items: List of items to join
        separator: Separator string (default: ", ")

    Returns:
        Joined string

    Example:
        >>> join_with_separator(["a", "b", "c"], " + ")
        'a + b + c'
    """
    return separator.join(str(item) for item in items)


def uppercase(value: str) -> str:
    """Convert string to uppercase."""
    return str(value).upper()


def lowercase(value: str) -> str:
    """Convert string to lowercase."""
    return str(value).lower()


def capitalize(value: str) -> str:
    """Capitalize first letter."""
    return str(value).capitalize()


def join_with_comma(items: list) -> str:
    """Join list items with comma (legacy compatibility)."""
    return join_with_separator(items, ", ")


def join_with_newline(items: list) -> str:
    """Join list items with newlines."""
    return join_with_separator(items, "\\n")


# Auto-register all transforms
TransformRegistry.register("join_with_separator", join_with_separator)
TransformRegistry.register("join_with_comma", join_with_comma)
TransformRegistry.register("join_with_newline", join_with_newline)
TransformRegistry.register("uppercase", uppercase)
TransformRegistry.register("lowercase", lowercase)
TransformRegistry.register("capitalize", capitalize)
