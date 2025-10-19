#!/usr/bin/env python3
"""
QMS Conversion Script - Convert merged QMS data to docjl format.

This script uses the QMSConverter plugin to convert the merged QMS data
(created by build_qms.py) into docjl format ready for LaTeX generation.

Usage:
    python3 qms/convert.py

Output:
    qms/build/QMS_output.json - Final docjl format

Next step:
    Use docjl to convert to LaTeX:
    >>> from docjl import MarkdownJsonToDocjl
    >>> converter = MarkdownJsonToDocjl()
    >>> latex = converter.convert(json.dumps(docjl_data))
"""

import json
import sys
from pathlib import Path

from labor.converters import QMSConverter


def main() -> None:
    """Main conversion process."""
    print("=" * 70)
    print("QMS Conversion - Transform QMS data to docjl format")
    print("=" * 70)

    # Paths
    qms_dir = Path(__file__).parent
    build_dir = qms_dir / "build"

    input_path = build_dir / "QMS_full_input.json"
    template_path = build_dir / "QMS_full_template.json"
    format_path = build_dir / "QMS_full_format.json"
    output_path = build_dir / "QMS_output.json"

    # Check if build files exist
    if not input_path.exists():
        print(f"❌ Error: {input_path} not found")
        print("   Run build_qms.py first to generate merged files")
        sys.exit(1)

    if not template_path.exists():
        print(f"❌ Error: {template_path} not found")
        print("   Run build_qms.py first to generate merged files")
        sys.exit(1)

    if not format_path.exists():
        print(f"❌ Error: {format_path} not found")
        print("   Run build_qms.py first to generate merged files")
        sys.exit(1)

    # Convert
    print("\n🔄 Starting QMS conversion...")
    converter = QMSConverter()

    try:
        docjl = converter.convert(str(input_path), str(template_path), str(format_path))
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Save output
    print(f"\n💾 Saving output to {output_path}")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(docjl, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "=" * 70)
    print("✅ Conversion complete!")
    print(f"📁 Output file: {output_path}")
    block_count = len(docjl.get("docjll", []))
    print(f"📊 Total blocks: {block_count}")
    print("\n💡 Next step:")
    print("   Convert to LaTeX using docjl:")
    print("   >>> from docjl import MarkdownJsonToDocjl")
    print("   >>> import json")
    print(f"   >>> with open('{output_path}') as f:")
    print("   ...     docjl_data = json.load(f)")
    print("   >>> converter = MarkdownJsonToDocjl()")
    print("   >>> latex = converter.convert(json.dumps(docjl_data))")
    print("=" * 70)


if __name__ == "__main__":
    main()
