{% if installed %}
## Thanks for installing NMMiner! 🎉

Your ESP32 Bitcoin miners will now automatically appear in Home Assistant.

### Next Steps:

1. **Add the Integration**:
   - Go to Settings → Integrations
   - Click "+ Add Integration"
   - Search for "NMMiner"
   - Configure the UDP port (default: 12345)

2. **Wait for Auto-Discovery**:
   - Your miners should appear within 10 seconds
   - Each miner becomes a device with multiple sensors

3. **Set Up Block Notifications**:
   ```yaml
   automation:
     - alias: "Bitcoin Block Found"
       trigger:
         - platform: event
           event_type: nmminer_block_found
       action:
         - service: notify.mobile_app_your_phone
           data:
             title: "🎉 Block Found!"
             message: >
               Miner {{ trigger.event.data.miner_ip }} found a block!
               Total: {{ trigger.event.data.valid_blocks }}
   ```

### Features:
- 🔄 Real-time updates via UDP broadcasts
- 🎉 Block hit event notifications
- 📊 Comprehensive sensors (hashrate, temp, shares, etc.)
- 🔍 Auto-discovery of miners
- 📱 Full device & entity registry support

### Troubleshooting:
- **Miners not appearing?** Check that UDP port 12345 isn't blocked by firewall
- **Sensors unavailable?** Wait 30 seconds for first broadcast
- **Need help?** Check the [full documentation](https://github.com/NMminer1024/NMMiner)

{% else %}

## NMMiner Integration for Home Assistant

Monitor your ESP32-based Bitcoin miners with this native Home Assistant integration.

### What You Get:

**📊 For Each Miner:**
- Hashrate monitoring
- Share statistics (accepted/rejected)
- Valid blocks found counter
- Best difficulty achieved
- Temperature monitoring
- WiFi signal strength
- Uptime tracking
- Firmware version

**🎉 Special Features:**
- **Block Hit Events** - Get instant notifications when any miner finds a block
- **Auto-Discovery** - Miners appear automatically when they start broadcasting
- **Real-Time Updates** - Push-based updates every 5 seconds (no polling!)
- **Full HA Integration** - Devices, entities, and native dashboards

### Requirements:

- Home Assistant 2024.1.0 or newer
- ESP32 miners running NMMiner firmware v0.3.01 or later
- Miners configured to broadcast on UDP (default port 12345)
- Network connectivity between HA and miners

### Quick Start:

1. Install this integration via HACS
2. Restart Home Assistant
3. Add via Settings → Integrations → "+ Add Integration" → "NMMiner"
4. Configure UDP port (default: 12345)
5. Your miners will auto-discover!

### Documentation:

- [NMMiner Firmware](https://github.com/NMminer1024/NMMiner)
- [Telegram Community](https://t.me/NMMiner)

{% endif %}
