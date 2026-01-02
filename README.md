# NMMiner Home Assistant Integration

A proper Home Assistant custom integration for monitoring ESP32-based Bitcoin miners (NMMiner firmware).

## Features

- 🎛️ **UI Configuration** - Set up via Home Assistant UI (no YAML needed!)
- 🔄 **Real-time Updates** - UDP push notifications every 5 seconds
- 🔍 **Auto-discovery** - Miners automatically appear as devices
- 🎉 **Block Hit Events** - Get notified when any miner finds a valid block
- 📊 **Comprehensive Sensors** - Hashrate, shares, temperature, WiFi signal, and more
- 🏗️ **Proper Architecture** - Uses DataUpdateCoordinator, config entries, and modern HA patterns

## Installation

### HACS (Recommended - when published)

1. Open HACS
2. Go to Integrations
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add this repository URL
6. Install "NMMiner"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/nmminer` folder to your Home Assistant's `config/custom_components/` directory
2. Restart Home Assistant
3. Go to Configuration → Integrations
4. Click "+ Add Integration"
5. Search for "NMMiner"

## Configuration

1. After adding the integration, you'll be prompted for:
   - **UDP Port**: The port your miners broadcast on (default: 12345)

2. Click Submit

3. Your miners will auto-discover within seconds!

## Sensors

For each discovered miner (e.g., `192.168.1.101`), you get:

- `sensor.nmminer_192_168_1_101_hashrate` - Current hashrate (H/s)
- `sensor.nmminer_192_168_1_101_shares` - Accepted/Total shares
- `sensor.nmminer_192_168_1_101_valid_blocks` - **Blocks found** ⭐
- `sensor.nmminer_192_168_1_101_best_difficulty` - Best share difficulty
- `sensor.nmminer_192_168_1_101_temperature` - Device temperature (°C)
- `sensor.nmminer_192_168_1_101_wifi_signal` - RSSI (dBm)
- `sensor.nmminer_192_168_1_101_uptime` - Miner uptime
- `sensor.nmminer_192_168_1_101_progress` - Current work progress (%)
- `sensor.nmminer_192_168_1_101_firmware_version` - Firmware version

### Extra Attributes

Some sensors include additional data in their attributes:

**Shares sensor:**
- `accepted` - Number of accepted shares
- `total` - Total shares submitted
- `rejection_rate` - Percentage of rejected shares

**Best Difficulty sensor:**
- `pool_diff` - Current pool difficulty
- `last_diff` - Last share difficulty
- `net_diff` - Network difficulty

**Firmware Version sensor:**
- `board_type` - Type of ESP32 board
- `free_heap` - Available memory

## Events

### nmminer_block_found

Fired whenever any miner's Valid block counter increases.

**Event Data:**
```python
{
    "miner_ip": "192.168.1.101",
    "valid_blocks": 1,
    "best_diff": "4.021M",
    "hashrate": "113.13K"
}
```

## Automations

### Block Found Notification

```yaml
automation:
  - alias: "🎉 NMMiner Block Found"
    trigger:
      - platform: event
        event_type: nmminer_block_found
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "💎 Bitcoin Block Found!"
          message: >
            Miner {{ trigger.event.data.miner_ip }} found a valid block!
            
            Valid Blocks: {{ trigger.event.data.valid_blocks }}
            Best Diff: {{ trigger.event.data.best_diff }}
            Hashrate: {{ trigger.event.data.hashrate }}
          data:
            priority: high
```

### Monitor Individual Miner

```yaml
automation:
  - alias: "Miner Block Counter"
    trigger:
      - platform: state
        entity_id: sensor.nmminer_192_168_1_101_valid_blocks
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "Miner 1 found a block! Total: {{ trigger.to_state.state }}"
```

### High Temperature Alert

```yaml
automation:
  - alias: "NMMiner Overheating"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nmminer_192_168_1_101_temperature
        above: 65
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Miner Overheating"
          message: "Miner is at {{ trigger.to_state.state }}°C!"
```

### Miner Offline Detection

```yaml
automation:
  - alias: "NMMiner Offline"
    trigger:
      - platform: state
        entity_id: 
          - sensor.nmminer_192_168_1_101_hashrate
          - sensor.nmminer_192_168_1_102_hashrate
        to: 'unavailable'
        for:
          minutes: 2
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Miner Offline"
          message: "{{ trigger.to_state.name }} stopped broadcasting"
