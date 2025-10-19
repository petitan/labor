#!/usr/bin/env python3
"""
Migration script: paragraph+metadata.box_style → petitan_box

Ez a script automatikusan konvertálja a régi formátumot az újra:
  Előtt: {"type": "paragraph", "metadata": {"box_style": "nahinfo", ...}, "content": ...}
  Utána: {"type": "petitan_box", "style": "nahinfo", "title": ..., "content": ...}

Usage:
    python scripts/migrate_box_style.py <file_or_directory>
    python scripts/migrate_box_style.py src/labor/qms/templates/
    python scripts/migrate_box_style.py src/labor/qms/templates/QMS_ch04_template.json

v2.2.7: Refactoring - tcolorbox functionality moved from docjl core to plugin.
"""

import json
import sys
from pathlib import Path


def migrate_block(block: dict) -> dict:
    """
    Migrálja a paragraph+metadata.box_style blokkot petitan_box-ra.

    Args:
        block: JSON block dictionary

    Returns:
        Migrált block (petitan_box vagy eredeti)
    """
    # Csak paragraph blokkokat dolgozzuk fel
    if block.get("type") != "paragraph":
        return block

    # Ellenőrizzük van-e metadata.box_style
    metadata = block.get("metadata", {})
    box_style = metadata.get("box_style")

    if not box_style:
        # Nincs box_style, visszaadjuk változatlanul
        return block

    # Migráció: paragraph → petitan_box
    migrated = {
        "type": "petitan_box",
        "style": box_style,
        "content": block.get("content", ""),
    }

    # Opcionális box_title átmásolás
    box_title = metadata.get("box_title")
    if box_title:
        migrated["title"] = box_title

    # Metadata-ból eltávolítjuk a box_style és box_title-t
    remaining_metadata = {k: v for k, v in metadata.items() if k not in ["box_style", "box_title"]}

    # Ha maradt metadata (pl. iso_mandatory), átmásoljuk
    if remaining_metadata:
        migrated["metadata"] = remaining_metadata

    return migrated


def migrate_json_file(file_path: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Migrál egy JSON fájlt.

    Args:
        file_path: JSON fájl útvonala
        dry_run: Ha True, nem ment, csak számolja a változásokat

    Returns:
        (total_blocks, migrated_count)
    """
    print(f"Processing: {file_path}")

    with file_path.open(encoding="utf-8") as f:
        data = json.load(f)

    # Feltételezzük docjl JSON struktúrát
    if "docjll" not in data:
        print("  ⚠ Nincs 'docjll' kulcs, kihagyva.")
        return (0, 0)

    blocks = data["docjll"]
    migrated_count = 0
    total_blocks = len(blocks)

    # Migráljuk a blokkokat
    new_blocks = []
    for block in blocks:
        original_type = block.get("type")
        migrated_block = migrate_block(block)

        if migrated_block.get("type") == "petitan_box" and original_type == "paragraph":
            migrated_count += 1
            print(f"  ✓ Migrated: paragraph → petitan_box (style: {migrated_block['style']})")

        new_blocks.append(migrated_block)

    data["docjll"] = new_blocks

    # Mentés (ha nem dry run)
    if not dry_run and migrated_count > 0:
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  💾 Saved: {migrated_count}/{total_blocks} blocks migrated")
    elif dry_run and migrated_count > 0:
        print(f"  🔍 DRY RUN: {migrated_count}/{total_blocks} blocks would be migrated")

    return (total_blocks, migrated_count)


def main() -> None:
    """Fő migráló logika."""
    if len(sys.argv) < 2:
        print("Usage: python migrate_box_style.py <file_or_directory> [--dry-run]")
        sys.exit(1)

    target = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")

    # Fájl vagy directory?
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.rglob("*.json"))
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    # Migráció
    total_files = 0
    total_blocks = 0
    total_migrated = 0

    for file_path in files:
        blocks, migrated = migrate_json_file(file_path, dry_run=dry_run)
        if blocks > 0:
            total_files += 1
            total_blocks += blocks
            total_migrated += migrated

    # Összesítés
    print()
    print("=" * 60)
    print(f"Migration {'dry run ' if dry_run else ''}complete!")
    print(f"  Files processed: {total_files}")
    print(f"  Total blocks: {total_blocks}")
    print(f"  Migrated blocks: {total_migrated}")
    print("=" * 60)


if __name__ == "__main__":
    main()
