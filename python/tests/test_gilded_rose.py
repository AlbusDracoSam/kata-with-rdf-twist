# -*- coding: utf-8 -*-
import unittest

from gilded_rose import GildedRose, Item


def update_once(item):
    items = [item]
    GildedRose(items).update_quality()
    return items[0]


class GildedRoseTest(unittest.TestCase):
    def test_normal_item_before_sell_date(self):
        item = update_once(Item("foo", 10, 20))
        self.assertEqual("foo", item.name)
        self.assertEqual(9, item.sell_in)
        self.assertEqual(19, item.quality)

    def test_normal_item_after_sell_date(self):
        item = update_once(Item("foo", 0, 10))
        self.assertEqual(-1, item.sell_in)
        self.assertEqual(8, item.quality)

    def test_quality_never_negative(self):
        item = update_once(Item("foo", 0, 0))
        self.assertEqual(-1, item.sell_in)
        self.assertEqual(0, item.quality)

    def test_aged_brie_increases_quality(self):
        item = update_once(Item("Aged Brie", 2, 0))
        self.assertEqual(1, item.sell_in)
        self.assertEqual(1, item.quality)

    def test_aged_brie_increases_twice_after_expiry(self):
        item = update_once(Item("Aged Brie", 0, 10))
        self.assertEqual(-1, item.sell_in)
        self.assertEqual(12, item.quality)

    def test_aged_brie_capped_at_50(self):
        item = update_once(Item("Aged Brie", 2, 50))
        self.assertEqual(1, item.sell_in)
        self.assertEqual(50, item.quality)

    def test_sulfuras_never_changes(self):
        item = update_once(Item("Sulfuras, Hand of Ragnaros", 0, 80))
        self.assertEqual(0, item.sell_in)
        self.assertEqual(80, item.quality)

    def test_backstage_increase_by_1_when_more_than_10_days(self):
        item = update_once(Item("Backstage passes to a TAFKAL80ETC concert", 11, 10))
        self.assertEqual(10, item.sell_in)
        self.assertEqual(11, item.quality)

    def test_backstage_increase_by_2_when_10_or_less_days(self):
        item = update_once(Item("Backstage passes to a TAFKAL80ETC concert", 10, 10))
        self.assertEqual(9, item.sell_in)
        self.assertEqual(12, item.quality)

    def test_backstage_increase_by_3_when_5_or_less_days(self):
        item = update_once(Item("Backstage passes to a TAFKAL80ETC concert", 5, 10))
        self.assertEqual(4, item.sell_in)
        self.assertEqual(13, item.quality)

    def test_backstage_drops_to_zero_after_concert(self):
        item = update_once(Item("Backstage passes to a TAFKAL80ETC concert", 0, 10))
        self.assertEqual(-1, item.sell_in)
        self.assertEqual(0, item.quality)

    def test_conjured_degrades_twice_as_fast(self):
        item = update_once(Item("Conjured Mana Cake", 3, 6))
        self.assertEqual(2, item.sell_in)
        self.assertEqual(4, item.quality)

    def test_conjured_degrades_four_after_expiry(self):
        item = update_once(Item("Conjured Mana Cake", 0, 6))
        self.assertEqual(-1, item.sell_in)
        self.assertEqual(2, item.quality)

    def test_conjured_never_negative(self):
        item = update_once(Item("Conjured Mana Cake", 0, 3))
        self.assertEqual(-1, item.sell_in)
        self.assertEqual(0, item.quality)


if __name__ == "__main__":
    unittest.main()
