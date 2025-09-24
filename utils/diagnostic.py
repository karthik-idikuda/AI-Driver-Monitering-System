#!/usr/bin/env python3
"""
Diagnostic tool for the Driver Monitoring System
Tests camera functionality and detection modules
"""

import cv2
import time
import sys
import os
import logging
from pathlib import Path

# Add project directories to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "utils"))

from main_detector import DriverMonitoringSystem
from config_manager import ConfigManager

def setup_logging():
    """Setup diagnostic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("diagnostic")

def test_camera():
    """Test camera access and frame capture"""
    logger = logging.getLogger("diagnostic.camera")
    logger.info("Testing camera...")
    
    # Try to open the default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("❌ Failed to open camera")
        return False
    
    logger.info("✅ Camera opened successfully")
    
    # Try to read a frame
    ret, frame = cap.read()
    if not ret or frame is None:
        logger.error("❌ Failed to read frame from camera")
        cap.release()
        return False
    
    logger.info(f"✅ Frame read successfully (shape: {frame.shape})")
    
    # Display camera properties
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    logger.info(f"Camera properties: {width}x{height} @ {fps} FPS")
    
    # Clean up
    cap.release()
    return True

def test_detection_modules():
    """Test all detection modules with a sample frame"""
    logger = logging.getLogger("diagnostic.detectors")
    logger.info("Testing detection modules...")
    
    # Create monitoring system
    system = DriverMonitoringSystem()
    
    # Initialize modules
    logger.info("Initializing detection modules...")
    system.init_detectors()
    
    detector_count = len(system.detectors)
    if detector_count == 0:
        logger.error("❌ No detection modules initialized")
        return False
    
    logger.info(f"✅ {detector_count} detection modules initialized")
    
    # List available modules
    logger.info("Available detection modules:")
    for name in system.detectors.keys():
        logger.info(f" - {name}")
    
    return True

def test_monitoring_system():
    """Test full monitoring system operation"""
    logger = logging.getLogger("diagnostic.system")
    logger.info("Testing monitoring system...")
    
    # Create and start monitoring system
    system = DriverMonitoringSystem()
    
    if not system.start():
        logger.error("❌ Failed to start monitoring system")
        return False
    
    logger.info("✅ Monitoring system started")
    
    # Process a few frames
    logger.info("Processing 10 frames...")
    frames_processed = 0
    start_time = time.time()
    
    for _ in range(10):
        frame, results = system.process_frame()
        
        if frame is None:
            logger.error("❌ Failed to process frame")
            continue
            
        frames_processed += 1
        
        # Check detection results
        if results:
            logger.info(f"Frame {frames_processed} detection results:")
            for key, value in results.items():
                if isinstance(value, dict) and 'status' in value:
                    status = value['status']
                    logger.info(f" - {key}: {status}")
    
    elapsed = time.time() - start_time
    if frames_processed > 0:
        fps = frames_processed / elapsed
        logger.info(f"✅ Processed {frames_processed} frames in {elapsed:.2f}s ({fps:.2f} FPS)")
    
    # Stop monitoring system
    system.stop()
    logger.info("Monitoring system stopped")
    
    return frames_processed > 0

def main():
    """Run all diagnostic tests"""
    logger = setup_logging()
    logger.info("Starting Driver Monitoring System diagnostics")
    
    # Test camera
    camera_ok = test_camera()
    
    # Test detection modules
    modules_ok = test_detection_modules()
    
    # Test full system
    system_ok = test_monitoring_system()
    
    # Report results
    logger.info("\n--- Diagnostic Results ---")
    logger.info(f"Camera: {'✅ OK' if camera_ok else '❌ Failed'}")
    logger.info(f"Detection Modules: {'✅ OK' if modules_ok else '❌ Failed'}")
    logger.info(f"System Operation: {'✅ OK' if system_ok else '❌ Failed'}")
    
    # Overall status
    if camera_ok and modules_ok and system_ok:
        logger.info("\n✅ All tests passed. The system should be working properly.")
    else:
        logger.info("\n⚠️ Some tests failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
