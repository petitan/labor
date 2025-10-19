"""Unit tests for calibration-specific transform functions."""

from labor.transforms.calibration_transforms import kmk_parameter_2_label, standards_description


class TestCalibrationTransforms:
    """Test calibration-specific transform functions."""

    def test_standards_description_single_item(self) -> None:
        """Test standards_description with single item."""
        items = [{"name": "Pressure calibrator Fluke 718", "accuracy": "±0.05%"}]
        result = standards_description(items)
        assert result == "Pressure calibrator Fluke 718 (Pontosság: ±0.05%)"

    def test_standards_description_multiple_items(self) -> None:
        """Test standards_description with multiple items."""
        items = [
            {"name": "Pressure calibrator Fluke 718", "accuracy": "±0.05%"},
            {"name": "Digital manometer Druck DPI104", "accuracy": "±0.1%"},
        ]
        result = standards_description(items)
        expected = (
            "Pressure calibrator Fluke 718 (Pontosság: ±0.05%)\n"
            "Digital manometer Druck DPI104 (Pontosság: ±0.1%)"
        )
        assert result == expected

    def test_standards_description_missing_accuracy(self) -> None:
        """Test standards_description with missing accuracy."""
        items = [{"name": "Pressure calibrator Fluke 718"}]
        result = standards_description(items)
        assert result == "Pressure calibrator Fluke 718"

    def test_standards_description_empty_list(self) -> None:
        """Test standards_description with empty list."""
        result = standards_description([])
        assert result == ""

    def test_standards_description_non_list(self) -> None:
        """Test standards_description with non-list input."""
        result = standards_description("not a list")  # type: ignore[arg-type]
        assert result == "not a list"

    def test_kmk_parameter_2_label_float(self) -> None:
        """Test kmk_parameter_2_label with float."""
        result = kmk_parameter_2_label(2.0)
        assert result == "Bővített bizonytalanság (k=2.0)"

    def test_kmk_parameter_2_label_int(self) -> None:
        """Test kmk_parameter_2_label with int."""
        result = kmk_parameter_2_label(2)
        assert result == "Bővített bizonytalanság (k=2)"

    def test_kmk_parameter_2_label_string(self) -> None:
        """Test kmk_parameter_2_label with string."""
        result = kmk_parameter_2_label("2.5")
        assert result == "Bővített bizonytalanság (k=2.5)"

    def test_kmk_parameter_2_label_none(self) -> None:
        """Test kmk_parameter_2_label with None defaults to 2.0."""
        result = kmk_parameter_2_label(None)  # type: ignore[arg-type]
        assert result == "Bővített bizonytalanság (k=2.0)"

    def test_kmk_parameter_2_label_zero(self) -> None:
        """Test kmk_parameter_2_label with zero defaults to 2.0."""
        result = kmk_parameter_2_label(0)
        assert result == "Bővített bizonytalanság (k=2.0)"