```

## Template Sensors

### Total Blocks from All Miners

```yaml
template:
  - sensor:
      - name: "Total Blocks Found"
        unique_id: nmminer_total_blocks
        state: >
          {% set ns = namespace(total=0) %}
          {% for state in states.sensor 
             if 'nmminer' in state.entity_id 
             and 'valid_blocks' in state.entity_id 
             and state.state not in ['unknown', 'unavailable'] %}
            {% set ns.total = ns.total + (state.state | int(0)) %}
          {% endfor %}
          {{ ns.total }}
        icon: mdi:bitcoin
```

### Total Hashrate

```yaml
template:
  - sensor:
      - name: "Total Mining Hashrate"
        unique_id: nmminer_total_hashrate
        unit_of_measurement: "KH/s"
        state_class: measurement
        state: >
          {% set ns = namespace(total=0.0) %}
          {% for state in states.sensor 
             if 'nmminer' in state.entity_id 
             and 'hashrate' in state.entity_id 
             and state.state not in ['unknown', 'unavailable'] %}
            {% set ns.total = ns.total + (state.state | float(0)) %}
          {% endfor %}
          {{ (ns.total / 1000) | round(2) }}
        icon: mdi:chip
```

## Dashboard Example

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      # 💎 Bitcoin Mining Farm
      **Total Blocks:** {{ states('sensor.total_blocks_found') | int(0) }}
      **Total Hashrate:** {{ states('sensor.total_mining_hashrate') }} KH/s

  - type: entities
    title: "Miner Status"
    entities:
      - entity: sensor.nmminer_192_168_1_101_hashrate
        name: "Miner 1 Hashrate"
      - entity: sensor.nmminer_192_168_1_101_valid_blocks
        name: "Miner 1 Blocks"
      - entity: sensor.nmminer_192_168_1_101_temperature
        name: "Miner 1 Temperature"
      - entity: sensor.nmminer_192_168_1_102_hashrate
        name: "Miner 2 Hashrate"
      - entity: sensor.nmminer_192_168_1_102_valid_blocks
        name: "Miner 2 Blocks"
      - entity: sensor.nmminer_192_168_1_102_temperature
        name: "Miner 2 Temperature"

  - type: history-graph
    title: "Hashrate History"
    hours_to_show: 24
    entities:
      - sensor.nmminer_192_168_1_101_hashrate
      - sensor.nmminer_192_168_1_102_hashrate
```

## Troubleshooting

### Integration won't install
- Make sure you've restarted Home Assistant after copying files
- Check the logs for errors: Settings → System → Logs

### No miners appearing
1. **Verify UDP broadcasts are reaching HA:**
   ```bash
   sudo tcpdump -i any -n udp port 12345 -A
   ```
   
2. **Check firewall:**
   ```bash
   sudo ufw allow 12345/udp
   ```

3. **Verify miners are broadcasting:**
   - Access miner's web interface
   - Confirm firmware version supports broadcasts (v0.3.01+)

### Sensors show "unavailable"
- Wait 30 seconds for first broadcast
- Check Home Assistant logs for errors
- Ensure miners and HA are on same network/VLAN

### Reinstalling the integration
1. Settings → Integrations → NMMiner → Delete
2. Restart Home Assistant
3. Re-add the integration

## Technical Details

- **Architecture**: Modern HA integration using DataUpdateCoordinator
- **Protocol**: UDP broadcasts on configurable port (default 12345)
- **Update Method**: Push-based (miners broadcast every 5 seconds)
- **Data Format**: JSON payload
- **Device Discovery**: Automatic based on IP in broadcast

## Development

This integration follows Home Assistant's integration quality scale and best practices:

- ✅ Config flow for UI-based setup
- ✅ DataUpdateCoordinator for data management
- ✅ CoordinatorEntity for sensors
- ✅ Proper device registry entries
- ✅ Unique IDs for all entities
- ✅ Event-driven architecture
- ✅ Async/await throughout

## Support

- **NMMiner Firmware**: https://github.com/NMminer1024/NMMiner
- **Telegram**: https://t.me/NMMiner
- **Home Assistant Community**: https://community.home-assistant.io/

## License

MIT License
