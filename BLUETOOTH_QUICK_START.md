# Bluetooth Agent - Quick Start Guide

## TL;DR - The Fix

**Problem:** `subprocess.Popen` with `bluetoothctl` exits immediately, losing the agent registration.

**Solution:** Persistent D-Bus agent that stays running for the server lifetime.

## Quick Installation

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3-dbus python3-gi -y

# 2. Clear old pairings
bluetoothctl
remove <MAC_OF_YOUR_PHONE>
exit

# 3. Test the agent
python3 test_bluetooth_agent.py
# Keep running, try pairing from phone - should work instantly!

# 4. Run full server
python3 integrated_server.py
```

## Quick Test

```bash
# Terminal 1: Start agent test
python3 test_bluetooth_agent.py

# Terminal 2: Monitor Bluetooth (optional)
watch -n 1 'bluetoothctl devices; echo "---"; bluetoothctl paired-devices'

# Phone: Try to pair with "MASH-IoT-Device"
# Should connect instantly without any confirmation!
```

## Expected Log Output

### ✅ Success Looks Like:

```
Starting persistent Bluetooth agent for 'Just Works' pairing...
Bluetooth Agent initialized at /org/bluez/AutoPairingAgent
Registering Bluetooth agent with capability: NoInputNoOutput
✅ Bluetooth agent registered as default with 'NoInputNoOutput' capability
✅ Bluetooth adapter configured: Powered, Discoverable, Pairable as 'MASH-IoT-Device'
Starting Bluetooth agent main loop (running persistently)...
✅ Persistent Bluetooth agent started successfully
Device is now discoverable and pairable with automatic pairing
Agent will remain active for the lifetime of this server

# When someone pairs:
RequestConfirmation: device=/org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX, passkey=123456
Auto-confirming pairing (Just Works mode)
AuthorizeService called for device /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX, UUID 0000110e-...
Auto-approving service authorization
```

### ❌ Failure Looks Like:

```
❌ Failed to start Bluetooth agent
Error in Bluetooth agent: org.freedesktop.DBus.Error...
```

**Fix:** Install dependencies:
```bash
sudo apt install python3-dbus python3-gi
```

## Quick Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| Agent won't start | `sudo apt install python3-dbus python3-gi` |
| Bluetooth service down | `sudo systemctl restart bluetooth` |
| Not discoverable | `sudo hciconfig hci0 piscan` |
| Old pairing cached | `bluetoothctl remove <MAC>` |
| Permission denied | Add user to `bluetooth` group: `sudo usermod -a -G bluetooth $USER` |

## Key Files

- **`src/utils/bluetooth_agent.py`** - The persistent D-Bus agent (main fix)
- **`test_bluetooth_agent.py`** - Standalone test script
- **`integrated_server.py`** - Updated to use persistent agent (lines 1166-1180)
- **`BLUETOOTH_AGENT_FIX.md`** - Full technical documentation

## One-Liner Status Check

```bash
# Check if agent is running
ps aux | grep bluetooth_agent

# Check if device is discoverable
hciconfig hci0 | grep -i "discoverable\|pairable"

# Check BlueZ agent status
dbus-send --system --print-reply --dest=org.bluez /org/bluez org.freedesktop.DBus.Introspectable.Introspect | grep -i agent
```

## What Changed in Code

### Before (Lines 1169-1198) - ❌ WRONG
```python
process = subprocess.Popen(['bluetoothctl'], ...)
stdout, stderr = process.communicate(input="\n".join(commands))
# Agent exits here! ❌
```

### After (Lines 1166-1180) - ✅ CORRECT
```python
if start_bluetooth_agent(bluetooth_device_name):
    logger.info("✅ Persistent Bluetooth agent started successfully")
    # Agent stays running! ✅
```

## Verification Steps

1. ✅ Run `test_bluetooth_agent.py` - should start without errors
2. ✅ See device in Bluetooth scan on phone
3. ✅ Tap device - should pair instantly (no PIN)
4. ✅ Check log - should see "Auto-confirming pairing"
5. ✅ Connection stays active

## Why This Works

```
Manual bluetoothctl:
  You type commands → bluetoothctl stays open → agent persists ✅

Subprocess approach:
  Script sends commands → process.communicate() → process exits → agent lost ❌

D-Bus agent:
  Python agent registers → runs in thread → stays active → agent persists ✅
```

## Next Steps

1. **Test standalone:** `python3 test_bluetooth_agent.py`
2. **Verify pairing works**
3. **Run full server:** `python3 integrated_server.py`
4. **Monitor logs for agent messages**
5. **Deploy with confidence! 🚀**

## Support

If issues persist after following this guide, check:
- `BLUETOOTH_AGENT_FIX.md` - Full technical documentation
- `BLUETOOTH_TROUBLESHOOTING.md` - Comprehensive troubleshooting guide
- System logs: `journalctl -u bluetooth -f`
- BlueZ version: `bluetoothd --version` (needs 5.43+)

---

**Ready to deploy!** The persistent D-Bus agent solves the "Pairing Failed" issue definitively. 🎉
