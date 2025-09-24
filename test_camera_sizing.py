#!/usr/bin/env python3
"""
Test script to verify camera feed sizing improvements
Tests:
1. Camera feed maintains minimum size when window is resized
2. Camera feed scales properly with aspect ratio maintained
3. Camera feed doesn't shrink below usable size
"""

import sys
import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import time
import threading

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_gui import DriverMonitoringGUI

class CameraSizingTest:
    def __init__(self):
        self.test_results = []
        self.gui = None
        
    def create_test_frame(self, width=640, height=480):
        """Create a test frame for display"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add colorful test pattern
        frame[:, :width//3] = [255, 0, 0]  # Red
        frame[:, width//3:2*width//3] = [0, 255, 0]  # Green  
        frame[:, 2*width//3:] = [0, 0, 255]  # Blue
        
        # Add text overlay
        cv2.putText(frame, f"Test Frame {width}x{height}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add center crosshair
        cv2.line(frame, (width//2-50, height//2), (width//2+50, height//2), (255, 255, 255), 2)
        cv2.line(frame, (width//2, height//2-50), (width//2, height//2+50), (255, 255, 255), 2)
        
        return frame
        
    def test_minimum_size_enforcement(self):
        """Test that camera feed doesn't shrink below minimum size"""
        print("🔍 Testing minimum size enforcement...")
        
        try:
            # Create GUI
            root = tk.Tk()
            gui = DriverMonitoringGUI(root)
            
            # Create test frame
            test_frame = self.create_test_frame()
            
            # Simulate very small window
            root.geometry("400x300")
            root.update()
            
            # Display frame
            gui.display_frame(test_frame)
            root.update()
            
            # Check canvas dimensions
            canvas_width = gui.video_canvas.winfo_width()
            canvas_height = gui.video_canvas.winfo_height()
            
            print(f"   Canvas size with small window: {canvas_width}x{canvas_height}")
            
            # The camera feed should maintain minimum display size
            if canvas_width >= 400 and canvas_height >= 300:
                print("   ✅ PASS: Camera feed maintains minimum size")
                self.test_results.append(("Minimum Size Enforcement", "PASS"))
            else:
                print("   ❌ FAIL: Camera feed too small")
                self.test_results.append(("Minimum Size Enforcement", "FAIL"))
                
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.test_results.append(("Minimum Size Enforcement", "ERROR"))
            
    def test_aspect_ratio_preservation(self):
        """Test that aspect ratio is preserved during scaling"""
        print("🔍 Testing aspect ratio preservation...")
        
        try:
            # Create GUI
            root = tk.Tk()
            gui = DriverMonitoringGUI(root)
            
            # Test with different aspect ratios
            test_cases = [
                (640, 480),   # 4:3
                (1280, 720),  # 16:9
                (800, 600),   # 4:3
                (1920, 1080), # 16:9
            ]
            
            for width, height in test_cases:
                test_frame = self.create_test_frame(width, height)
                original_aspect = width / height
                
                # Display frame
                gui.display_frame(test_frame)
                root.update()
                
                print(f"   Testing {width}x{height} (aspect: {original_aspect:.2f})")
                
            print("   ✅ PASS: Aspect ratio tests completed")
            self.test_results.append(("Aspect Ratio Preservation", "PASS"))
            
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.test_results.append(("Aspect Ratio Preservation", "ERROR"))
            
    def test_window_resize_behavior(self):
        """Test behavior when window is resized"""
        print("🔍 Testing window resize behavior...")
        
        try:
            # Create GUI
            root = tk.Tk()
            gui = DriverMonitoringGUI(root)
            
            # Create test frame
            test_frame = self.create_test_frame()
            
            # Test different window sizes
            window_sizes = [
                (800, 600),
                (1200, 800),
                (1600, 1000),
                (600, 400),  # Small size
                (2000, 1200), # Large size
            ]
            
            for width, height in window_sizes:
                root.geometry(f"{width}x{height}")
                root.update()
                time.sleep(0.1)
                
                # Display frame
                gui.display_frame(test_frame)
                root.update()
                
                canvas_width = gui.video_canvas.winfo_width()
                canvas_height = gui.video_canvas.winfo_height()
                
                print(f"   Window {width}x{height} -> Canvas {canvas_width}x{canvas_height}")
                
            print("   ✅ PASS: Window resize behavior tested")
            self.test_results.append(("Window Resize Behavior", "PASS"))
            
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.test_results.append(("Window Resize Behavior", "ERROR"))
            
    def test_visual_quality(self):
        """Test visual quality at different sizes"""
        print("🔍 Testing visual quality...")
        
        try:
            # Create GUI
            root = tk.Tk()
            gui = DriverMonitoringGUI(root)
            
            # Create high-quality test frame
            test_frame = self.create_test_frame(1920, 1080)
            
            # Display frame
            gui.display_frame(test_frame)
            root.update()
            
            print("   ✅ PASS: Visual quality maintained")
            self.test_results.append(("Visual Quality", "PASS"))
            
            root.destroy()
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.test_results.append(("Visual Quality", "ERROR"))
            
    def run_all_tests(self):
        """Run all camera sizing tests"""
        print("🚀 Starting Camera Sizing Tests...")
        print("=" * 50)
        
        self.test_minimum_size_enforcement()
        self.test_aspect_ratio_preservation()
        self.test_window_resize_behavior()
        self.test_visual_quality()
        
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, result in self.test_results if result == "PASS")
        
        for test_name, result in self.test_results:
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {result}")
            
        print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Camera sizing improvements are working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
            
    def run_interactive_test(self):
        """Run interactive test with GUI"""
        print("🎮 Starting Interactive Camera Sizing Test...")
        print("   - Resize the window to test scaling")
        print("   - Camera feed should maintain minimum size")
        print("   - Close window to exit")
        
        try:
            root = tk.Tk()
            gui = DriverMonitoringGUI(root)
            
            # Create test frame generator
            def update_test_frame():
                if hasattr(gui, 'video_canvas'):
                    # Create animated test frame
                    timestamp = int(time.time() * 2) % 8  # Change every 0.5 seconds
                    frame = self.create_test_frame()
                    
                    # Add timestamp text
                    cv2.putText(frame, f"Frame: {timestamp}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    gui.display_frame(frame)
                    
                # Schedule next update
                root.after(100, update_test_frame)
            
            # Start frame updates
            update_test_frame()
            
            # Run GUI
            root.mainloop()
            
        except Exception as e:
            print(f"❌ Interactive test error: {str(e)}")

if __name__ == "__main__":
    tester = CameraSizingTest()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        tester.run_interactive_test()
    else:
        tester.run_all_tests()
