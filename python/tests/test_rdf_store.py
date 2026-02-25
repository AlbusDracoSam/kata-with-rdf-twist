# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gilded_rose import Item
from rdf_store import (
    GR,
    RDFItemStore,
    TYPE_AGED_BRIE,
    TYPE_BACKSTAGE_PASS,
    TYPE_CONJURED,
    TYPE_NORMAL,
    TYPE_SULFURAS,
)


class RDFStoreTest(unittest.TestCase):
    def test_item_to_rdf_creates_expected_triples(self):
        store = RDFItemStore()
        uri = store.item_to_rdf(Item("Aged Brie", 2, 0), 0)

        self.assertEqual("Aged Brie", str(store.graph.value(uri, GR["name"])))
        self.assertEqual(2, int(store.graph.value(uri, GR["sellIn"])))
        self.assertEqual(0, int(store.graph.value(uri, GR["quality"])))
        self.assertEqual(TYPE_AGED_BRIE, store.graph.value(uri, GR["itemType"]))

    def test_item_type_detection(self):
        store = RDFItemStore()
        self.assertEqual(TYPE_SULFURAS, store._determine_item_type("Sulfuras, Hand of Ragnaros"))
        self.assertEqual(TYPE_AGED_BRIE, store._determine_item_type("Aged Brie"))
        self.assertEqual(
            TYPE_BACKSTAGE_PASS,
            store._determine_item_type("Backstage passes to a TAFKAL80ETC concert"),
        )
        self.assertEqual(TYPE_CONJURED, store._determine_item_type("Conjured Mana Cake"))
        self.assertEqual(TYPE_NORMAL, store._determine_item_type("+5 Dexterity Vest"))

    def test_rdf_to_item_syncs_values_back(self):
        store = RDFItemStore()
        item = Item("foo", 1, 1)
        uri = store.item_to_rdf(item, 1)
        store.update_quality()
        store.rdf_to_item(uri, item)

        self.assertEqual(0, item.sell_in)
        self.assertEqual(0, item.quality)

    def test_update_quality_applies_rules_in_graph(self):
        store = RDFItemStore()
        normal_uri = store.item_to_rdf(Item("foo", 0, 10), 1)
        conjured_uri = store.item_to_rdf(Item("Conjured Mana Cake", 0, 6), 2)
        brie_uri = store.item_to_rdf(Item("Aged Brie", 0, 10), 3)

        store.update_quality()

        self.assertEqual(-1, int(store.graph.value(normal_uri, GR["sellIn"])))
        self.assertEqual(8, int(store.graph.value(normal_uri, GR["quality"])))

        self.assertEqual(-1, int(store.graph.value(conjured_uri, GR["sellIn"])))
        self.assertEqual(2, int(store.graph.value(conjured_uri, GR["quality"])))

        self.assertEqual(-1, int(store.graph.value(brie_uri, GR["sellIn"])))
        self.assertEqual(12, int(store.graph.value(brie_uri, GR["quality"])))

    def test_serialize_and_load_inventory_round_trip_turtle(self):
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "inventory.ttl"
            store = RDFItemStore()
            original = Item("Conjured Mana Cake", 3, 6)
            uri = store.item_to_rdf(original, 9)
            store.serialize_inventory(str(file_path), rdf_format="turtle")

            loaded = RDFItemStore()
            loaded.load_inventory(str(file_path), rdf_format="ttl")

            restored = Item(original.name, original.sell_in, original.quality)
            loaded.rdf_to_item(uri, restored)

            self.assertEqual(3, restored.sell_in)
            self.assertEqual(6, restored.quality)

    def test_serialize_inventory_rejects_unknown_format(self):
        store = RDFItemStore()
        with self.assertRaises(ValueError):
            store.serialize_inventory("inventory.invalid", rdf_format="ntriples")


if __name__ == "__main__":
    unittest.main()
