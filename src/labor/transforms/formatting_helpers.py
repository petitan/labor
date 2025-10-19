"""
Formatting helpers for docjl inline arrays.

This module provides reusable helper functions for creating inline array
structures with bold, italic, and other formatting. These helpers are used
by transform functions to generate consistent docjl-compatible formatting.

The helpers generate inline arrays in docjl format:
    [{"type": "bold", "content": "..."}, {"type": "text", "content": "..."}]

These inline arrays are then processed by docjl's InlineFormatter to generate
LaTeX commands like \\textbf{}, \\textit{}, etc.

Example:
    >>> from transforms.formatting_helpers import make_bold_label_value
    >>> make_bold_label_value("Alapszabvány", "ISO 17025:2018")
    [{'type': 'bold', 'content': 'Alapszabvány:'},
     {'type': 'text', 'content': ' ISO 17025:2018'}]
"""


def make_bold_label_value(label: str, value: str, separator: str = ":") -> list[dict]:
    """
    Create inline array with bold label and plain value.

    This is commonly used for key-value pairs in info boxes where
    the label should be bold and the value plain text.

    Args:
        label: The label text (will be bold)
        value: The value text (will be plain)
        separator: Separator between label and value (default: ":")

    Returns:
        List of inline array elements

    Example:
        >>> make_bold_label_value("Alapszabvány", "ISO 17025:2018")
        [{'type': 'bold', 'content': 'Alapszabvány:'},
         {'type': 'text', 'content': ' ISO 17025:2018'}]

        >>> make_bold_label_value("Count", "42", separator=" =")
        [{'type': 'bold', 'content': 'Count ='},
         {'type': 'text', 'content': ' 42'}]
    """
    return [
        {"type": "bold", "content": f"{label}{separator}"},
        {"type": "text", "content": f" {value}"},
    ]


def make_bold_prefix(prefix: str, text: str, separator: str = " -- ") -> list[dict]:
    """
    Create inline array with bold prefix and plain text.

    This is commonly used for document codes, standards, and regulations
    where the code/identifier should be bold followed by the description.

    Args:
        prefix: The prefix text (will be bold)
        text: The main text (will be plain)
        separator: Separator between prefix and text (default: " -- ")

    Returns:
        List of inline array elements

    Example:
        >>> make_bold_prefix("NAR-87", "Pártatlansági Tanácsadó Testület ügyrendje*")
        [{'type': 'bold', 'content': 'NAR-87'},
         {'type': 'text', 'content': ' -- Pártatlansági Tanácsadó Testület ügyrendje*'}]

        >>> make_bold_prefix("ISO 17025:2018", "Requirements*", " - ")
        [{'type': 'bold', 'content': 'ISO 17025:2018'},
         {'type': 'text', 'content': ' - Requirements*'}]
    """
    return [
        {"type": "bold", "content": prefix},
        {"type": "text", "content": f"{separator}{text}"},
    ]


def make_info_box_content(fields: dict[str, str]) -> list[dict]:
    """
    Create inline array content for info boxes from label-value pairs.

    Generates a structured list of bold labels followed by plain values,
    with double newlines between pairs (except after the last one).

    Args:
        fields: Dictionary of label-value pairs (ordered dict recommended)

    Returns:
        List of inline array elements suitable for info box content

    Example:
        >>> fields = {"Alapszabvány": "ISO 17025", "Cél": "Akkreditáció"}
        >>> make_info_box_content(fields)
        [{'type': 'bold', 'content': 'Alapszabvány:'},
         {'type': 'text', 'content': ' ISO 17025\\n\\n'},
         {'type': 'bold', 'content': 'Cél:'},
         {'type': 'text', 'content': ' Akkreditáció'}]

    Note:
        The last value does NOT have trailing \\n\\n to avoid extra spacing
        at the end of the info box.
    """
    result = []
    items = list(fields.items())

    for i, (label, value) in enumerate(items):
        # Bold label with colon
        result.append({"type": "bold", "content": f"{label}:"})

        # Plain value with double newline (except last item)
        suffix = "\n\n" if i < len(items) - 1 else ""
        result.append({"type": "text", "content": f" {value}{suffix}"})

    return result


def make_bold_text(text: str) -> list[dict]:
    """
    Create inline array with single bold text element.

    Simple helper for wrapping text in bold formatting.

    Args:
        text: Text to make bold

    Returns:
        List with single bold inline element

    Example:
        >>> make_bold_text("Important")
        [{'type': 'bold', 'content': 'Important'}]
    """
    return [{"type": "bold", "content": text}]


def make_italic_text(text: str) -> list[dict]:
    """
    Create inline array with single italic text element.

    Simple helper for wrapping text in italic formatting.

    Args:
        text: Text to make italic

    Returns:
        List with single italic inline element

    Example:
        >>> make_italic_text("Note")
        [{'type': 'italic', 'content': 'Note'}]
    """
    return [{"type": "italic", "content": text}]


def make_plain_text(text: str) -> list[dict]:
    """
    Create inline array with single plain text element.

    Helper for consistency when mixing formatted and plain text.

    Args:
        text: Plain text

    Returns:
        List with single text inline element

    Example:
        >>> make_plain_text("Regular text")
        [{'type': 'text', 'content': 'Regular text'}]
    """
    return [{"type": "text", "content": text}]


def combine_inline_arrays(*arrays: list[dict]) -> list[dict]:
    """
    Combine multiple inline arrays into a single array.

    Useful for building complex inline formatting by combining
    multiple helper function results.

    Args:
        *arrays: Variable number of inline arrays to combine

    Returns:
        Combined inline array

    Example:
        >>> bold_part = make_bold_text("Bold")
        >>> italic_part = make_italic_text("Italic")
        >>> combine_inline_arrays(bold_part, [{"type": "text", "content": " and "}], italic_part)
        [{'type': 'bold', 'content': 'Bold'},
         {'type': 'text', 'content': ' and '},
         {'type': 'italic', 'content': 'Italic'}]
    """
    result = []
    for array in arrays:
        result.extend(array)
    return result
