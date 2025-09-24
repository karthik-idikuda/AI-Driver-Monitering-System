#!/usr/bin/env python3
"""
Simple test to verify camera feed sizing improvements without complex dependencies
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import time

class SimpleCameraSizeTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Sizing Test")
        self.root.geometry("1200x800")
        
        # Define colors
        self.colors = {
            'primary': '#ffffff',
            'accent': '#2196f3',
            'border': '#e0e0e0'
        }
        
        self.setup_ui()
        self.MIN_DISPLAY_WIDTH = 400
        self.MIN_DISPLAY_HEIGHT = 300
        
        # Cache for canvas dimensions
        self.cached_canvas_width = 800
        self.cached_canvas_height = 600
        self.last_canvas_check = 0
        
    def setup_ui(self):
        """Setup test UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Video container
        self.video_container = tk.Frame(main_frame, bg=self.colors['primary'], 
                                       highlightbackground=self.colors['accent'],
                                       highlightthickness=3)
        self.video_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Set minimum size for video container
        self.video_container.configure(width=820, height=640)
        self.video_container.pack_propagate(False)
        
        # Video canvas
        self.video_canvas = tk.Canvas(self.video_container, bg='white', 
                                    width=800, height=600,
                                    highlightthickness=1,
                                    highlightbackground=self.colors['border'])
        self.video_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.video_canvas.configure(width=800, height=600)
        self.video_canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Test buttons
        self.test_small_btn = tk.Button(control_frame, text="Test Small Window",
                                       command=self.test_small_window,
                                       bg=self.colors['accent'], fg='white')
        self.test_small_btn.pack(side=tk.LEFT, padx=5)
        
        self.test_large_btn = tk.Button(control_frame, text="Test Large Window",
                                       command=self.test_large_window,
                                       bg=self.colors['accent'], fg='white')
        self.test_large_btn.pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = tk.Label(control_frame, text="Resize window to test camera feed sizing",
                                  bg=self.colors['primary'])
        self.info_label.pack(side=tk.RIGHT, padx=5)
        
    def create_test_frame(self, width=640, height=480):
        """Create a test frame"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add colorful test pattern
        frame[:, :width//3] = [255, 0, 0]  # Red
        frame[:, width//3:2*width//3] = [0, 255, 0]  # Green  
        frame[:, 2*width//3:] = [0, 0, 255]  # Blue
        
        # Add text
        cv2.putText(frame, f"Test Frame {width}x{height}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add center crosshair
        cv2.line(frame, (width//2-50, height//2), (width//2+50, height//2), (255, 255, 255), 2)
        cv2.line(frame, (width//2, height//2-50), (width//2, height//2+50), (255, 255, 255), 2)
        
        return frame
        
    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        current_time = time.time()
        if current_time - self.last_canvas_check > 0.2:
            self.cached_canvas_width = max(event.width, 320)
            self.cached_canvas_height = max(event.height, 240)
            self.last_canvas_check = current_time
            self.update_info()
            
    def display_frame(self, frame):
        """Display frame with sizing improvements"""
        try:
            if frame is None:
                return
                
            # Convert to PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Get canvas dimensions
            self.video_canvas.update_idletasks()
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width > 10 and canvas_height > 10:
                self.cached_canvas_width = canvas_width
                self.cached_canvas_height = canvas_height
            
            # Minimum size enforcement
            effective_canvas_width = max(canvas_width, self.MIN_DISPLAY_WIDTH + 40)
            effective_canvas_height = max(canvas_height, self.MIN_DISPLAY_HEIGHT + 40)
            
            # Calculate scaling
            img_width, img_height = pil_image.size
            scale_x = (effective_canvas_width - 20) / img_width
            scale_y = (effective_canvas_height - 20) / img_height
            scale = min(scale_x, scale_y)
            
            # Apply constraints
            scale = max(scale, 0.3)  # Minimum scale
            scale = min(scale, 2.0)  # Maximum scale
            
            # Calculate new dimensions
            new_width = max(int(img_width * scale), self.MIN_DISPLAY_WIDTH)
            new_height = max(int(img_height * scale), self.MIN_DISPLAY_HEIGHT)
            
            # Aspect ratio preservation
            aspect_ratio = img_width / img_height
            if new_width / new_height < aspect_ratio * 0.8:
                new_width = int(new_height * aspect_ratio)
            elif new_height / new_width < (1/aspect_ratio) * 0.8:
                new_height = int(new_width / aspect_ratio)
            
            # Final bounds check
            if new_width > canvas_width - 10:
                new_width = canvas_width - 10
                new_height = int(new_width * img_height / img_width)
            if new_height > canvas_height - 10:
                new_height = canvas_height - 10
                new_width = int(new_height * img_width / img_height)
            
            # Final minimum enforcement
            new_width = max(new_width, self.MIN_DISPLAY_WIDTH)
            new_height = max(new_height, self.MIN_DISPLAY_HEIGHT)
            
            # Resize image
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Clear and display
            self.video_canvas.delete("all")
            self.video_canvas.configure(bg='white')
            
            # Center the image
            x_center = canvas_width // 2
            y_center = canvas_height // 2
            self.video_canvas.create_image(x_center, y_center, anchor=tk.CENTER, image=photo)
            
            # Keep reference
            self.video_canvas.image = photo
            
            # Update info
            self.update_info(f"Display: {new_width}x{new_height}, Canvas: {canvas_width}x{canvas_height}")
            
        except Exception as e:
            print(f"Error displaying frame: {str(e)}")
            
    def update_info(self, extra=""):
        """Update info label"""
        canvas_width = self.cached_canvas_width
        canvas_height = self.cached_canvas_height
        window_size = f"{self.root.winfo_width()}x{self.root.winfo_height()}"
        info = f"Window: {window_size}, Canvas: {canvas_width}x{canvas_height}"
        if extra:
            info += f", {extra}"
        self.info_label.config(text=info)
        
    def test_small_window(self):
        """Test with small window"""
        self.root.geometry("600x400")
        self.root.update()
        frame = self.create_test_frame()
        self.display_frame(frame)
        
    def test_large_window(self):
        """Test with large window"""
        self.root.geometry("1600x1000")
        self.root.update()
        frame = self.create_test_frame()
        self.display_frame(frame)
        
    def run_animated_test(self):
        """Run animated test"""
        def update_frame():
            # Create test frame with timestamp
            timestamp = int(time.time() * 2) % 10
            frame = self.create_test_frame()
            cv2.putText(frame, f"Time: {timestamp}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            self.display_frame(frame)
            self.root.after(100, update_frame)
            
        # Start animation
        update_frame()
        
        # Start GUI
        self.root.mainloop()

if __name__ == "__main__":
    print("🚀 Starting Simple Camera Sizing Test")
    print("   - Use the test buttons to change window size")
    print("   - Resize the window manually to test scaling")
    print("   - Camera feed should maintain minimum 400x300 size")
    
    test = SimpleCameraSizeTest()
    test.run_animated_test()
