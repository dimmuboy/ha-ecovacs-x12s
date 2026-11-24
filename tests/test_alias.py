"""Verify the EU profile and room parsing against the pinned client."""
import asyncio
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock

from deebot_client.hardware import get_static_device_info
from deebot_client.events import RoomsEvent
from deebot_client.message import HandlingState

path = Path(__file__).resolve().parents[1] / "custom_components/ecovacs/x12s_alias.py"
spec = importlib.util.spec_from_file_location("x12s_alias", path)
alias = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alias)


class AliasTest(unittest.IsolatedAsyncioTestCase):
    async def test_alias(self):
        us = await get_static_device_info("k5azjg")
        await asyncio.to_thread(alias.install_alias)
        eu = await get_static_device_info("sdr8vw")
        self.assertIsNotNone(eu)
        self.assertIs(eu.capabilities.device_type, us.capabilities.device_type)
        self.assertIsNone(eu.capabilities.map.major)
        self.assertIsNone(eu.capabilities.map.minor)
        self.assertIsNotNone(us.capabilities.map.major)
        self.assertIsNotNone(eu.capabilities.map.info)
        self.assertIs(eu.capabilities.map.set.execute, alias.GetMapSetX12SEU)

    async def test_room_format(self):
        bus = Mock()
        rows = [["3", "Test room", "6"] + ["0"] * 10,
                ["5", "Second room", "3"] + ["0"] * 10]
        result = alias.GetMapSetX12SEU._handle_rooms_subsets(
            bus, {"type": "ar", "mid": "test"}, rows, "test"
        )
        self.assertEqual(result.state, HandlingState.SUCCESS)
        self.assertFalse(result.args)
        event = bus.notify.call_args.args[0]
        self.assertIsInstance(event, RoomsEvent)
        self.assertEqual(event.map_id, "test")
        self.assertEqual([(r.id, r.name) for r in event.rooms],
                         [(3, "Test room"), (5, "Second room")])

    async def test_existing_format(self):
        bus = Mock()
        rows = [["7", "Old format"] + ["0"] * 8]
        result = alias.GetMapSetX12SEU._handle_rooms_subsets(
            bus, {"type": "ar", "mid": "test"}, rows, "test"
        )
        self.assertEqual(result.state, HandlingState.SUCCESS)
        self.assertEqual(bus.notify.call_args.args[0].rooms[0].id, 7)
