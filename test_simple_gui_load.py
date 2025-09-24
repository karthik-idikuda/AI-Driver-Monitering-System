#!/usr/bin/env python3
"""
Simple test to check if GUI loads properly
"""

import sys
import os
import tkinter as tk
import time

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

def test_gui_load():
    """Test basic GUI loading"""
    try:
        print("Testing GUI load...")
        
        # Import the GUI module
        from main_gui import DriverMonitoringGUI
        
        # Create GUI instance (it creates its own root)
        print("Creating GUI instance...")
        app = DriverMonitoringGUI()
        
        print("GUI created successfully! The application should now be visible.")
        print("Test completed - you can close the window when done testing.")
        
        # Run for a short time then close automatically for testing
        def auto_close():
            print("Auto-closing test window...")
            app.root.destroy()
        
        # Auto close after 30 seconds for testing
        app.root.after(30000, auto_close)
        
        # Start the main loop
        app.run()
        
        print("GUI test completed successfully!")
        
    except Exception as e:
        print(f"Error in GUI test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_load()
