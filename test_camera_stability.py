#!/usr/bin/env python3
"""
Test script to verify camera feed stability and anti-shake fixes
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
import threading

class CameraStabilityTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Feed Stability Test")
        self.root.geometry("1200x800")
        
        # Test variables
        self.is_running = False
        self.current_frame = None
        self.frame_ready = False
        
        # Canvas size caching for stability
        self.cached_canvas_width = 800
        self.cached_canvas_height = 600
        self.pending_canvas_width = 800
        self.pending_canvas_height = 600
        self.resize_timer = None
        
        # Animation variables
        self.border_glow_intensity = 0.0
        self.border_glow_direction = 1
        
        self.setup_ui()
        self.start_camera_simulation()
        
    def setup_ui(self):
        """Setup the test UI"""
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='lightgray', height=60)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        control_frame.pack_propagate(False)
        
        tk.Button(control_frame, text="Start Feed", command=self.start_feed,
                 bg='green', fg='white', font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Button(control_frame, text="Stop Feed", command=self.stop_feed,
                 bg='red', fg='white', font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Status: Ready", 
                                   font=('Arial', 12), bg='lightgray')
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Video display area
        video_frame = tk.LabelFrame(main_frame, text="📹 Stable Camera Feed Test", 
                                  font=('Arial', 14, 'bold'))
        video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video container with border
        self.video_container = tk.Frame(video_frame, bg='white', 
                                       highlightbackground='blue',
                                       highlightthickness=3)
        self.video_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Set minimum size to prevent shrinking
        self.video_container.configure(width=820, height=640)
        self.video_container.pack_propagate(False)
        
        # Video canvas
        self.video_canvas = tk.Canvas(self.video_container, bg='white', 
                                    width=800, height=600,
                                    highlightthickness=1,
                                    highlightbackground='lightblue')
        self.video_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Bind resize event with debouncing
        self.video_canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Start border animation
        self.animate_border()
        
    def start_camera_simulation(self):
        """Start simulated camera feed"""
        def generate_frames():
            frame_count = 0
            while True:
                if self.is_running:
                    # Generate a test frame with moving pattern
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    
                    # Add moving pattern to test stability
                    x_offset = int(50 * np.sin(frame_count * 0.1))
                    y_offset = int(30 * np.cos(frame_count * 0.1))
                    
                    # Draw test pattern
                    cv2.rectangle(frame, (100 + x_offset, 100 + y_offset), 
                                (200 + x_offset, 200 + y_offset), (0, 255, 0), -1)
                    cv2.rectangle(frame, (300 + x_offset, 200 + y_offset), 
                                (400 + x_offset, 300 + y_offset), (255, 0, 0), -1)
                    cv2.rectangle(frame, (200 + x_offset, 300 + y_offset), 
                                (300 + x_offset, 400 + y_offset), (0, 0, 255), -1)
                    
                    # Add text
                    cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, "Stability Test", (10, 70), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    self.current_frame = frame
                    self.frame_ready = True
                    frame_count += 1
                
                time.sleep(1/30)  # 30 FPS
                
        thread = threading.Thread(target=generate_frames, daemon=True)
        thread.start()
        
        # Start display update loop
        self.update_display()
        
    def start_feed(self):
        """Start the camera feed"""
        self.is_running = True
        self.status_label.config(text="Status: Running", fg="green")
        
    def stop_feed(self):
        """Stop the camera feed"""
        self.is_running = False
        self.status_label.config(text="Status: Stopped", fg="red")
        
    def on_canvas_resize(self, event):
        """Handle canvas resize with debouncing"""
        # Store new dimensions with minimum constraints
        self.pending_canvas_width = max(event.width, 600)
        self.pending_canvas_height = max(event.height, 450)
        
        # Cancel pending resize
        if self.resize_timer:
            try:
                self.root.after_cancel(self.resize_timer)
            except:
                pass
                
        # Schedule delayed resize
        self.resize_timer = self.root.after(150, self.apply_pending_resize)
        
    def apply_pending_resize(self):
        """Apply pending resize after debouncing"""
        # Only update if change is significant
        width_diff = abs(self.cached_canvas_width - self.pending_canvas_width)
        height_diff = abs(self.cached_canvas_height - self.pending_canvas_height)
        
        if width_diff > 20 or height_diff > 20:
            self.cached_canvas_width = self.pending_canvas_width
            self.cached_canvas_height = self.pending_canvas_height
            
            # Trigger redraw if we have a frame
            if self.current_frame is not None:
                self.display_frame(self.current_frame)
                
    def display_frame(self, frame):
        """Display frame with stable sizing"""
        if frame is None:
            return
            
        try:
            # Get canvas dimensions with minimums enforced
            canvas_width = max(self.video_canvas.winfo_width(), 600)
            canvas_height = max(self.video_canvas.winfo_height(), 450)
            
            # Use cached dimensions for stability
            if (abs(canvas_width - self.cached_canvas_width) < 10 and 
                abs(canvas_height - self.cached_canvas_height) < 10):
                canvas_width = self.cached_canvas_width
                canvas_height = self.cached_canvas_height
            else:
                self.cached_canvas_width = canvas_width
                self.cached_canvas_height = canvas_height
                
            # Calculate aspect ratio
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_width / frame_height
            
            # Calculate display size maintaining aspect ratio
            if canvas_width / canvas_height > aspect_ratio:
                display_width = max(400, int(canvas_height * aspect_ratio))
                display_height = canvas_height
            else:
                display_width = canvas_width
                display_height = max(300, int(canvas_width / aspect_ratio))
                
            # Ensure minimum display size
            display_width = max(display_width, 400)
            display_height = max(display_height, 300)
            
            # Resize frame smoothly
            resized_frame = cv2.resize(frame, (display_width, display_height), 
                                     interpolation=cv2.INTER_LINEAR)
                                     
            # Convert to PhotoImage
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            frame_image = ImageTk.PhotoImage(image=pil_image)
            
            # Clear canvas and draw frame
            self.video_canvas.delete("all")
            
            # Center the image
            x_center = canvas_width // 2
            y_center = canvas_height // 2
            
            self.video_canvas.create_image(x_center, y_center, 
                                         image=frame_image, anchor=tk.CENTER)
            
            # Keep reference
            self.video_canvas.image = frame_image
            
            # Add stable corner indicators
            self.draw_corner_indicators(canvas_width, canvas_height)
            
        except Exception as e:
            print(f"Error displaying frame: {e}")
            
    def draw_corner_indicators(self, width, height):
        """Draw stable corner indicators"""
        try:
            corner_size = 15
            color = "lime" if self.is_running else "red"
            
            # Four corners
            corners = [
                (10, 10),
                (width - 25, 10),
                (10, height - 25),
                (width - 25, height - 25)
            ]
            
            for x, y in corners:
                self.video_canvas.create_rectangle(
                    x, y, x + corner_size, y + corner_size,
                    outline=color, width=2, fill=""
                )
                
        except Exception as e:
            print(f"Error drawing indicators: {e}")
            
    def animate_border(self):
        """Animate border with stable timing"""
        try:
            self.border_glow_intensity += 0.02 * self.border_glow_direction
            
            if self.border_glow_intensity >= 1.0:
                self.border_glow_intensity = 1.0
                self.border_glow_direction = -1
            elif self.border_glow_intensity <= 0.2:
                self.border_glow_intensity = 0.2
                self.border_glow_direction = 1
                
            # Update border color
            intensity = int(255 * (0.3 + 0.7 * self.border_glow_intensity))
            color = f"#{intensity:02x}{intensity//2:02x}{255:02x}"
            
            self.video_container.config(highlightbackground=color)
            
        except Exception as e:
            print(f"Border animation error: {e}")
            
        # Schedule next frame
        self.root.after(100, self.animate_border)
        
    def update_display(self):
        """Update display loop"""
        try:
            if self.current_frame is not None and self.frame_ready:
                self.display_frame(self.current_frame)
                self.frame_ready = False
                
        except Exception as e:
            print(f"Display update error: {e}")
            
        # Schedule next update
        self.root.after(33, self.update_display)  # ~30 FPS
        
    def run(self):
        """Run the test application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Camera Feed Stability Test...")
    test_app = CameraStabilityTest()
    test_app.run()
