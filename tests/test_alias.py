"""Verify the runtime alias against the pinned client (no robot required)."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import unittest

from deebot_client.hardware import get_static_device_info

path = Path(__file__).resolve().parents[1] / "custom_components/ecovacs/x12s_alias.py"
spec = importlib.util.spec_from_file_location("x12s_alias", path)
alias = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alias)


class AliasTest(unittest.IsolatedAsyncioTestCase):
    async def test_alias(self):
        us = await get_static_device_info("k5azjg")
        self.assertIsNotNone(us)
        await asyncio.to_thread(alias.install_alias)
        eu = await get_static_device_info("sdr8vw")
        self.assertIsNotNone(eu)
        self.assertIs(eu.capabilities.device_type, us.capabilities.device_type)
        self.assertIs(sys.modules[alias.EU].get_device_info,
                      sys.modules[alias.US].get_device_info)
