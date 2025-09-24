#!/usr/bin/env python3
"""
Simple test script for Driver Monitoring System
Tests basic functionality with minimal dependencies
"""

import cv2
import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_camera():
    """Test camera functionality"""
    print("Testing camera...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not accessible")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("❌ Cannot read from camera")
        cap.release()
        return False
    
    print("✅ Camera working")
    cap.release()
    return True

def test_opencv_cascades():
    """Test OpenCV cascade classifiers"""
    print("Testing OpenCV cascades...")
    
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        if face_cascade.empty() or eye_cascade.empty():
            print("❌ OpenCV cascades not loaded")
            return False
        
        print("✅ OpenCV cascades loaded")
        return True
        
    except Exception as e:
        print(f"❌ Error loading cascades: {e}")
        return False

def test_mediapipe():
    """Test MediaPipe functionality"""
    print("Testing MediaPipe...")
    
    try:
        import mediapipe as mp
        
        # Test face mesh
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
        
        # Test hands
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=2)
        
        print("✅ MediaPipe working")
        return True
        
    except Exception as e:
        print(f"❌ MediaPipe error: {e}")
        return False

def test_simple_detection():
    """Test simple face and eye detection"""
    print("Testing simple detection...")
    
    try:
        from simple_drowsiness_detector import SimpleDrowsinessDetector
        
        detector = SimpleDrowsinessDetector()
        
        # Test with camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera for detection test")
            return False
        
        print("Starting detection test (press 'q' to quit)...")
        
        frame_count = 0
        start_time = time.time()
        
        while frame_count < 100:  # Test for 100 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, is_drowsy, score = detector.detect_drowsiness(frame)
            
            # Display result
            cv2.imshow('Detection Test', processed_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        end_time = time.time()
        fps = frame_count / (end_time - start_time)
        
        print(f"✅ Detection test completed: {frame_count} frames at {fps:.1f} FPS")
        return True
        
    except Exception as e:
        print(f"❌ Detection test error: {e}")
        return False

def test_directory_structure():
    """Test if required directories exist"""
    print("Testing directory structure...")
    
    required_dirs = [
        'src',
        'gui', 
        'utils',
        'config',
        'models',
        'data/logs',
        'data/known_faces',
        'data/screenshots',
        'data/recordings',
        'data/alerts'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Directory structure complete")
    return True

def test_config_file():
    """Test configuration file"""
    print("Testing configuration file...")
    
    try:
        import json
        
        config_path = 'config/config.json'
        if not os.path.exists(config_path):
            print("❌ Configuration file missing")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = ['camera', 'detection_settings', 'models', 'alerts']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing config section: {section}")
                return False
        
        print("✅ Configuration file valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("Driver Monitoring System - Basic Tests")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Configuration File", test_config_file),
        ("Camera Access", test_camera),
        ("OpenCV Cascades", test_opencv_cascades),
        ("MediaPipe", test_mediapipe),
        ("Simple Detection", test_simple_detection),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! System should work correctly.")
        print("\nNext steps:")
        print("1. Run: python main.py --mode gui")
        print("2. Or run: python main.py --mode console")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("\nTroubhooting:")
        print("1. Ensure camera is connected and not used by other apps")
        print("2. Install requirements: pip install -r requirements.txt")
        print("3. Check permissions for camera access")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
