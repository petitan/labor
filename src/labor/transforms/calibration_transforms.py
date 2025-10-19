"""Calibration-specific transform functions."""

from .registry import TransformRegistry


def standards_description(items: list[dict]) -> str:
    """
    Format standards list with accuracy information.

    Converts a list of calibration standards into a formatted description
    showing each standard's name and accuracy specification.

    Args:
        items: List of standard dicts with 'name' and 'accuracy' keys

    Returns:
        Formatted multi-line string with standards descriptions

    Example:
        >>> items = [
        ...     {"name": "Pressure calibrator Fluke 718", "accuracy": "±0.05%"},
        ...     {"name": "Digital manometer Druck DPI104", "accuracy": "±0.1%"}
        ... ]
        >>> standards_description(items)
        'Pressure calibrator Fluke 718 (Pontosság: ±0.05%)\\nDigital manometer Druck DPI104 (Pontosság: ±0.1%)'
    """
    if not isinstance(items, list):
        return str(items)

    lines = []
    for std in items:
        name = std.get("name", "")
        accuracy = std.get("accuracy", "")
        if name and accuracy:
            lines.append(f"{name} (Pontosság: {accuracy})")
        elif name:
            lines.append(name)

    return "\n".join(lines)


def kmk_parameter_2_label(coverage_factor: float | int | str) -> str:
    """
    Generate expanded uncertainty label with coverage factor.

    Creates a Hungarian label for expanded measurement uncertainty
    including the coverage factor (k value).

    Args:
        coverage_factor: Coverage factor value (typically 2.0)

    Returns:
        Formatted label string

    Example:
        >>> kmk_parameter_2_label(2.0)
        'Bővített bizonytalanság (k=2.0)'
        >>> kmk_parameter_2_label(2)
        'Bővített bizonytalanság (k=2)'
    """
    k = coverage_factor if coverage_factor else 2.0
    return f"Bővített bizonytalanság (k={k})"


# Auto-register all calibration transforms
TransformRegistry.register("standards_description", standards_description)
TransformRegistry.register("kmk_parameter_2_label", kmk_parameter_2_label)
