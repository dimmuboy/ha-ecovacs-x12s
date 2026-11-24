"""Experimental EU X12S profile without modifying installed packages."""
from dataclasses import replace
import importlib
import importlib.util
import logging
import sys
from types import ModuleType

from deebot_client.commands.json.map import GetMapSetV2
from deebot_client.events import RoomsEvent
from deebot_client.message import HandlingResult
from deebot_client.models import Room

_LOGGER = logging.getLogger(__name__)
EU = "deebot_client.hardware.sdr8vw"
US = "deebot_client.hardware.k5azjg"


class GetMapSetX12SEU(GetMapSetV2):
    """Handle the EU firmware's additional room field."""

    @classmethod
    def _handle_rooms_subsets(cls, event_bus, data, subsets, map_id):
        if subsets and all(
            isinstance(row, list)
            and len(row) == 13
            and isinstance(row[0], str)
            and row[0].isdigit()
            and isinstance(row[1], str)
            for row in subsets
        ):
            event_bus.notify(
                RoomsEvent(map_id, [Room(row[1], int(row[0]), "") for row in subsets])
            )
            return HandlingResult.success()
        return super()._handle_rooms_subsets(event_bus, data, subsets, map_id)


def install_alias() -> None:
    """Prefer native support; otherwise install the EU-specific profile."""
    if EU in sys.modules or importlib.util.find_spec(EU) is not None:
        return
    try:
        profile = importlib.import_module(US)
    except ModuleNotFoundError:
        _LOGGER.exception("X12S EU alias unavailable: US profile missing")
        return
    from deebot_client import hardware

    def get_device_info():
        info = profile.get_device_info()
        caps = info.capabilities
        map_caps = replace(
            caps.map, major=None, minor=None,
            set=replace(caps.map.set, execute=GetMapSetX12SEU),
        )
        return replace(info, capabilities=replace(caps, map=map_caps))

    alias = ModuleType(EU)
    alias.get_device_info = get_device_info
    sys.modules[EU] = alias
    hardware._NOT_FOUND.discard("sdr8vw")
    _LOGGER.info("Experimental EU X12S profile installed (sdr8vw, map V2)")
