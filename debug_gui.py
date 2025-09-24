#!/usr/bin/env python3
"""
Debug version of the GUI to identify camera feed issues
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import logging
import os
import sys
import time
from datetime import datetime

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DebugCameraGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Debug Camera GUI")
        self.root.geometry("900x700")
        
        self.camera = None
        self.is_monitoring = False
        self.current_frame = None
        self.frame_count = 0
        
        self.setup_gui()
        self.update_gui()
        
    def setup_gui(self):
        # Control panel
        control_frame = ttk.LabelFrame(self.root, text="Debug Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Test Direct Camera", command=self.test_direct_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Start Monitoring System", command=self.start_monitoring_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(control_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=20)
        
        # Video display
        video_frame = ttk.LabelFrame(self.root, text="Camera Feed", padding=5)
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=640, height=480)
        self.video_canvas.pack(expand=True, fill=tk.BOTH)
        
        # Debug info
        debug_frame = ttk.LabelFrame(self.root, text="Debug Info", padding=10)
        debug_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.debug_text = tk.Text(debug_frame, height=8, width=80)
        scrollbar = ttk.Scrollbar(debug_frame, orient=tk.VERTICAL, command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=scrollbar.set)
        
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def log_debug(self, message):
        """Add debug message to text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.debug_text.see(tk.END)
        logger.debug(message)
        
    def test_direct_camera(self):
        """Test direct camera access"""
        self.log_debug("Testing direct camera access...")
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.log_debug("❌ Failed to open camera")
                return
            
            self.log_debug("✅ Camera opened successfully")
            
            # Get properties
            width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            self.log_debug(f"Camera properties: {width}x{height} @ {fps} FPS")
            
            # Start direct capture
            self.is_monitoring = True
            self.status_var.set("Direct Camera Active")
            self.capture_thread = threading.Thread(target=self.direct_capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
        except Exception as e:
            self.log_debug(f"❌ Error: {str(e)}")
            
    def direct_capture_loop(self):
        """Direct camera capture loop"""
        self.log_debug("Starting direct capture loop")
        
        while self.is_monitoring and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    self.current_frame = frame.copy()
                    self.frame_count += 1
                    
                    if self.frame_count % 30 == 0:
                        self.log_debug(f"Captured {self.frame_count} frames, current shape: {frame.shape}")
                else:
                    self.log_debug("Failed to read frame")
                    
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                self.log_debug(f"Error in capture loop: {str(e)}")
                break
                
        self.log_debug("Direct capture loop ended")
    
    def start_monitoring_system(self):
        """Test the full monitoring system"""
        self.log_debug("Testing full monitoring system...")
        
        try:
            from main_detector import DriverMonitoringSystem
            
            self.log_debug("Initializing DriverMonitoringSystem...")
            self.monitoring_system = DriverMonitoringSystem()
            
            self.log_debug("Starting monitoring system...")
            if not self.monitoring_system.start():
                self.log_debug("❌ Failed to start monitoring system")
                return
            
            self.log_debug("✅ Monitoring system started")
            self.status_var.set("Monitoring System Active")
            
            # Start monitoring thread
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_system_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
        except Exception as e:
            self.log_debug(f"❌ Error: {str(e)}")
            import traceback
            self.log_debug(traceback.format_exc())
    
    def monitoring_system_loop(self):
        """Monitoring system loop"""
        self.log_debug("Starting monitoring system loop")
        
        while self.is_monitoring and hasattr(self, 'monitoring_system'):
            try:
                frame, results = self.monitoring_system.process_frame()
                
                if frame is not None:
                    self.current_frame = frame.copy()
                    self.frame_count += 1
                    
                    if self.frame_count % 30 == 0:
                        self.log_debug(f"Processed {self.frame_count} frames, shape: {frame.shape}")
                        if results:
                            self.log_debug(f"Detection results: {list(results.keys())}")
                else:
                    self.log_debug("No frame from monitoring system")
                    
                time.sleep(0.033)
                
            except Exception as e:
                self.log_debug(f"Error in monitoring system loop: {str(e)}")
                break
        
        self.log_debug("Monitoring system loop ended")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.status_var.set("Stopped")
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        if hasattr(self, 'monitoring_system'):
            self.monitoring_system.stop()
            
        self.log_debug("Monitoring stopped")
    
    def update_gui(self):
        """Update GUI"""
        try:
            if self.current_frame is not None:
                self.display_frame()
                
        except Exception as e:
            self.log_debug(f"Error updating GUI: {str(e)}")
        
        self.root.after(16, self.update_gui)
    
    def display_frame(self):
        """Display frame on canvas"""
        try:
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Get canvas size
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 640
                canvas_height = 480
            
            # Resize
            img_width, img_height = pil_image.size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Display
            self.video_canvas.delete("all")
            self.video_canvas.create_image(canvas_width//2, canvas_height//2, anchor=tk.CENTER, image=photo)
            self.video_canvas.image = photo
            
        except Exception as e:
            self.log_debug(f"Error displaying frame: {str(e)}")
    
    def run(self):
        """Run the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_monitoring()
        self.root.destroy()

if __name__ == "__main__":
    app = DebugCameraGUI()
    app.run()
