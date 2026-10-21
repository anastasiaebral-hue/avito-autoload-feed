import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from generate_feed import build_feed, load_items


class FeedGenerationTests(unittest.TestCase):
    def test_build_feed_includes_only_enabled_items(self):
        items = [
            {
                "id": "iron-001",
                "enabled": True,
                "title": "Утюг Haier HI-601 паровой 3100 Вт",
                "description": "Б/у, полностью исправен.",
                "address": "Санкт-Петербург",
                "price": 4290,
                "category": "Бытовая техника",
                "attributes": {
                    "AdType": "Товар приобретен на продажу",
                    "Condition": "Б/у",
                },
                "images": ["https://example.com/iron.jpg"],
            },
            {
                "id": "draft-001",
                "enabled": False,
                "title": "Черновик",
                "description": "Не публиковать",
                "address": "Санкт-Петербург",
                "price": 1,
                "category": "Другое",
                "attributes": {},
                "images": [],
            },
        ]

        xml_text = build_feed(items)
        root = ET.fromstring(xml_text)
        ads = root.findall("Ad")

        self.assertEqual(root.attrib, {"formatVersion": "3", "target": "Avito.ru"})
        self.assertEqual(len(ads), 1)
        self.assertEqual(ads[0].findtext("Id"), "iron-001")
        self.assertEqual(ads[0].findtext("Condition"), "Б/у")
        self.assertEqual(ads[0].find("Images/Image").attrib["url"], "https://example.com/iron.jpg")

    def test_build_feed_preserves_existing_avito_id(self):
        item = {
            "id": "scooter-001",
            "avito_id": "8187553274",
            "enabled": True,
            "title": "Самокат городской Decathlon Oxelo Town 7 XL",
            "description": "Исправен.",
            "address": "Санкт-Петербург",
            "price": 4000,
            "category": "Хобби и отдых",
            "attributes": {},
            "images": [],
        }

        ad = ET.fromstring(build_feed([item])).find("Ad")

        self.assertEqual(ad.findtext("AvitoId"), "8187553274")

    def test_build_feed_rejects_enabled_item_without_required_field(self):
        item = {
            "id": "broken",
            "enabled": True,
            "title": "Без цены",
            "description": "Исправен.",
            "address": "Санкт-Петербург",
            "category": "Другое",
            "attributes": {},
            "images": [],
        }

        with self.assertRaisesRegex(ValueError, "price"):
            build_feed([item])

    def test_load_items_requires_a_json_list(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "items.json"
            path.write_text('{"not": "a list"}', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON array"):
                load_items(path)


if __name__ == "__main__":
    unittest.main()
