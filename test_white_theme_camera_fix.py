#!/usr/bin/env python3
"""
Test script for white theme UI and camera feed fixes
Tests the updated Driver Monitoring System GUI with white background and improved camera handling
"""

import sys
import os
import logging
import threading
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

def test_camera_availability():
    """Test if camera is available before starting GUI"""
    import cv2
    
    logger.info("Testing camera availability...")
    
    # Test different camera backends and IDs
    backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_V4L2, cv2.CAP_DSHOW, cv2.CAP_ANY]
    camera_ids = [0, 1, 2, -1]
    
    working_configs = []
    
    for camera_id in camera_ids:
        for backend in backends:
            try:
                cap = cv2.VideoCapture(camera_id, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        working_configs.append((camera_id, backend))
                        logger.info(f"✅ Camera {camera_id} with backend {backend} works - Frame shape: {frame.shape}")
                    else:
                        logger.warning(f"❌ Camera {camera_id} with backend {backend} opens but cannot read frames")
                cap.release()
            except Exception as e:
                logger.warning(f"❌ Camera {camera_id} with backend {backend} failed: {str(e)}")
    
    if working_configs:
        logger.info(f"Found {len(working_configs)} working camera configurations")
        return True
    else:
        logger.error("No working camera configurations found")
        return False

def test_gui_startup():
    """Test GUI startup with white theme"""
    try:
        logger.info("Starting GUI with white theme...")
        
        # Import and start the GUI
        from main_gui import DriverMonitoringGUI
        
        # Create GUI instance
        app = DriverMonitoringGUI()
        
        logger.info("✅ GUI started successfully with white theme")
        
        # Add a test to verify white theme colors
        if app.colors['primary'] == '#ffffff':
            logger.info("✅ White theme colors applied correctly")
        else:
            logger.warning(f"❌ Theme colors incorrect - primary: {app.colors['primary']}")
        
        # Start the GUI main loop
        logger.info("Starting GUI main loop...")
        app.root.mainloop()
        
    except Exception as e:
        logger.error(f"❌ GUI startup failed: {str(e)}")
        raise

def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("TESTING WHITE THEME UI AND CAMERA FEED FIXES")
    logger.info("=" * 60)
    
    # Test 1: Camera availability
    logger.info("\n🔍 TEST 1: Camera Availability")
    camera_available = test_camera_availability()
    
    if not camera_available:
        logger.warning("⚠️  No camera detected - GUI will start but camera feed may show error message")
    
    # Test 2: GUI startup
    logger.info("\n🎨 TEST 2: GUI Startup with White Theme")
    test_gui_startup()
    
    logger.info("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
