"""Check that custom integration translations contain no Core build references."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components/ecovacs"


class TranslationTest(unittest.TestCase):
    def test_no_unresolved_references(self):
        for path in [ROOT / "strings.json", * (ROOT / "translations").glob("*.json")]:
            with self.subTest(path=path):
                raw = path.read_text(encoding="utf-8")
                json.loads(raw)
                self.assertNotIn("[%key:", raw)
