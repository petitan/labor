"""Unit tests for TransformRegistry."""

import pytest

from labor.transforms.registry import TransformRegistry


class TestTransformRegistry:
    """Test TransformRegistry functionality."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        TransformRegistry.clear()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        TransformRegistry.clear()

    def test_register_transform(self) -> None:
        """Test registering a transform function."""

        def my_transform(value: str) -> str:
            return value.upper()

        TransformRegistry.register("my_transform", my_transform)
        assert "my_transform" in TransformRegistry.list_transforms()

    def test_register_overwrite_warning(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that overwriting a transform shows warning."""

        def transform1(value: str) -> str:
            return value.upper()

        def transform2(value: str) -> str:
            return value.lower()

        TransformRegistry.register("test", transform1)
        TransformRegistry.register("test", transform2)

        captured = capsys.readouterr()
        assert "Warning: Overwriting existing transform 'test'" in captured.out

    def test_get_existing_transform(self) -> None:
        """Test getting a registered transform."""

        def my_transform(value: str) -> str:
            return value.upper()

        TransformRegistry.register("my_transform", my_transform)
        func = TransformRegistry.get("my_transform")
        assert func("hello") == "HELLO"

    def test_get_nonexistent_transform(self) -> None:
        """Test getting a non-existent transform raises ValueError."""
        with pytest.raises(ValueError, match="Unknown transform: 'nonexistent'"):
            TransformRegistry.get("nonexistent")

    def test_apply_transform_without_params(self) -> None:
        """Test applying a transform without parameters."""

        def uppercase(value: str) -> str:
            return value.upper()

        TransformRegistry.register("uppercase", uppercase)
        result = TransformRegistry.apply("uppercase", "hello")
        assert result == "HELLO"

    def test_apply_transform_with_params(self) -> None:
        """Test applying a transform with parameters."""

        def join_with_sep(items: list, separator: str = ", ") -> str:
            return separator.join(items)

        TransformRegistry.register("join", join_with_sep)
        result = TransformRegistry.apply("join", ["a", "b", "c"], {"separator": " + "})
        assert result == "a + b + c"

    def test_list_transforms(self) -> None:
        """Test listing all registered transforms."""

        def transform1(value: str) -> str:
            return value

        def transform2(value: str) -> str:
            return value

        TransformRegistry.register("transform1", transform1)
        TransformRegistry.register("transform2", transform2)

        transforms = TransformRegistry.list_transforms()
        assert transforms == ["transform1", "transform2"]

    def test_clear_transforms(self) -> None:
        """Test clearing all transforms."""

        def my_transform(value: str) -> str:
            return value

        TransformRegistry.register("my_transform", my_transform)
        assert len(TransformRegistry.list_transforms()) > 0

        TransformRegistry.clear()
        assert len(TransformRegistry.list_transforms()) == 0
