# Installation Guide

## Quick Install via HACS (Recommended)

### Prerequisites
- Home Assistant 2024.1.0 or newer
- HACS installed and configured

### Steps

1. **Open HACS**
   - Go to HACS in your Home Assistant sidebar

2. **Add Custom Repository** (if not in default HACS)
   - Click the three dots (⋮) in the top right
   - Select "Custom repositories"
   - Repository: `YOUR_GITHUB_USERNAME/nmminer-ha`
   - Category: Integration
   - Click "Add"

3. **Install Integration**
   - Click "+ Explore & Download Repositories"
   - Search for "NMMiner"
   - Click "NMMiner"
   - Click "Download"
   - Select the latest version
   - Click "Download"

4. **Restart Home Assistant**
   - Settings → System → Restart

5. **Add Integration**
   - Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "NMMiner"
   - Configure UDP port (default: 37778)
   - Click "Submit"

6. **Done!**
   - Your miners should appear within 10 seconds

---

## Manual Installation

### Prerequisites
- SSH access to your Home Assistant instance
- Home Assistant 2024.1.0 or newer

### Steps

1. **Download the Integration**
   ```bash
   cd /config
   wget https://github.com/YOUR_GITHUB_USERNAME/nmminer-ha/archive/refs/heads/main.zip
   unzip main.zip
   ```

2. **Copy Files**
   ```bash
   mkdir -p custom_components
   cp -r nmminer-ha-main/custom_components/nmminer custom_components/
   ```

3. **Set Permissions**
   ```bash
   chmod -R 755 custom_components/nmminer
   ```

4. **Verify Structure**
   ```bash
   ls -la custom_components/nmminer/
   ```
   
   You should see:
   ```
   __init__.py
   config_flow.py
   const.py
   coordinator.py
   manifest.json
   sensor.py
   strings.json
   translations/
   ```

5. **Restart Home Assistant**
   - Settings → System → Restart

6. **Add Integration**
   - Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "NMMiner"
   - Configure settings
   - Click "Submit"

---

## Docker Compose Installation

If running HA in Docker, add the integration via volume mount:

```yaml
version: '3'
services:
  homeassistant:
    container_name: homeassistant
    image: homeassistant/home-assistant:stable
    volumes:
      - ./config:/config
      - ./custom_components/nmminer:/config/custom_components/nmminer
    network_mode: host
    restart: unless-stopped
```

Then restart the container:
```bash
docker-compose restart homeassistant
```

---

## Home Assistant OS Installation

### Via SSH Add-on

1. **Enable SSH**
   - Install "Terminal & SSH" add-on from the Add-on Store
   - Start the add-on

2. **Connect via SSH**
   ```bash
   ssh root@homeassistant.local
   ```

3. **Navigate to Config**
   ```bash
   cd /config
   ```

4. **Download and Extract**
   ```bash
   wget https://github.com/YOUR_GITHUB_USERNAME/nmminer-ha/archive/refs/heads/main.zip
   unzip main.zip
   mkdir -p custom_components
   cp -r nmminer-ha-main/custom_components/nmminer custom_components/
   rm -rf main.zip nmminer-ha-main
   ```

5. **Restart HA**
   - Settings → System → Restart

6. **Add Integration**
   - Follow UI setup steps above

---

## Verification

### Check Installation

1. **Check Logs**
   - Settings → System → Logs
   - Look for: `NMMiner UDP listener started on port 37778`

2. **Verify Integration**
   - Settings → Devices & Services
   - You should see "NMMiner" integration

3. **Test Discovery**
   - Wait 10 seconds
   - Settings → Devices & Services → Devices
   - You should see your miners listed

### Troubleshooting

#### Integration not showing up
- Clear browser cache and refresh
- Check that files are in correct location
- Verify file permissions (should be readable by HA user)
- Check logs for errors

#### Miners not discovered
```bash
# On HA host, check if broadcasts are reaching HA
sudo tcpdump -i any -n udp port 37778 -A
```

You should see JSON data every 5 seconds.

#### Firewall blocking
```bash
# Allow UDP port
sudo ufw allow 37778/udp

# Or for firewalld
sudo firewall-cmd --add-port=37778/udp --permanent
sudo firewall-cmd --reload
```

---

## Updating

### Via HACS
1. Go to HACS → Integrations
2. Find "NMMiner"
3. Click "Update" if available
4. Restart Home Assistant

### Manual Update
1. Download new version
2. Replace files in `custom_components/nmminer/`
3. Restart Home Assistant
4. Check changelog for breaking changes

---

## Uninstalling

### Remove Integration
1. Settings → Devices & Services
2. Find "NMMiner"
3. Click the three dots (⋮)
4. Select "Delete"
5. Confirm deletion

### Remove Files
```bash
cd /config
rm -rf custom_components/nmminer
```

### Restart
- Settings → System → Restart

---

## Network Configuration

### Required Ports
- **UDP 37778** (default) - For miner broadcasts

### Firewall Rules

**UFW:**
```bash
sudo ufw allow 37778/udp comment 'NMMiner broadcasts'
```

**iptables:**
```bash
sudo iptables -A INPUT -p udp --dport 37778 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

**firewalld:**
```bash
sudo firewall-cmd --add-port=37778/udp --permanent
sudo firewall-cmd --reload
```

### VLANs

If your miners are on a different VLAN:
1. Ensure VLAN routing is configured
2. Allow UDP broadcasts between VLANs
3. Test with: `sudo tcpdump -i any -n udp port 37778`

---

## Getting Help

- Check [README.md](README.md) for full documentation
- Review [examples/automations.yaml](examples/automations.yaml) for automation ideas
- Open an issue on GitHub
- Join [NMMiner Telegram](https://t.me/NMMiner)
