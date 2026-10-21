#!/usr/bin/env python3
"""Generate an Avito autoload XML feed from data/items.json."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("id", "title", "description", "address", "price", "category")


def load_items(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("items file must contain a JSON array")
    return data


def _add_text(parent: ET.Element, tag: str, value: Any) -> None:
    if value is None or value == "":
        return
    ET.SubElement(parent, tag).text = str(value)


def build_feed(items: list[dict[str, Any]]) -> str:
    root = ET.Element("Ads", {"formatVersion": "3", "target": "Avito.ru"})

    for item in items:
        if not item.get("enabled", False):
            continue

        for field in REQUIRED_FIELDS:
            if item.get(field) in (None, ""):
                raise ValueError(f"enabled item {item.get('id', '<unknown>')} is missing {field}")

        ad = ET.SubElement(root, "Ad")
        _add_text(ad, "Id", item["id"])
        _add_text(ad, "AvitoId", item.get("avito_id"))
        _add_text(ad, "Address", item["address"])
        _add_text(ad, "Title", item["title"])
        _add_text(ad, "Description", item["description"])

        images = item.get("images", [])
        if images:
            images_element = ET.SubElement(ad, "Images")
            for url in images:
                ET.SubElement(images_element, "Image", {"url": str(url)})

        _add_text(ad, "Category", item["category"])
        _add_text(ad, "Price", item["price"])

        attributes = item.get("attributes", {})
        if not isinstance(attributes, dict):
            raise ValueError(f"attributes for {item['id']} must be an object")
        for tag, value in attributes.items():
            _add_text(ad, tag, value)

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/items.json"))
    parser.add_argument("--output", type=Path, default=Path("public/avito.xml"))
    args = parser.parse_args()

    xml_text = build_feed(load_items(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml_text, encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
