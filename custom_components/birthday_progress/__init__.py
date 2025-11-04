"""
Birthday Progress Integration for Home Assistant.

This integration allows tracking multiple people's birthdays with real-time
age calculation, progress toward next birthday, and countdown timers.
"""
from __future__ import annotations

import logging
from typing import Any

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import update_coordinator
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """
    Set up the Birthday Progress integration.

    Args:
        hass: Home Assistant instance
        config: Configuration dictionary

    Returns:
        True if setup successful, False otherwise
    """
    # Domain-level setup - minimal since we use config entries
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up Birthday Progress from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Configuration entry for this integration

    Returns:
        True if setup successful, False otherwise
    """
    # Initialize coordinator for this entry
    coordinator = BirthdayProgressCoordinator(hass, entry)

    # Store coordinator in hass.data
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward entry setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload a Birthday Progress config entry.

    Args:
        hass: Home Assistant instance
        entry: Configuration entry to unload

    Returns:
        True if unload successful, False otherwise
    """
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove coordinator from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Handle removal of a Birthday Progress entry.

    Args:
        hass: Home Assistant instance
        entry: Configuration entry being removed
    """
    _LOGGER.info("Removing Birthday Progress entry: %s", entry.data.get("name"))


class BirthdayProgressCoordinator(update_coordinator.DataUpdateCoordinator):
    """
    Coordinator for Birthday Progress data updates.

    Handles periodic updates to refresh birthday calculations.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """
        Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            entry: Configuration entry
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=1),
        )
        self.entry = entry
        self.name = entry.data.get("name", "Unknown")
        self.birth_date = entry.data.get("birth_date")
        self.birth_time = entry.data.get("birth_time")

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Fetch data from the coordinator.

        Returns:
            Dictionary with current birthday data
        """
        return {
            "name": self.name,
            "birth_date": self.birth_date,
            "birth_time": self.birth_time,
        }

