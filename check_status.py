#!/usr/bin/env python3
"""
Driver Monitoring System - Status Check
Quick verification that everything is working correctly.
"""

import sys
import os
import subprocess

def check_venv():
    """Check if virtual environment is activated"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is activated")
        print(f"   Python: {sys.executable}")
        return True
    else:
        print("❌ Virtual environment is not activated")
        print("   Please run: source venv/bin/activate")
        return False

def check_packages():
    """Check if required packages are installed"""
    required_packages = ['cv2', 'mediapipe', 'numpy', 'PIL', 'scipy', 'tkinter']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is not available")
            return False
    return True

def check_camera():
    """Check if camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera is accessible")
            cap.release()
            return True
        else:
            print("❌ Camera is not accessible")
            return False
    except Exception as e:
        print(f"❌ Camera check failed: {e}")
        return False

def main():
    print("🚗 Driver Monitoring System - Status Check")
    print("==========================================")
    
    checks = [
        check_venv(),
        check_packages(),
        check_camera()
    ]
    
    if all(checks):
        print("\n🎉 All checks passed! System is ready to use.")
        print("\n📋 Next steps:")
        print("   ./run_system.sh gui      - Start with GUI")
        print("   ./run_system.sh console  - Start in console mode")
        print("   ./run_system.sh test     - Run comprehensive tests")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")

if __name__ == "__main__":
    main()
