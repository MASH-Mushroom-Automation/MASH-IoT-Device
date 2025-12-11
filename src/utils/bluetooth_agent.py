"""
Persistent Bluetooth Agent for "Just Works" Pairing
Implements a D-Bus agent that enables automatic pairing without user confirmation
"""

import sys
import os

# Fix for venv: Add system site-packages to path for dbus and gi
# These packages can't be pip installed, they must use system packages
if 'dbus' not in sys.modules:
    system_paths = [
        '/usr/lib/python3/dist-packages',
        '/usr/lib/python3.11/dist-packages',
        '/usr/lib/python3.10/dist-packages',
        '/usr/lib/python3.9/dist-packages',
    ]
    for path in system_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import logging
import threading

logger = logging.getLogger(__name__)

# Agent capability constants
AGENT_PATH = "/org/bluez/AutoPairingAgent"
AGENT_INTERFACE = "org.bluez.Agent1"
AGENT_CAPABILITY = "NoInputNoOutput"  # This enables "Just Works" pairing

class BluetoothAgent(dbus.service.Object):
    """
    D-Bus Agent for automatic Bluetooth pairing
    
    This agent implements the "NoInputNoOutput" capability which enables
    "Just Works" pairing - no PIN, no confirmation, automatic pairing
    like a Bluetooth speaker.
    """
    
    def __init__(self, bus, path):
        """Initialize the agent"""
        super().__init__(bus, path)
        self.bus = bus
        self.path = path
        logger.info(f"Bluetooth Agent initialized at {path}")
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        """Called when agent is unregistered"""
        logger.info("Bluetooth Agent released")
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        """Authorize service connection - auto-approve"""
        logger.info(f"AuthorizeService called for device {device}, UUID {uuid}")
        logger.info("Auto-approving service authorization")
        return
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        """
        Request PIN code - should never be called for NoInputNoOutput
        But we'll return a default PIN just in case
        """
        logger.warning(f"RequestPinCode called for {device} (unexpected for NoInputNoOutput)")
        return "0000"
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        """
        Request passkey - should never be called for NoInputNoOutput
        But we'll return a default passkey just in case
        """
        logger.warning(f"RequestPasskey called for {device} (unexpected for NoInputNoOutput)")
        return dbus.UInt32(0)
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        """Display passkey - just log it, no action needed"""
        logger.info(f"DisplayPasskey: device={device}, passkey={passkey}, entered={entered}")
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        """Display PIN code - just log it, no action needed"""
        logger.info(f"DisplayPinCode: device={device}, pincode={pincode}")
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        """
        Request confirmation - for NoInputNoOutput, this should auto-confirm
        This is the KEY method for "Just Works" pairing
        """
        logger.info("="*60)
        logger.info("BLUETOOTH PAIRING REQUEST")
        logger.info(f"Device: {device}")
        logger.info(f"Passkey: {passkey}")
        logger.info("Mode: Just Works (NoInputNoOutput)")
        logger.info("Action: Auto-confirming pairing")
        logger.info("="*60)
        # Simply returning (not raising an exception) means "confirmed"
        return
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        """Request authorization - auto-approve"""
        logger.info("="*60)
        logger.info("🔵 BLUETOOTH AUTHORIZATION REQUEST")
        logger.info(f"Device: {device}")
        logger.info("Action: Auto-approving authorization")
        logger.info("="*60)
        return
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        """Cancel any pending request"""
        logger.warning("="*60)
        logger.warning("⚠️  BLUETOOTH PAIRING CANCELLED")
        logger.warning("="*60)


