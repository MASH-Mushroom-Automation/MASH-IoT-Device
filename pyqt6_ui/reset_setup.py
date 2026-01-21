#!/usr/bin/env python3
"""
Reset Setup - Remove setup completion marker to test setup flow again
"""
import os
from pathlib import Path

setup_file = Path(__file__).parent / ".setup_complete"

if setup_file.exists():
    setup_file.unlink()
    print("✓ Setup marker removed. Run main.py to see setup flow again.")
else:
    print("ℹ Setup marker doesn't exist. Setup flow will show on next run.")
