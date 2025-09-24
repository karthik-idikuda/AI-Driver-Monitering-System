#!/usr/bin/env python3
"""
Simple camera test to verify camera functionality
"""

import cv2
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_camera_simple():
    """Simple test to verify camera is working"""
    logger.info("Testing camera access...")
    
    # Try different backends
    backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_ANY]
    
    for backend in backends:
        try:
            logger.info(f"Trying backend: {backend}")
            cap = cv2.VideoCapture(0, backend)
            
            if cap.isOpened():
                logger.info("Camera opened successfully")
                
                # Try to read a few frames
                for i in range(5):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        logger.info(f"Frame {i+1}: {frame.shape}, dtype: {frame.dtype}")
                    else:
                        logger.error(f"Failed to read frame {i+1}")
                        break
                
                cap.release()
                logger.info("✅ Camera test successful")
                return True
            else:
                logger.warning("Failed to open camera")
                
        except Exception as e:
            logger.error(f"Camera test failed: {str(e)}")
    
    logger.error("❌ All camera tests failed")
    return False

if __name__ == "__main__":
    test_camera_simple()
