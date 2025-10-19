"""
Converter Plugins - Pluggable document converters.

This package provides a plugin-based converter system where each document type
(QMS, Calibration, etc.) has its own dedicated converter that uses the shared
Transform Registry for data transformations.

Available converters:
- QMSConverter: ISO 17025 Quality Management System documents
- CalibrationConverter: Calibration procedure documents

Example:
    >>> from converters import QMSConverter
    >>> converter = QMSConverter()
    >>> docjl = converter.convert('qms/build/QMS_full_input.json',
    ...                           'qms/build/QMS_full_template.json',
    ...                           'qms/build/QMS_full_format.json')
"""

from .base_converter import BaseConverter
from .calibration_converter import CalibrationConverter
from .qms_converter import QMSConverter

__all__ = ["BaseConverter", "CalibrationConverter", "QMSConverter"]
