# NMMiner HA Integration - Project Structure

```
nmminer_ha_proper/
├── .github/
│   └── workflows/
│       └── validate.yml              # GitHub Actions CI/CD workflow
├── .gitignore                         # Git ignore rules
├── CONTRIBUTING.md                    # Contribution guidelines
├── INSTALLATION.md                    # Detailed installation guide
├── LICENSE                            # MIT License
├── README.md                          # Main documentation
├── hacs.json                          # HACS integration metadata
├── info.md                            # HACS info panel content
├── custom_components/
│   └── nmminer/                      # Main integration code
│       ├── __init__.py               # Entry point, coordinator setup
│       ├── config_flow.py            # UI configuration flow
│       ├── const.py                  # Constants and configuration
│       ├── coordinator.py            # Data coordinator & UDP listener
│       ├── manifest.json             # Integration manifest
│       ├── sensor.py                 # Sensor entities
│       ├── strings.json              # UI text strings
│       └── translations/
│           └── en.json               # English translations
└── examples/
    └── automations.yaml              # Example automations
```

## File Descriptions

### Root Level

- **`.github/workflows/validate.yml`**: GitHub Actions workflow for automated testing
  - Validates HACS compatibility
  - Runs Home Assistant's hassfest validation
  - Lints code with ruff

- **`hacs.json`**: HACS metadata
  - Defines integration name, domain, and requirements
  - Specifies Home Assistant minimum version

- **`info.md`**: HACS info panel
  - Displayed in HACS UI before/after installation
  - Contains quick start guide and features

- **`README.md`**: Main documentation
  - Features overview
  - Installation instructions
  - Configuration examples
  - Troubleshooting guide

- **`INSTALLATION.md`**: Detailed installation guide
  - HACS installation
  - Manual installation
  - Docker setup
  - Network configuration

- **`CONTRIBUTING.md`**: Contribution guidelines
  - Development setup
  - Testing procedures
  - Code style requirements
  - PR guidelines

### Integration Code (`custom_components/nmminer/`)

- **`__init__.py`**: Entry point
  - `async_setup_entry()`: Creates coordinator, starts platforms
  - `async_unload_entry()`: Cleanup on removal

- **`config_flow.py`**: UI configuration
  - Port selection dialog
  - Input validation
  - Unique ID management

- **`const.py`**: Constants
  - Domain name
  - Default values
  - Event names
  - Platform list

- **`coordinator.py`**: Core logic
  - `NMMinerDataCoordinator`: Manages data updates
  - `NMMinerProtocol`: Handles UDP datagrams
  - Fires block hit events
  - Updates all sensors

- **`manifest.json`**: Integration metadata
  - Domain, name, version
  - Dependencies and requirements
  - Integration type and IoT class

- **`sensor.py`**: Sensor entities
  - `NMMinerSensor`: Base sensor class using CoordinatorEntity
  - Sensor descriptions with value extractors
  - Auto-discovery of new miners

- **`strings.json` & `translations/en.json`**: UI text
  - Config flow dialog text
  - Error messages
  - Help text

### Examples

- **`examples/automations.yaml`**: Ready-to-use automations
  - Block notifications (mobile, Discord, Telegram)
  - Temperature monitoring
  - Offline detection
  - Daily reports
  - Smart cooling
  - Integration examples

## Architecture

### Data Flow

```
Miner (ESP32)
    |
    | UDP Broadcast (every 5s)
    | Port 37778
    v
NMMinerProtocol.datagram_received()
    |
    | Parse JSON
    v
NMMinerDataCoordinator.async_process_miner_data()
    |
    ├─> Check for block hits
    │   └─> Fire "nmminer_block_found" event
    |
    └─> Update coordinator.data
        |
        v
    Coordinator notifies listeners
        |
        v
    NMMinerSensor entities update
        |
        v
    Home Assistant state machine
```

### Component Relationships

```
ConfigFlow
    |
    | Creates
    v
DataUpdateCoordinator ──┬──> Starts UDP Listener (NMMinerProtocol)
    |                   |
    | Manages           └──> Stores miner data
    v
NMMinerSensor (CoordinatorEntity)
    |
    | Auto-discovers from coordinator data
    |
    └──> Provides state to Home Assistant
```

## Key Design Decisions

1. **UDP Push vs Polling**: Uses UDP broadcasts for real-time updates without network overhead

2. **DataUpdateCoordinator**: Centralizes data management, enables efficient sensor updates

3. **CoordinatorEntity**: Sensors automatically update when coordinator data changes

4. **Config Flow**: UI-based setup for better user experience

5. **Auto-discovery**: Miners automatically create sensors when first seen

6. **Event-driven**: Block hits fire events for flexible automation

7. **Device Registry**: Each miner is a device with multiple sensors

## Testing Checklist

- [ ] Install via HACS
- [ ] Install manually
- [ ] Add integration via UI
- [ ] Verify miners auto-discover
- [ ] Check all sensors update
- [ ] Test block hit event
- [ ] Verify automations work
- [ ] Test uninstall/reinstall
- [ ] Check logs for errors
- [ ] Validate with hassfest
- [ ] HACS validation passes
- [ ] Code passes ruff linting

## Deployment

### To HACS Default Repository

1. Fork this repository
2. Submit PR to HACS-default
3. Wait for review and approval

### As Custom Repository

1. Push to your GitHub
2. Users add as custom repository in HACS
3. Distribute URL: `https://github.com/YOUR_USERNAME/nmminer-ha`

## Maintenance

### Version Updates

1. Update version in `manifest.json`
2. Update changelog in README
3. Tag release: `git tag v1.1.0`
4. Push tags: `git push --tags`

### Breaking Changes

- Update `README.md` with migration guide
- Bump version major number
- Add `config_flow.async_migrate_entry()` if needed

## Resources

- [HA Integration Docs](https://developers.home-assistant.io/docs/creating_integration_manifest)
- [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [HACS Guide](https://hacs.xyz/docs/publish/start)
