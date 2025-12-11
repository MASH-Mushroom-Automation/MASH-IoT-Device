# Raspberry Pi 3 Bluetooth Troubleshooting Guide

This guide provides comprehensive troubleshooting steps for Bluetooth pairing issues on Raspberry Pi 3 devices.

## Common Issues

1. **Pairing Failures**: "Pairing Failed" messages on mobile devices
2. **Device Not Visible**: The Raspberry Pi is not visible to other devices
3. **Connection Drops**: Connections are established but drop immediately

## Root Causes

Raspberry Pi 3 Bluetooth issues are often caused by:

1. **UART Clock Speed**: The default UART clock can cause stability issues
2. **Device Class**: Incorrect device class can prevent proper pairing
3. **Firmware Loading**: Improper firmware loading sequence
4. **Configuration Conflicts**: Multiple services trying to control Bluetooth

## Solution Approach

We've created a specialized script for Raspberry Pi 3 Bluetooth pairing:

```bash
sudo python rpi3_bluetooth_pairing_fix.py
```

This script:
1. Completely resets the Bluetooth stack
2. Fixes Raspberry Pi 3 specific UART issues
3. Sets the optimal device class for pairing (0x000104 - Computer + Peripheral)
4. Creates a service to maintain pairing settings

## If Issues Persist

If pairing still fails after running the script:

1. **Reboot Required**: Some changes require a reboot to take effect:
   ```bash
   sudo reboot
   ```

2. **Check Mobile Device**: Try these steps on your mobile device:
   - Turn Bluetooth off and back on
   - Forget any previous pairing with this device
   - Ensure your app is using the correct Bluetooth profile (SPP or GATT)
   - Try pairing from the system Bluetooth settings first, then open your app

3. **Hardware Issues**: Consider these hardware factors:
   - Interference from other devices (try in a different location)
   - Power supply issues (ensure adequate power to the Raspberry Pi)
   - Try a USB Bluetooth adapter as an alternative

## Debugging Commands

Use these commands to diagnose Bluetooth issues:

```bash
# Check Bluetooth adapter status
sudo hciconfig -a

# Check Bluetooth service status
sudo systemctl status bluetooth

# View Bluetooth logs
sudo journalctl -u bluetooth

# Test Bluetooth scanning
sudo hcitool scan

# Check if adapter is blocked
sudo rfkill list
```

## Technical Details

### Device Classes

Different device classes can affect pairing compatibility:

- **0x000100**: Computer
- **0x000104**: Computer + Peripheral (keyboard/mouse)
- **0x000200**: Phone
- **0x000500**: Peripheral (keyboard/mouse)

### UART Clock Settings

The Raspberry Pi 3's UART clock can affect Bluetooth stability:

```
# Add to /boot/cmdline.txt
bcm2708.uart_clock=3000000
```

### Bluetooth Configuration

The optimal Bluetooth configuration for Raspberry Pi 3:

```
[General]
Name = MASH-IoT-Device
Class = 0x000104
DiscoverableTimeout = 0
PairableTimeout = 0

[Policy]
AutoEnable=true
```

## Mobile App Development Considerations

When developing mobile apps that connect to Raspberry Pi:

1. **Increase Timeouts**: Use longer timeouts for scanning and connection
2. **Implement Retries**: Add automatic retry logic for failed connections
3. **Handle Pairing Explicitly**: Some devices require explicit pairing handling
4. **Use Correct Profile**: Ensure you're using the appropriate Bluetooth profile
5. **Test on Multiple Devices**: Different phones handle Bluetooth differently
