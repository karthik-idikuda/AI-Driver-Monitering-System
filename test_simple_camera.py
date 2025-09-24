#!/usr/bin/env python3
"""
Simple camera test to verify video feed functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time

class SimpleCameraTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎥 Simple Camera Feed Test")
        self.root.geometry("900x700")
        self.root.configure(bg='white')
        
        # Camera variables
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.capture_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the test UI"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="📹 Camera Feed Test", 
                              font=('Arial', 18, 'bold'), bg='white')
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg='lightgray', height=60)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        control_frame.pack_propagate(False)
        
        # Control buttons
        self.start_btn = tk.Button(control_frame, text="▶️ Start Camera", 
                                  command=self.start_camera,
                                  bg='green', fg='white', font=('Arial', 12, 'bold'),
                                  padx=20, pady=10)
        self.start_btn.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop Camera", 
                                 command=self.stop_camera,
                                 bg='red', fg='white', font=('Arial', 12, 'bold'),
                                 padx=20, pady=10)
        self.stop_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Status: Ready", 
                                   font=('Arial', 12), bg='lightgray')
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Video frame
        video_frame = tk.LabelFrame(main_frame, text="📹 Live Camera Feed", 
                                  font=('Arial', 14, 'bold'))
        video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video canvas
        self.video_canvas = tk.Canvas(video_frame, bg='white', 
                                    width=640, height=480,
                                    highlightthickness=2,
                                    highlightbackground='blue')
        self.video_canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Show initial placeholder
        self.show_placeholder()
        
        # Start update loop
        self.update_display()
        
    def show_placeholder(self):
        """Show placeholder when camera is not active"""
        self.video_canvas.delete("all")
        width = self.video_canvas.winfo_width() or 640
        height = self.video_canvas.winfo_height() or 480
        
        # Create placeholder
        self.video_canvas.create_rectangle(
            20, 20, width-20, height-20,
            outline='gray', width=2, fill='lightgray'
        )
        
        # Camera icon
        icon_x, icon_y = width//2, height//2 - 20
        self.video_canvas.create_rectangle(
            icon_x-25, icon_y-15, icon_x+25, icon_y+15,
            outline='blue', width=2, fill=''
        )
        self.video_canvas.create_oval(
            icon_x-6, icon_y-6, icon_x+6, icon_y+6,
            outline='blue', width=2, fill=''
        )
        
        # Text
        self.video_canvas.create_text(
            width//2, height//2 + 20,
            text="Click 'Start Camera' to begin video feed",
            font=('Arial', 14), fill='black'
        )
        
    def start_camera(self):
        """Start camera capture"""
        try:
            self.status_label.config(text="Status: Starting camera...")
            self.root.update()
            
            # Try to open camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                # Try other camera indices
                for i in range(1, 5):
                    self.camera = cv2.VideoCapture(i)
                    if self.camera.isOpened():
                        break
                else:
                    raise Exception("No camera found")
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # Start capture
            self.is_running = True
            self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
            self.capture_thread.start()
            
            self.status_label.config(text="Status: Camera running", fg="green")
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            print("Camera started successfully")
            
        except Exception as e:
            error_msg = f"Camera error: {e}"
            print(error_msg)
            self.status_label.config(text=f"Status: {error_msg}", fg="red")
            messagebox.showerror("Camera Error", f"Failed to start camera: {e}")
            
    def stop_camera(self):
        """Stop camera capture"""
        self.is_running = False
        
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            
        self.current_frame = None
        self.show_placeholder()
        
        self.status_label.config(text="Status: Camera stopped", fg="red")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        print("Camera stopped")
        
    def capture_loop(self):
        """Capture frames in a loop"""
        frame_count = 0
        while self.is_running and self.camera is not None:
            try:
                ret, frame = self.camera.read()
                if ret:
                    self.current_frame = frame.copy()
                    frame_count += 1
                    if frame_count % 30 == 0:  # Print every 30 frames
                        print(f"Captured {frame_count} frames")
                else:
                    print("Failed to read frame")
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(0.1)
                
            time.sleep(1/30)  # 30 FPS
            
    def update_display(self):
        """Update the display with current frame"""
        try:
            if self.current_frame is not None and self.is_running:
                # Get canvas dimensions
                canvas_width = self.video_canvas.winfo_width()
                canvas_height = self.video_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:  # Valid dimensions
                    frame = self.current_frame.copy()
                    
                    # Resize frame to fit canvas
                    frame_height, frame_width = frame.shape[:2]
                    aspect_ratio = frame_width / frame_height
                    
                    if canvas_width / canvas_height > aspect_ratio:
                        display_height = canvas_height - 20
                        display_width = int(display_height * aspect_ratio)
                    else:
                        display_width = canvas_width - 20
                        display_height = int(display_width / aspect_ratio)
                    
                    # Resize frame
                    resized_frame = cv2.resize(frame, (display_width, display_height))
                    
                    # Convert to RGB and create PhotoImage
                    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(rgb_frame)
                    photo = ImageTk.PhotoImage(image=pil_image)
                    
                    # Clear canvas and display frame
                    self.video_canvas.delete("all")
                    self.video_canvas.create_image(
                        canvas_width//2, canvas_height//2, 
                        image=photo, anchor=tk.CENTER
                    )
                    
                    # Keep reference
                    self.video_canvas.image = photo
                    
        except Exception as e:
            print(f"Display error: {e}")
            
        # Schedule next update
        self.root.after(33, self.update_display)  # ~30 FPS
        
    def on_closing(self):
        """Handle window close"""
        self.stop_camera()
        self.root.destroy()
        
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Simple Camera Test...")
    app = SimpleCameraTest()
    app.run()
