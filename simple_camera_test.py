#!/usr/bin/env python3
"""
Simplified GUI test for camera feed display
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import time

class SimpleCameraGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Feed Test")
        self.root.geometry("800x600")
        
        self.cap = None
        self.is_running = False
        self.current_frame = None
        
        self.setup_gui()
        
    def setup_gui(self):
        # Control frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)
        
        ttk.Button(control_frame, text="Start Camera", command=self.start_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop Camera", command=self.stop_camera).pack(side=tk.LEFT, padx=5)
        
        # Video display
        self.video_canvas = tk.Canvas(self.root, bg='black', width=640, height=480)
        self.video_canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Camera not started")
        self.status_label.pack(pady=5)
        
        # Start GUI update loop
        self.update_gui()
    
    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.status_label.config(text="❌ Failed to open camera")
                return
            
            self.is_running = True
            self.status_label.config(text="✅ Camera started")
            
            # Start capture thread
            self.capture_thread = threading.Thread(target=self.capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {str(e)}")
    
    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status_label.config(text="Camera stopped")
        self.video_canvas.delete("all")
    
    def capture_loop(self):
        while self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.current_frame = frame.copy()
            time.sleep(0.03)  # ~30 FPS
    
    def update_gui(self):
        if self.current_frame is not None:
            self.display_frame()
        
        self.root.after(16, self.update_gui)  # ~60 FPS
    
    def display_frame(self):
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Get canvas dimensions
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 640
                canvas_height = 480
            
            # Resize image to fit canvas
            img_width, img_height = pil_image.size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(pil_image)
            
            # Clear canvas and add image
            self.video_canvas.delete("all")
            self.video_canvas.create_image(canvas_width//2, canvas_height//2, anchor=tk.CENTER, image=photo)
            self.video_canvas.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Error displaying frame: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleCameraGUI()
    app.run()
