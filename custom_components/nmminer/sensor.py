"""Sensor platform for NMMiner integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NMMinerDataCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class NMMinerSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass
class NMMinerSensorEntityDescription(
    SensorEntityDescription, NMMinerSensorEntityDescriptionMixin
):
    """Describes NMMiner sensor entity."""

    attr_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def parse_hashrate(hashrate_str: str) -> float:
    """Parse hashrate string to numeric H/s."""
    try:
        # Remove any extra text like "H/s", "KH/s", "MH/s"
        hashrate_str = hashrate_str.replace("H/s", "").replace("h/s", "").strip()
        
        if "M" in hashrate_str or "m" in hashrate_str:
            return float(hashrate_str.replace("M", "").replace("m", "").strip()) * 1000000
        if "K" in hashrate_str or "k" in hashrate_str:
            return float(hashrate_str.replace("K", "").replace("k", "").strip()) * 1000
        return float(hashrate_str)
    except (ValueError, AttributeError):
        return 0.0


def get_share_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Get share statistics as attributes."""
    try:
        share = data.get("Share", "0/0")
        # Handle format like "7/2123/99.7%" - split and take first two parts
        parts = share.split("/")
        if len(parts) >= 2:
            accepted_int = int(parts[0])
            total_int = int(parts[1])
            rejection_rate = (
                round((total_int - accepted_int) / total_int * 100, 2)
                if total_int > 0
                else 0
            )
            return {
                "accepted": accepted_int,
                "total": total_int,
                "rejection_rate": rejection_rate,
            }
    except (ValueError, AttributeError, IndexError):
        pass
    return {}


def get_difficulty_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Get difficulty statistics as attributes."""
    return {
        "pool_diff": data.get("PoolDiff", "0").strip(),
        "last_diff": data.get("LastDiff", "0").strip(),
        "net_diff": data.get("NetDiff", "0").strip(),
    }


def get_version_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Get version and board info as attributes."""
    return {
        "board_type": data.get("BoardType", "Unknown"),
        "free_heap": data.get("FreeHeap", 0),
    }


SENSOR_TYPES: tuple[NMMinerSensorEntityDescription, ...] = (
    NMMinerSensorEntityDescription(
        key="hashrate",
        name="Hashrate",
        native_unit_of_measurement="H/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chip",
        value_fn=lambda data: parse_hashrate(data.get("HashRate", "0")),
    ),
    NMMinerSensorEntityDescription(
        key="shares",
        name="Shares",
        icon="mdi:chart-line",
        value_fn=lambda data: data.get("Share", "0/0"),
        attr_fn=get_share_attributes,
    ),
    NMMinerSensorEntityDescription(
        key="valid_blocks",
        name="Valid Blocks",
        icon="mdi:bitcoin",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("Valid", 0),
    ),
    NMMinerSensorEntityDescription(
        key="best_diff",
        name="Best Difficulty",
        icon="mdi:trophy",
        value_fn=lambda data: data.get("BestDiff", "0").strip(),
        attr_fn=get_difficulty_attributes,
    ),
    NMMinerSensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("Temp", 0),
    ),
    NMMinerSensorEntityDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("Uptime", "000d 00:00:00").split("\r")[0] if data.get("Uptime") else "000d 00:00:00",
    ),
    NMMinerSensorEntityDescription(
        key="rssi",
        name="WiFi Signal",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("RSSI", -100),
    ),
    NMMinerSensorEntityDescription(
        key="progress",
        name="Progress",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:progress-clock",
        value_fn=lambda data: round(data.get("Progress", 0) * 100, 2) if data.get("Progress") else 0,
    ),
    NMMinerSensorEntityDescription(
        key="pool",
        name="Pool",
        icon="mdi:server-network",
        value_fn=lambda data: data.get("PoolInUse", "Unknown"),
    ),
    NMMinerSensorEntityDescription(
        key="version",
        name="Firmware Version",
        icon="mdi:information-outline",
        value_fn=lambda data: data.get("Version", "Unknown"),
        attr_fn=get_version_attributes,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NMMiner sensor based on a config entry."""
    coordinator: NMMinerDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Track which miners we've created entities for
    created_miners: set[str] = set()

    @callback
    def async_add_miner_sensors() -> None:
        """Add sensors for newly discovered miners."""
        new_entities: list[NMMinerSensor] = []
        
        # Handle None data during initialization
        if not coordinator.data:
            return
        
        for miner_ip in coordinator.data:
            if miner_ip not in created_miners:
                _LOGGER.info("Creating sensors for miner %s", miner_ip)
                created_miners.add(miner_ip)
                
                for description in SENSOR_TYPES:
                    new_entities.append(
                        NMMinerSensor(coordinator, miner_ip, description)
                    )
        
        if new_entities:
            async_add_entities(new_entities)

    # Listen for new miners
    coordinator.async_add_listener(async_add_miner_sensors)
    
    # Add any miners already discovered
    async_add_miner_sensors()


class NMMinerSensor(CoordinatorEntity[NMMinerDataCoordinator], SensorEntity):
    """Representation of a NMMiner sensor."""

    entity_description: NMMinerSensorEntityDescription

    def __init__(
        self,
        coordinator: NMMinerDataCoordinator,
        miner_ip: str,
        description: NMMinerSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._miner_ip = miner_ip
        
        # Entity ID - replace dots with underscores
        safe_ip = miner_ip.replace(".", "_")
        self._attr_unique_id = f"{safe_ip}_{description.key}"
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, miner_ip)},
            "name": f"NMMiner {miner_ip}",
            "manufacturer": "NMTech",
            "model": "NMMiner",
        }
        
        # Entity name
        self._attr_name = f"NMMiner {miner_ip} {description.name}"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._miner_ip in self.coordinator.data

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self._miner_ip not in self.coordinator.data:
            return None
        
        data = self.coordinator.data[self._miner_ip]
        return self.entity_description.value_fn(data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self._miner_ip not in self.coordinator.data:
            return None
        
        if self.entity_description.attr_fn is None:
            return None
        
        data = self.coordinator.data[self._miner_ip]
        return self.entity_description.attr_fn(data)