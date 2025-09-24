#!/usr/bin/env python3
"""
Simple camera test to verify OpenCV camera access
"""

import cv2
import time

def test_camera():
    print("Testing camera access...")
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return False
    
    print("✅ Camera opened successfully")
    
    # Get camera properties
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Camera properties: {width}x{height} @ {fps} FPS")
    
    # Try to read a few frames
    for i in range(5):
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✅ Frame {i+1}: {frame.shape}")
        else:
            print(f"❌ Failed to read frame {i+1}")
        time.sleep(0.1)
    
    # Create a window and display frames for 5 seconds
    print("Displaying camera feed for 5 seconds...")
    start_time = time.time()
    
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if ret and frame is not None:
            cv2.imshow('Camera Test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Failed to read frame")
            break
    
    cv2.destroyAllWindows()
    cap.release()
    print("Camera test completed")
    return True

if __name__ == "__main__":
    test_camera()
