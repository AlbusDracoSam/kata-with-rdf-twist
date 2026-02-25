# -*- coding: utf-8 -*-
"""RDF-backed inventory store for the Gilded Rose kata."""

import os

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

# Define namespace for Gilded Rose ontology
GR = Namespace("http://example.org/gilded-rose#")

# Item type URIs for business rules
TYPE_SULFURAS = GR["Sulfuras"]
TYPE_AGED_BRIE = GR["AgedBrie"]
TYPE_BACKSTAGE_PASS = GR["BackstagePass"]
TYPE_CONJURED = GR["Conjured"]
TYPE_NORMAL = GR["NormalItem"]


class RDFItemStore:
    """
    Manages items as RDF triples and provides methods for quality updates.
    Converts Item objects to RDF, runs quality rules on the graph, then syncs back.
    """

    def __init__(self):
        """Initialize the RDF graph and load schema."""
        self.graph = Graph()
        self.graph.bind("gr", GR)
        self._load_schema()
        self._supported_formats = {
            "turtle": "turtle",
            "ttl": "turtle",
            "xml": "xml",
            "rdfxml": "xml",
            "json-ld": "json-ld",
            "jsonld": "json-ld",
        }

    def _load_schema(self):
        """Load the RDF schema from schema.ttl (path relative to this module)."""
        schema_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(schema_dir, "schema.ttl")
        try:
            self.graph.parse(schema_path, format="turtle")
        except Exception as e:
            raise RuntimeError(f"Failed to load schema.ttl: {e}") from e

    def _determine_item_type(self, name: str) -> URIRef:
        """
        Map item name to the appropriate gr:ItemType URI.
        Order matters: check specific names (e.g. Sulfuras, Conjured) before generic.
        """
        if name is None:
            return TYPE_NORMAL
        name_str = str(name).strip()
        if "Sulfuras" in name_str:
            return TYPE_SULFURAS
        if "Aged Brie" in name_str:
            return TYPE_AGED_BRIE
        if "Backstage passes" in name_str:
            return TYPE_BACKSTAGE_PASS
        if "Conjured" in name_str:
            return TYPE_CONJURED
        return TYPE_NORMAL

    def _resolve_format(self, rdf_format: str) -> str:
        """Normalize format aliases to an rdflib serializer/parser format."""
        normalized = str(rdf_format).strip().lower()
        if normalized not in self._supported_formats:
            raise ValueError(
                "Unsupported RDF format. Use one of: turtle/ttl, xml/rdfxml, json-ld/jsonld"
            )
        return self._supported_formats[normalized]

    def item_to_rdf(self, item, item_id: int) -> URIRef:
        """
        Convert an Item to RDF triples and add them to the graph.
        Creates a unique URI (gr:item/0, gr:item/1, ...), adds name, sellIn, quality, itemType.
        """
        uri = GR[f"item/{item_id}"]
        self.graph.add((uri, RDF.type, GR["Item"]))
        self.graph.add((uri, GR["name"], Literal(item.name, datatype=XSD.string)))
        self.graph.add((uri, GR["sellIn"], Literal(item.sell_in, datatype=XSD.integer)))
        self.graph.add((uri, GR["quality"], Literal(item.quality, datatype=XSD.integer)))
        self.graph.add((uri, GR["itemType"], self._determine_item_type(item.name)))
        return uri

    def rdf_to_item(self, item_uri: URIRef, item):
        """
        Read sellIn and quality from the graph for the given item URI and set them on the Item.
        Name is not modified (per kata rules).
        """
        sell_in_val = self.graph.value(item_uri, GR["sellIn"])
        quality_val = self.graph.value(item_uri, GR["quality"])
        if sell_in_val is not None:
            item.sell_in = int(sell_in_val)
        if quality_val is not None:
            item.quality = int(quality_val)

    def serialize_inventory(self, path: str, rdf_format: str = "turtle"):
        """
        Persist the inventory graph to disk in an RDF format.
        Supported formats: turtle, xml, json-ld (plus aliases).
        """
        resolved = self._resolve_format(rdf_format)
        self.graph.serialize(destination=path, format=resolved)

    def load_inventory(self, path: str, rdf_format: str = "turtle"):
        """
        Load persisted RDF inventory into this graph.
        Keeps schema + previously loaded data and parses additional triples.
        """
        resolved = self._resolve_format(rdf_format)
        self.graph.parse(path, format=resolved)

    def _get_inventory_item_uris(self):
        """Return URIs of all inventory items (subjects that have gr:sellIn)."""
        return set(self.graph.subjects(GR["sellIn"], None))

    def _apply_quality_rules(self, item_uri: URIRef):
        """
        Apply one day's quality/sellIn update for a single item in the graph.
        Reads itemType, sellIn, quality; computes new values; updates triples.
        """
        item_type = self.graph.value(item_uri, GR["itemType"])
        sell_in_val = self.graph.value(item_uri, GR["sellIn"])
        quality_val = self.graph.value(item_uri, GR["quality"])
        if item_type is None or sell_in_val is None or quality_val is None:
            return
        sell_in = int(sell_in_val)
        quality = int(quality_val)

        if item_type == TYPE_SULFURAS:
            new_sell_in, new_quality = sell_in, quality
        else:
            new_sell_in = sell_in - 1
            if item_type == TYPE_AGED_BRIE:
                delta = 2 if new_sell_in < 0 else 1
                new_quality = min(50, quality + delta)
            elif item_type == TYPE_BACKSTAGE_PASS:
                if new_sell_in < 0:
                    new_quality = 0
                elif new_sell_in < 5:
                    new_quality = min(50, quality + 3)
                elif new_sell_in < 10:
                    new_quality = min(50, quality + 2)
                else:
                    new_quality = min(50, quality + 1)
            elif item_type == TYPE_CONJURED:
                delta = 4 if new_sell_in < 0 else 2
                new_quality = max(0, quality - delta)
            else:
                # Normal
                delta = 2 if new_sell_in < 0 else 1
                new_quality = max(0, quality - delta)

        # Update graph: remove old triples, add new (RDF is immutable triples)
        self.graph.remove((item_uri, GR["sellIn"], sell_in_val))
        self.graph.remove((item_uri, GR["quality"], quality_val))
        self.graph.add((item_uri, GR["sellIn"], Literal(new_sell_in, datatype=XSD.integer)))
        self.graph.add((item_uri, GR["quality"], Literal(new_quality, datatype=XSD.integer)))

    def update_quality(self):
        """
        Update sellIn and quality for every inventory item in the graph
        according to Gilded Rose rules (Normal, Aged Brie, Sulfuras, Backstage, Conjured).
        """
        for item_uri in self._get_inventory_item_uris():
            self._apply_quality_rules(item_uri)
