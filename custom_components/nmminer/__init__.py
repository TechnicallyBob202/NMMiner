"""The NMMiner integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_PORT, DEFAULT_PORT, DOMAIN
from .coordinator import NMMinerDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NMMiner from a config entry."""
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    
    coordinator = NMMinerDataCoordinator(hass, port)
    
    try:
        await coordinator.async_start()
    except OSError as err:
        _LOGGER.error("Failed to start NMMiner listener: %s", err)
        return False
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: NMMinerDataCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_stop()
    
    return unload_ok
