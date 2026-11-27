"""Regression tests for extended map appearance."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("map_style", Path(__file__).resolve().parents[1] / "custom_components/ecovacs/map_style.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -10 20 30"><g><path class="r0" d="M0 0"/></g><style>.r0{fill:#a2bce7}</style></svg>'

class ExtendedMapTest(unittest.TestCase):
    def test_rgb(self):
        self.assertEqual(mod.rgb_to_hex([1, 2, 255]), "#0102ff")
        self.assertEqual(mod.hex_to_rgb("#0102ff"), [1, 2, 255])

    def test_rotate_padding(self):
        result = mod.style_svg(SVG, mod.settings_key({"map_rotation":90,"map_padding":5}))
        root = ET.fromstring(result)
        self.assertEqual(root.attrib["viewBox"], "-15 -10 40 30")
        self.assertIn(b'rotate(90 5 5)', result)

    def test_opacity(self):
        result = mod.style_svg(SVG, mod.settings_key({"map_room_opacity":50}))
        self.assertIn(b'fill-opacity:0.5', result)
        ET.fromstring(result)
