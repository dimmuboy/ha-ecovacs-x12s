"""Experimental EU X12S alias without modifying installed packages."""
import importlib
import importlib.util
import logging
import sys
from types import ModuleType

_LOGGER = logging.getLogger(__name__)
EU = "deebot_client.hardware.sdr8vw"
US = "deebot_client.hardware.k5azjg"


def install_alias() -> None:
    """Prefer native support; otherwise register a process-local module alias."""
    if EU in sys.modules or importlib.util.find_spec(EU) is not None:
        return
    try:
        profile = importlib.import_module(US)
    except ModuleNotFoundError:
        _LOGGER.exception("X12S EU alias unavailable: US profile missing")
        return
    from deebot_client import hardware
    alias = ModuleType(EU)
    alias.get_device_info = profile.get_device_info
    sys.modules[EU] = alias
    hardware._NOT_FOUND.discard("sdr8vw")
    _LOGGER.info("Experimental EU X12S profile alias installed (sdr8vw)")
