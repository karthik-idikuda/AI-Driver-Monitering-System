#!/usr/bin/env python3
"""
Test script for stable camera feed with no shaking and proper sizing
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import time
import threading
import logging

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_stable_camera_feed():
    """Test the stable camera feed implementation"""
    try:
        # Import the GUI module
        from main_gui import DriverMonitoringGUI
        
        # Create root window
        root = tk.Tk()
        
        # Create GUI instance
        app = DriverMonitoringGUI(root)
        
        # Set up test message
        def show_test_info():
            test_msg = """
🔧 STABLE CAMERA FEED TEST

This test verifies the following fixes:
✅ Camera feed no longer shrinks excessively
✅ Detection animations don't shake
✅ Modern white theme with proper layout
✅ Stable frame processing and display
✅ Debounced canvas resizing
✅ Smooth, stable animations

Instructions:
1. Click 'Start Monitoring' to begin
2. Try resizing the window - camera feed should remain stable
3. Observe that animations are smooth and don't shake
4. The camera feed maintains a minimum size
5. UI remains responsive with stable performance

Expected Results:
- Camera feed stays large and centered
- No excessive shrinking below minimum size
- Animations are smooth without jitter
- Window resizing doesn't cause shaking
- Modern white theme with proper spacing
            """
            
            messagebox.showinfo("Test Information", test_msg)
        
        # Show test info after a short delay
        root.after(1000, show_test_info)
        
        # Start the main loop
        logger.info("Starting stable camera feed test")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Error in stable camera feed test: {str(e)}")
        messagebox.showerror("Test Error", f"Failed to run test: {str(e)}")

if __name__ == "__main__":
    test_stable_camera_feed()
