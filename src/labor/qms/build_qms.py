#!/usr/bin/env python3
"""
QMS Build Script - Merge global + chapter data and generate full QMS document.

This script:
1. Merges global data with chapter-specific data
2. Combines all chapter templates into one
3. Combines all chapter format configs into one
4. Generates full QMS input JSON for converter
"""

import json
from pathlib import Path
from typing import Any


def load_json(filepath: Path) -> dict[str, Any]:
    """Load JSON file."""
    with filepath.open(encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def save_json(data: dict, filepath: Path) -> None:
    """Save JSON file with pretty formatting."""
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")


def merge_global_and_chapters(qms_dir: Path) -> dict:
    """
    Merge global data with all chapter-specific data.

    Returns:
        {
          "global": {...},
          "chapters": {
            "ch01": {...},
            "ch02": {...},
            ...
          }
        }
    """
    # Load global data
    global_file = qms_dir / "global" / "QMS_global_data.json"
    global_data = load_json(global_file)
    print(f"📖 Loaded global data from {global_file}")

    # Load chapter-specific data
    chapters = {}
    chapters_dir = qms_dir / "chapters"

    for i in range(1, 9):  # Chapters 1-8
        chapter_id = f"ch{i:02d}"
        chapter_file = chapters_dir / f"QMS_{chapter_id}_data.json"

        if chapter_file.exists():
            chapters[chapter_id] = load_json(chapter_file)
            print(f"📖 Loaded {chapter_id} data from {chapter_file}")
        else:
            print(f"⚠️  {chapter_id} data not found, skipping")

    # Merge
    full_input = {"global": global_data, "chapters": chapters}

    return full_input


def merge_templates(qms_dir: Path) -> dict:
    """
    Merge all chapter templates into one combined template.

    Returns:
        {
          "docjll": [
            ...chapter1 blocks...,
            ...chapter2 blocks...,
            ...
          ]
        }
    """
    templates_dir = qms_dir / "templates"
    combined_docjll = []

    for i in range(1, 9):  # Chapters 1-8
        chapter_id = f"ch{i:02d}"
        template_file = templates_dir / f"QMS_{chapter_id}_template.json"

        if template_file.exists():
            template = load_json(template_file)
            chapter_blocks = template.get("docjll", [])
            combined_docjll.extend(chapter_blocks)
            print(f"📖 Merged {chapter_id} template ({len(chapter_blocks)} blocks)")
        else:
            print(f"⚠️  {chapter_id} template not found, skipping")

    return {"docjll": combined_docjll}


def merge_formats(qms_dir: Path) -> dict:
    """
    Merge all chapter format configs into one.

    Returns:
        {
          "mappings": {
            ...ch01 mappings...,
            ...ch02 mappings...,
            ...
          }
        }
    """
    formats_dir = qms_dir / "formats"
    combined_mappings = {}

    for i in range(1, 9):  # Chapters 1-8
        chapter_id = f"ch{i:02d}"
        format_file = formats_dir / f"QMS_{chapter_id}_format.json"

        if format_file.exists():
            format_config = load_json(format_file)

            # Merge simple_mappings (legacy support)
            if "simple_mappings" in format_config:
                combined_mappings.update(format_config["simple_mappings"])
                print(
                    f"📖 Merged {chapter_id} simple_mappings ({len(format_config['simple_mappings'])} entries)"
                )

            # Merge complex_mappings (legacy) or mappings (new)
            if "complex_mappings" in format_config:
                combined_mappings.update(format_config["complex_mappings"])
                print(
                    f"📖 Merged {chapter_id} complex_mappings ({len(format_config['complex_mappings'])} entries)"
                )
            elif "mappings" in format_config:
                combined_mappings.update(format_config["mappings"])
                print(f"📖 Merged {chapter_id} mappings ({len(format_config['mappings'])} entries)")
        else:
            print(f"⚠️  {chapter_id} format not found, skipping")

    return {"mappings": combined_mappings}


def main() -> None:
    """Main build process."""
    print("=" * 60)
    print("QMS Build Script - Merging global + chapter data")
    print("=" * 60)

    # Paths
    qms_dir = Path(__file__).parent
    build_dir = qms_dir / "build"
    build_dir.mkdir(exist_ok=True)

    # Step 1: Merge data
    print("\n[1/3] Merging global + chapter data...")
    full_input = merge_global_and_chapters(qms_dir)
    save_json(full_input, build_dir / "QMS_full_input.json")

    # Step 2: Merge templates
    print("\n[2/3] Merging chapter templates...")
    full_template = merge_templates(qms_dir)
    save_json(full_template, build_dir / "QMS_full_template.json")

    # Step 3: Merge formats
    print("\n[3/3] Merging chapter format configs...")
    full_format = merge_formats(qms_dir)
    save_json(full_format, build_dir / "QMS_full_format.json")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Build complete!")
    print(f"📁 Output directory: {build_dir}")
    print(f"   - QMS_full_input.json ({len(full_input['chapters'])} chapters)")
    print(f"   - QMS_full_template.json ({len(full_template['docjll'])} blocks)")
    print(f"   - QMS_full_format.json ({len(full_format['mappings'])} mappings)")
    print("=" * 60)


if __name__ == "__main__":
    main()
