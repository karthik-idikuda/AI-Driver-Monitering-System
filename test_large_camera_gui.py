#!/usr/bin/env python3
"""
Test script for large centered camera feed and white UI fixes
"""

import sys
import os
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def test_large_camera_gui():
    """Test the updated GUI with large centered camera feed"""
    try:
        logger.info("Starting GUI with large centered camera feed...")
        
        # Import and start the GUI
        from main_gui import DriverMonitoringGUI
        
        # Create GUI instance
        app = DriverMonitoringGUI()
        
        logger.info("✅ GUI started successfully")
        
        # Verify window size
        geometry = app.root.geometry()
        logger.info(f"Window geometry: {geometry}")
        
        # Verify white theme
        if app.colors['primary'] == '#ffffff':
            logger.info("✅ White theme applied correctly")
        else:
            logger.warning(f"❌ Theme issue - primary color: {app.colors['primary']}")
        
        # Verify canvas size
        logger.info(f"Canvas cached size: {app.cached_canvas_width}x{app.cached_canvas_height}")
        
        # Start the GUI main loop
        logger.info("Starting GUI main loop...")
        logger.info("Try clicking 'Start Monitoring' to test camera feed...")
        app.root.mainloop()
        
    except Exception as e:
        logger.error(f"❌ GUI test failed: {str(e)}")
        raise

def main():
    """Main test function"""
    logger.info("=" * 70)
    logger.info("TESTING LARGE CENTERED CAMERA FEED AND WHITE UI")
    logger.info("=" * 70)
    
    logger.info("\n🎨 Testing new layout with:")
    logger.info("  • Larger window (1600x1000)")
    logger.info("  • Centered camera feed (800x600)")
    logger.info("  • Three-panel layout")
    logger.info("  • White theme")
    logger.info("  • Proper spacing")
    
    test_large_camera_gui()
    
    logger.info("\n✅ Test completed!")

if __name__ == "__main__":
    main()