class BluetoothAgentManager:
    """
    Manages the Bluetooth Agent and D-Bus main loop
    Runs in a separate thread to avoid blocking the main application
    """
    
    def __init__(self, device_name="MASH-IoT-Device"):
        """Initialize the agent manager"""
        self.device_name = device_name
        self.agent = None
        self.mainloop = None
        self.thread = None
        self.registered = False
        
        # Initialize D-Bus main loop
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        
        logger.info("Bluetooth Agent Manager initialized")
    
    def start(self):
        """
        Start the Bluetooth agent in a separate thread
        This must run continuously to keep the agent registered
        """
        if self.thread and self.thread.is_alive():
            logger.warning("Bluetooth agent already running")
            return True
        
        try:
            # Start agent in separate thread
            self.thread = threading.Thread(target=self._run_agent, daemon=True)
            self.thread.start()
            
            # Wait a bit for agent to initialize
            import time
            time.sleep(1)
            
            logger.info("Bluetooth agent started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Bluetooth agent: {e}")
            return False
    
    def _run_agent(self):
        """
        Run the agent (called in separate thread)
        This is the persistent agent that stays running
        """
        try:
            # Get system bus
            bus = dbus.SystemBus()
            
            # Create agent
            self.agent = BluetoothAgent(bus, AGENT_PATH)
            
            # Get agent manager
            obj = bus.get_object('org.bluez', '/org/bluez')
            manager = dbus.Interface(obj, 'org.bluez.AgentManager1')
            
            # Register agent with NoInputNoOutput capability
            logger.info(f"Registering Bluetooth agent with capability: {AGENT_CAPABILITY}")
            manager.RegisterAgent(AGENT_PATH, AGENT_CAPABILITY)
            
            # Request to be default agent
            logger.info("Requesting default agent status...")
            manager.RequestDefaultAgent(AGENT_PATH)
            
            self.registered = True
            logger.info("Bluetooth agent registered as default with 'NoInputNoOutput' capability")
            
            # Make device discoverable and pairable
            self._setup_adapter(bus)
            
            # Run GLib main loop (this blocks until stopped)
            self.mainloop = GLib.MainLoop()
            logger.info("Starting Bluetooth agent main loop (running persistently)...")
            self.mainloop.run()
            
        except KeyboardInterrupt:
            logger.info("Bluetooth agent interrupted by user")
        except Exception as e:
            logger.error(f"Error in Bluetooth agent: {e}")
            import traceback
            traceback.print_exc()
    
    def _setup_adapter(self, bus):
        """Configure the Bluetooth adapter for discoverable and pairable"""
        try:
            # Get adapter
            adapter_obj = bus.get_object('org.bluez', '/org/bluez/hci0')
            adapter_props = dbus.Interface(adapter_obj, 'org.freedesktop.DBus.Properties')
            
            # Set properties
            adapter_props.Set('org.bluez.Adapter1', 'Powered', dbus.Boolean(True))
            adapter_props.Set('org.bluez.Adapter1', 'Discoverable', dbus.Boolean(True))
            adapter_props.Set('org.bluez.Adapter1', 'Pairable', dbus.Boolean(True))
            adapter_props.Set('org.bluez.Adapter1', 'DiscoverableTimeout', dbus.UInt32(0))  # 0 = always
            adapter_props.Set('org.bluez.Adapter1', 'PairableTimeout', dbus.UInt32(0))      # 0 = always
            adapter_props.Set('org.bluez.Adapter1', 'Alias', dbus.String(self.device_name))
            
            logger.info(f"Bluetooth adapter configured: Powered, Discoverable, Pairable as '{self.device_name}'")
            
        except Exception as e:
            logger.error(f"Warning: Could not configure adapter properties: {e}")
    
    def stop(self):
        """Stop the Bluetooth agent"""
        try:
            if self.mainloop and self.mainloop.is_running():
                logger.info("Stopping Bluetooth agent...")
                self.mainloop.quit()
            
            # Unregister agent
            if self.registered:
                try:
                    bus = dbus.SystemBus()
                    obj = bus.get_object('org.bluez', '/org/bluez')
                    manager = dbus.Interface(obj, 'org.bluez.AgentManager1')
                    manager.UnregisterAgent(AGENT_PATH)
                    logger.info("Bluetooth agent unregistered")
                except Exception as e:
                    logger.error(f"Error unregistering agent: {e}")
            
            self.registered = False
            
        except Exception as e:
            logger.error(f"Error stopping Bluetooth agent: {e}")
    
    def is_running(self):
        """Check if agent is running"""
        return self.thread and self.thread.is_alive() and self.registered


# Module-level singleton for easy access
_agent_manager = None

def get_agent_manager(device_name="MASH-IoT-Device"):
    """Get or create the global agent manager singleton"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = BluetoothAgentManager(device_name)
    return _agent_manager


def start_bluetooth_agent(device_name="MASH-IoT-Device"):
    """
    Convenience function to start the Bluetooth agent
    
    Args:
        device_name: Bluetooth device name
        
    Returns:
        True if started successfully
    """
    manager = get_agent_manager(device_name)
    return manager.start()


def stop_bluetooth_agent():
    """Convenience function to stop the Bluetooth agent"""
    global _agent_manager
    if _agent_manager:
        _agent_manager.stop()
