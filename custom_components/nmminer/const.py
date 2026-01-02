"""Constants for the NMMiner integration."""
from typing import Final

DOMAIN: Final = "nmminer"
DEFAULT_PORT: Final = 37778

# Config flow
CONF_PORT: Final = "port"

# Update coordinator
UPDATE_INTERVAL: Final = 30  # Consider miner stale after 30 seconds

# Events
EVENT_BLOCK_FOUND: Final = "nmminer_block_found"

# Platforms
PLATFORMS: Final = ["sensor"]
