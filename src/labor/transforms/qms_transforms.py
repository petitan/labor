"""QMS-specific transform functions."""

from .formatting_helpers import make_bold_prefix
from .registry import TransformRegistry


def format_standard_list(items: list[dict]) -> list[list[dict]]:
    """
    Format ISO standards list for display using docjl inline arrays.

    Uses the make_bold_prefix helper for consistent formatting.
    Uses unified keys: 'id' and 'name_hu'.

    Args:
        items: List of standard dicts with 'id' and 'name_hu' keys

    Returns:
        List of inline arrays with bold formatting for IDs

    Example:
        >>> items = [{"id": "ISO 17025:2018", "name_hu": "Requirements"}]
        >>> format_standard_list(items)
        [[{'type': 'bold', 'content': 'ISO 17025:2018'},
          {'type': 'text', 'content': ' -- Requirements*'}]]
    """
    return [make_bold_prefix(item["id"], f"{item['name_hu']}*", " -- ") for item in items]


def format_document_list(items: list[dict]) -> list[list[dict]]:
    """
    Format ILAC/EA/NAR documents list for display using docjl inline arrays.

    Uses the make_bold_prefix helper for consistent formatting.
    Uses unified keys: 'id' and 'name_hu'.

    Args:
        items: List of document dicts with 'id' and 'name_hu' keys

    Returns:
        List of inline arrays with bold formatting for IDs

    Example:
        >>> items = [{"id": "ILAC-P8:11/2023", "name_hu": "MRA Requirements"}]
        >>> format_document_list(items)
        [[{'type': 'bold', 'content': 'ILAC-P8:11/2023'},
          {'type': 'text', 'content': ' -- MRA Requirements*'}]]
    """
    return [make_bold_prefix(item["id"], f"{item['name_hu']}*", " -- ") for item in items]


def format_regulation_list(items: list[dict]) -> list[list[dict]]:
    """
    Format Hungarian regulations list for display using docjl inline arrays.

    Uses the make_bold_prefix helper for consistent formatting.
    Uses unified keys: 'id' and 'name_hu'.

    Args:
        items: List of regulation dicts with 'id' and 'name_hu' keys

    Returns:
        List of inline arrays with bold formatting for IDs

    Example:
        >>> items = [{"id": "1/1990 (IX.29) KHVM", "name_hu": "requirements"}]
        >>> format_regulation_list(items)
        [[{'type': 'bold', 'content': '1/1990 (IX.29) KHVM'},
          {'type': 'text', 'content': ' rendelet requirements*'}]]
    """
    return [make_bold_prefix(item["id"], f"rendelet {item['name_hu']}*", " ") for item in items]


def format_longtable(table_def: dict) -> dict:
    """
    Format table definition to docjl table structure.

    Takes a table definition from QMS data and converts it to docjl
    table format. The TableAnalyzer will automatically decide whether
    to use longtable or table environment based on row count.

    Args:
        table_def: Table definition dict with:
            - title: Table title (string)
            - columns: List of column keys (e.g., ["id", "name_hu", "name_en"])
            - column_names: List of column display names
            - data: List of row dicts

    Returns:
        docjl table structure dict

    Example:
        >>> table_def = {
        ...     "title": "Rövidítések jegyzéke",
        ...     "columns": ["id", "name_hu", "name_en"],
        ...     "column_names": ["Rövidítés", "Magyar", "Angol"],
        ...     "data": [{"id": "CAPA", "name_hu": "Helyesbítő...", "name_en": "Corrective..."}]
        ... }
        >>> format_longtable(table_def)
        {'type': 'table', 'headers': [...], 'rows': [...], 'caption': '...'}
    """
    columns = table_def.get("columns", [])
    column_names = table_def.get("column_names", columns)
    data = table_def.get("data", [])
    title = table_def.get("title", "")
    description = table_def.get("description", "")

    # Build rows from data
    rows = []
    for row_dict in data:
        row = [row_dict.get(col, "") for col in columns]
        rows.append(row)

    # Caption: use title or description
    caption = title if title else description

    return {"type": "table", "headers": column_names, "rows": rows, "caption": caption}


def format_info_box(box_def: dict) -> list[dict]:
    """
    Format info box content to docjl inline array structure.

    Takes an info box definition (nahalert, nahinfo, nahreq, nahsec)
    and converts it to inline array format with bold labels and plain text.

    Args:
        box_def: Box definition dict with:
            - intro: Introduction text (optional)
            - items: List of items (optional)
            - closing: Closing text (optional)

    Returns:
        List of inline array elements with bold/text formatting

    Example:
        >>> box = {
        ...     "intro": "The following items apply:",
        ...     "items": ["Item 1", "Item 2"],
        ...     "closing": "Contact immediately!"
        ... }
        >>> format_info_box(box)
        [{'type': 'bold', 'content': 'The following items apply:'},
         {'type': 'text', 'content': '\\n\\n'},
         {'type': 'text', 'content': '• Item 1\\n• Item 2\\n\\n'},
         {'type': 'bold', 'content': 'Contact immediately!'}]
    """
    result = []

    # Intro (if exists)
    intro = box_def.get("intro", "")
    if intro:
        result.append({"type": "bold", "content": intro})
        result.append({"type": "text", "content": "\n\n"})

    # Items (if exists)
    items = box_def.get("items", [])
    if items:
        # Format as bullet list with proper bullet character
        # Using • (U+2022 BULLET) which renders correctly in LaTeX
        items_text = "\n".join([f"• {item}" for item in items])
        result.append({"type": "text", "content": items_text + "\n\n"})

    # Closing (if exists)
    closing = box_def.get("closing", "")
    if closing:
        result.append({"type": "bold", "content": closing})

    return result


# Auto-register all QMS transforms
TransformRegistry.register("format_standard_list", format_standard_list)
TransformRegistry.register("format_document_list", format_document_list)
TransformRegistry.register("format_regulation_list", format_regulation_list)
TransformRegistry.register("format_longtable", format_longtable)
TransformRegistry.register("format_info_box", format_info_box)
