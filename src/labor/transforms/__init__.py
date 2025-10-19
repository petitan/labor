"""
Transforms package - Pluggable data transformation system.

Auto-discovers and registers all transform functions from submodules.
Also provides reusable formatting helpers for creating docjl inline arrays.
"""

# Import transform modules to trigger auto-registration
import contextlib

from . import (
    common_transforms,  # noqa: F401
    qms_transforms,  # noqa: F401
)

# Import formatting helpers for external use
from .formatting_helpers import (
    combine_inline_arrays,
    make_bold_label_value,
    make_bold_prefix,
    make_bold_text,
    make_info_box_content,
    make_italic_text,
    make_plain_text,
)
from .registry import TransformRegistry

# Try to import calibration_transforms if it exists (optional)
# Type ignore needed because mypy can't verify optional module at static analysis time
with contextlib.suppress(ImportError):
    from . import calibration_transforms as _calibration_transforms  # type: ignore  # noqa: F401

__all__ = [
    "TransformRegistry",
    # Formatting helpers
    "make_bold_prefix",
    "make_bold_label_value",
    "make_info_box_content",
    "make_bold_text",
    "make_italic_text",
    "make_plain_text",
    "combine_inline_arrays",
]

print(f"🔌 Loaded {len(TransformRegistry.list_transforms())} transforms:")
for name in TransformRegistry.list_transforms():
    print(f"   - {name}")
