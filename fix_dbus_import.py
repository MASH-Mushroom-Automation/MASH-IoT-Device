#!/usr/bin/env python3
"""
Fix D-Bus import issue by finding and adding system packages to Python path
"""

import sys
import os
import glob

def find_dbus_package():
    """Find where python3-dbus is installed"""
    possible_paths = [
        '/usr/lib/python3/dist-packages',
        '/usr/local/lib/python3/dist-packages',
        '/usr/lib/python3.*/dist-packages',
    ]
    
    for pattern in possible_paths:
        for path in glob.glob(pattern):
            dbus_path = os.path.join(path, 'dbus')
            if os.path.exists(dbus_path):
                return path
    return None

def fix_imports():
    """Add system packages to Python path"""
    dbus_location = find_dbus_package()
    
    if dbus_location:
        print(f"Found dbus at: {dbus_location}")
        if dbus_location not in sys.path:
            sys.path.insert(0, dbus_location)
            print(f"Added to sys.path: {dbus_location}")
        
        # Try importing
        try:
            import dbus
            import gi
            print("✅ Successfully imported dbus and gi")
            print(f"   dbus location: {dbus.__file__}")
            print(f"   gi location: {gi.__file__}")
            return True
        except ImportError as e:
            print(f"❌ Still can't import: {e}")
            return False
    else:
        print("❌ Could not find dbus package")
        print("\nSearched in:")
        for pattern in ['/usr/lib/python3/dist-packages', '/usr/local/lib/python3/dist-packages']:
            print(f"  - {pattern}")
        return False

if __name__ == '__main__':
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)
    print("\nCurrent sys.path:")
    for p in sys.path:
        print(f"  - {p}")
    print("\n" + "="*60)
    print("Attempting to fix imports...")
    print("="*60 + "\n")
    
    if fix_imports():
        print("\n✅ Fix successful! You can now import dbus and gi")
    else:
        print("\n❌ Fix failed. Manual intervention needed.")
        print("\nTry running:")
        print("  dpkg -L python3-dbus | grep dbus/__init__.py")
        print("  dpkg -L python3-gi | grep gi/__init__.py")
