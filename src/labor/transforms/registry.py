"""Transform Registry - Plugin system for data transformations."""

from collections.abc import Callable
from typing import Any


class TransformRegistry:
    """
    Registry for pluggable transform functions.

    Transforms are functions that convert input data to desired output format.
    This allows easy extension without modifying the core converter.

    Example:
        >>> def uppercase(value: str) -> str:
        ...     return value.upper()
        >>> TransformRegistry.register("uppercase", uppercase)
        >>> TransformRegistry.apply("uppercase", "hello")
        'HELLO'
    """

    _transforms: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, func: Callable) -> None:
        """
        Register a transform function.

        Args:
            name: Transform name (e.g., "join_with_separator")
            func: Transform function (signature: (value, **params) -> Any)
        """
        if name in cls._transforms:
            print(f"⚠️  Warning: Overwriting existing transform '{name}'")
        cls._transforms[name] = func
        print(f"✅ Registered transform: {name}")

    @classmethod
    def get(cls, name: str) -> Callable:
        """
        Get a registered transform function.

        Args:
            name: Transform name

        Returns:
            Transform function

        Raises:
            ValueError: If transform not found
        """
        if name not in cls._transforms:
            available = ", ".join(cls._transforms.keys())
            raise ValueError(f"Unknown transform: '{name}'. Available transforms: {available}")
        return cls._transforms[name]

    @classmethod
    def apply(cls, name: str, value: Any, params: dict | None = None) -> Any:
        """
        Apply a transform to a value.

        Args:
            name: Transform name
            value: Input value
            params: Optional parameters for the transform

        Returns:
            Transformed value

        Example:
            >>> TransformRegistry.apply("join", ["a", "b"], {"separator": " + "})
            'a + b'
        """
        transform = cls.get(name)

        if params:
            return transform(value, **params)
        return transform(value)

    @classmethod
    def list_transforms(cls) -> list[str]:
        """List all registered transform names."""
        return sorted(cls._transforms.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered transforms (for testing)."""
        cls._transforms.clear()
