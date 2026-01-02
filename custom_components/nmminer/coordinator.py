"""Data coordinator for NMMiner integration."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, EVENT_BLOCK_FOUND, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class NMMinerDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NMMiner data from UDP broadcasts."""

    def __init__(self, hass: HomeAssistant, port: int) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.port = port
        self.miners: dict[str, dict[str, Any]] = {}
        self.transport: asyncio.DatagramTransport | None = None
        self.protocol: NMMinerProtocol | None = None

    async def async_start(self) -> None:
        """Start listening for UDP broadcasts."""
        loop = asyncio.get_event_loop()
        
        try:
            self.transport, self.protocol = await loop.create_datagram_endpoint(
                lambda: NMMinerProtocol(self),
                local_addr=("0.0.0.0", self.port),
            )
            _LOGGER.info("NMMiner UDP listener started on port %s", self.port)
        except OSError as err:
            _LOGGER.error("Failed to start UDP listener on port %s: %s", self.port, err)
            raise

    async def async_stop(self) -> None:
        """Stop the UDP listener."""
        if self.transport:
            self.transport.close()
            _LOGGER.info("NMMiner UDP listener stopped")

    @callback
    def async_process_miner_data(self, miner_ip: str, data: dict[str, Any]) -> None:
        """Process incoming miner data."""
        # Check for block hit
        if miner_ip in self.miners:
            old_valid = self.miners[miner_ip].get("Valid", 0)
            new_valid = data.get("Valid", 0)
            
            if new_valid > old_valid:
                _LOGGER.info("Block found on miner %s! Valid blocks: %s", miner_ip, new_valid)
                
                # Fire event
                self.hass.bus.async_fire(
                    EVENT_BLOCK_FOUND,
                    {
                        "miner_ip": miner_ip,
                        "valid_blocks": new_valid,
                        "best_diff": data.get("BestDiff"),
                        "hashrate": data.get("HashRate"),
                    },
                )
        
        # Update stored data
        self.miners[miner_ip] = data
        
        # Trigger update for all sensors
        self.async_set_updated_data(self.miners)

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data - not used since we rely on UDP push."""
        return self.miners


class NMMinerProtocol(asyncio.DatagramProtocol):
    """UDP protocol handler for NMMiner broadcasts."""

    def __init__(self, coordinator: NMMinerDataCoordinator) -> None:
        """Initialize."""
        self.coordinator = coordinator

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle received datagram."""
        try:
            payload = json.loads(data.decode("utf-8"))
            # Use IP from payload, or fall back to source address
            miner_ip = payload.get("IP") or addr[0]
            
            if not miner_ip:
                _LOGGER.debug("Received broadcast without IP from %s", addr)
                return
            
            # Process in the event loop
            self.coordinator.hass.loop.call_soon_threadsafe(
                self.coordinator.async_process_miner_data, miner_ip, payload
            )
            
        except json.JSONDecodeError:
            _LOGGER.debug("Failed to decode JSON from %s", addr)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Error processing datagram: %s", err)
