"""Unit tests for QMS-specific transform functions."""

from labor.transforms.qms_transforms import (
    format_document_list,
    format_info_box,
    format_longtable,
    format_regulation_list,
    format_standard_list,
)


class TestQMSTransforms:
    """Test QMS-specific transform functions."""

    def test_format_standard_list_single_item(self) -> None:
        """Test format_standard_list with single item."""
        items = [{"id": "ISO 17025:2018", "name_hu": "Requirements"}]
        result = format_standard_list(items)
        expected = [
            [
                {"type": "bold", "content": "ISO 17025:2018"},
                {"type": "text", "content": " -- Requirements*"},
            ]
        ]
        assert result == expected

    def test_format_standard_list_multiple_items(self) -> None:
        """Test format_standard_list with multiple items."""
        items = [
            {"id": "ISO 17025:2018", "name_hu": "Requirements"},
            {"id": "ISO 9001:2015", "name_hu": "Quality Management"},
        ]
        result = format_standard_list(items)
        assert len(result) == 2
        assert result[0][0]["content"] == "ISO 17025:2018"
        assert result[1][0]["content"] == "ISO 9001:2015"

    def test_format_standard_list_empty(self) -> None:
        """Test format_standard_list with empty list."""
        result = format_standard_list([])
        assert result == []

    def test_format_document_list_single_item(self) -> None:
        """Test format_document_list with single item."""
        items = [{"id": "ILAC-P8:11/2023", "name_hu": "MRA Requirements"}]
        result = format_document_list(items)
        expected = [
            [
                {"type": "bold", "content": "ILAC-P8:11/2023"},
                {"type": "text", "content": " -- MRA Requirements*"},
            ]
        ]
        assert result == expected

    def test_format_document_list_multiple_items(self) -> None:
        """Test format_document_list with multiple items."""
        items = [
            {"id": "NAR-87", "name_hu": "Impartiality requirements"},
            {"id": "ILAC-P8:11/2023", "name_hu": "MRA Requirements"},
        ]
        result = format_document_list(items)
        assert len(result) == 2
        assert result[0][0]["content"] == "NAR-87"
        assert result[1][0]["content"] == "ILAC-P8:11/2023"

    def test_format_document_list_empty(self) -> None:
        """Test format_document_list with empty list."""
        result = format_document_list([])
        assert result == []

    def test_format_regulation_list_single_item(self) -> None:
        """Test format_regulation_list with single item."""
        items = [{"id": "1/1990 (IX.29) KHVM", "name_hu": "requirements"}]
        result = format_regulation_list(items)
        expected = [
            [
                {"type": "bold", "content": "1/1990 (IX.29) KHVM"},
                {"type": "text", "content": " rendelet requirements*"},
            ]
        ]
        assert result == expected

    def test_format_regulation_list_multiple_items(self) -> None:
        """Test format_regulation_list with multiple items."""
        items = [
            {"id": "1/1990 (IX.29) KHVM", "name_hu": "requirements"},
            {"id": "2/2024 (I.1) VM", "name_hu": "measurement standards"},
        ]
        result = format_regulation_list(items)
        assert len(result) == 2
        assert "rendelet requirements*" in result[0][1]["content"]
        assert "rendelet measurement standards*" in result[1][1]["content"]

    def test_format_regulation_list_empty(self) -> None:
        """Test format_regulation_list with empty list."""
        result = format_regulation_list([])
        assert result == []

    def test_format_longtable_complete(self) -> None:
        """Test format_longtable with complete table definition."""
        table_def = {
            "title": "Test Table",
            "columns": ["id", "name_hu", "name_en"],
            "column_names": ["ID", "Hungarian", "English"],
            "data": [
                {"id": "CAPA", "name_hu": "Helyesbítő", "name_en": "Corrective"},
                {"id": "QMS", "name_hu": "Minőségirányítás", "name_en": "Quality"},
            ],
        }
        result = format_longtable(table_def)

        assert result["type"] == "table"
        assert result["headers"] == ["ID", "Hungarian", "English"]
        assert result["caption"] == "Test Table"
        assert len(result["rows"]) == 2
        assert result["rows"][0] == ["CAPA", "Helyesbítő", "Corrective"]
        assert result["rows"][1] == ["QMS", "Minőségirányítás", "Quality"]

    def test_format_longtable_minimal(self) -> None:
        """Test format_longtable with minimal definition."""
        table_def = {"data": [{"col1": "value1"}], "columns": ["col1"]}
        result = format_longtable(table_def)

        assert result["type"] == "table"
        assert result["headers"] == ["col1"]
        assert result["rows"] == [["value1"]]
        assert result["caption"] == ""

    def test_format_longtable_with_description(self) -> None:
        """Test format_longtable uses description if no title."""
        table_def = {
            "description": "Table description",
            "columns": ["col"],
            "data": [{"col": "val"}],
        }
        result = format_longtable(table_def)
        assert result["caption"] == "Table description"

    def test_format_longtable_title_over_description(self) -> None:
        """Test format_longtable prefers title over description."""
        table_def = {
            "title": "Title",
            "description": "Description",
            "columns": ["col"],
            "data": [{"col": "val"}],
        }
        result = format_longtable(table_def)
        assert result["caption"] == "Title"

    def test_format_longtable_empty_data(self) -> None:
        """Test format_longtable with empty data."""
        table_def = {"columns": ["col1", "col2"], "data": []}
        result = format_longtable(table_def)

        assert result["type"] == "table"
        assert result["rows"] == []

    def test_format_longtable_missing_column_values(self) -> None:
        """Test format_longtable handles missing column values."""
        table_def = {
            "columns": ["col1", "col2", "col3"],
            "data": [{"col1": "val1", "col3": "val3"}],  # col2 missing
        }
        result = format_longtable(table_def)
        assert result["rows"][0] == ["val1", "", "val3"]

    def test_format_info_box_complete(self) -> None:
        """Test format_info_box with all fields."""
        box_def = {
            "intro": "Introduction text",
            "items": ["Item 1", "Item 2"],
            "closing": "Closing text",
        }
        result = format_info_box(box_def)

        assert len(result) == 5
        assert result[0] == {"type": "bold", "content": "Introduction text"}
        assert result[1] == {"type": "text", "content": "\n\n"}
        assert result[2]["type"] == "list_inline"
        assert result[2]["list_type"] == "itemize"
        assert result[2]["items"] == ["Item 1", "Item 2"]
        assert result[3] == {"type": "text", "content": "\n\n"}
        assert result[4] == {"type": "bold", "content": "Closing text"}

    def test_format_info_box_intro_only(self) -> None:
        """Test format_info_box with intro only."""
        box_def = {"intro": "Introduction"}
        result = format_info_box(box_def)

        assert len(result) == 2
        assert result[0] == {"type": "bold", "content": "Introduction"}
        assert result[1] == {"type": "text", "content": "\n\n"}

    def test_format_info_box_items_only(self) -> None:
        """Test format_info_box with items only."""
        box_def = {"items": ["Item 1", "Item 2"]}
        result = format_info_box(box_def)

        assert len(result) == 2
        assert result[0]["type"] == "list_inline"
        assert result[0]["items"] == ["Item 1", "Item 2"]

    def test_format_info_box_closing_only(self) -> None:
        """Test format_info_box with closing only."""
        box_def = {"closing": "Closing"}
        result = format_info_box(box_def)

        assert len(result) == 1
        assert result[0] == {"type": "bold", "content": "Closing"}

    def test_format_info_box_empty(self) -> None:
        """Test format_info_box with empty definition."""
        result = format_info_box({})
        assert result == []
