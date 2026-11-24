"""Verify SVG customization without HA or a robot."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("map_style", Path(__file__).resolve().parents[1] / "custom_components/ecovacs/map_style.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -10 20 30"><g><path class="r0" d="M0 0"/></g><style>.r0{fill:#a2bce7}</style></svg>'


class MapStyleTest(unittest.TestCase):
    def test_default(self):
        self.assertEqual(mod.style_svg(SVG, mod.settings_key({})), SVG.encode())

    def test_custom(self):
        result = mod.style_svg(SVG, mod.settings_key({"map_background":"#123456","map_room_1":"#abcdef","map_show_path":False}))
        ET.fromstring(result)
        self.assertIn(b'x="-5" y="-10"', result)
        self.assertIn(b'.r0{fill:#abcdef}', result)
        self.assertIn(b'{display:none}', result)
        self.assertIs(result, mod.style_svg(SVG, mod.settings_key({"map_background":"#123456","map_room_1":"#abcdef","map_show_path":False})))

    def test_invalid(self):
        self.assertEqual(mod.style_svg(SVG, mod.settings_key({"map_room_1":"</style>"})), SVG.encode())
