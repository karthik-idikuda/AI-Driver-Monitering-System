"""
Advanced Animated GUI Application for Driver Monitoring System
Built with Tkinter featuring modern animations and advanced visual effects
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance
import threading
import logging
import os
import sys
import time
import math
import random
from datetime import datetime
import colorsys
import numpy as np

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from main_detector import DriverMonitoringSystem
from config_manager import ConfigManager
from alert_system import AlertSystem
from futuristic_video_feed import FuturisticVideoFeed

# Try to import dashboard module, but don't fail if it's not available
try:
    from dashboard_module import DashboardModule
except ImportError:
    print("Warning: dashboard_module not found, dashboard functionality will be limited")
    DashboardModule = None

logger = logging.getLogger(__name__)

class DriverMonitoringGUI:
    def __init__(self):
        self.root = tk.Tk()
        
        # Enhanced styling colors - modern white theme
        self.colors = {
            'primary': '#ffffff',           # White background
            'secondary': '#f8f9fa',         # Light gray background
            'accent': '#2196f3',            # Blue accent
            'highlight': '#ff6b6b',         # Red highlight
            'success': '#4caf50',           # Green success
            'warning': '#ff9800',           # Orange warning
            'danger': '#f44336',            # Red danger
            'text_primary': '#212529',      # Dark text
            'text_secondary': '#6c757d',    # Gray text
            'glass_bg': 'rgba(0, 0, 0, 0.05)',  # Light glass effect
            'glow': '#2196f3',              # Blue glow
            'border': '#e9ecef',            # Light border
            'shadow': '#00000020'           # Subtle shadow
        }
        
        self.setup_window()
        
        # Initialize system components
        self.config_manager = ConfigManager()
        self.monitoring_system = None
        self.is_monitoring = False
        self.current_frame = None
        self.frame_ready = False  # Flag to indicate when frame is ready
        self.detection_results = {}  # Store detection results
        
        # Camera components (now managed by monitoring system)
        self.capture_thread = None
        
        # Removed canvas size caching variables - no longer needed
        # self.cached_canvas_width = 800
        # self.cached_canvas_height = 600
        # self.last_canvas_check = 0
        # self.pending_canvas_width = 800
        # self.pending_canvas_height = 600
        # self.resize_timer = None
        
        # Animation variables
        self.animation_time = 0
        self.pulse_alpha = 0.5
        self.pulse_direction = 1
        self.rotation_angle = 0
        self.zoom_factor = 1.0
        self.zoom_direction = 1
        self.gradient_offset = 0
        self.status_animation_frame = 0
        
        # Visual effects variables
        self.border_glow_intensity = 0.0
        self.border_glow_direction = 1
        self.status_indicator_animations = {}
        self.last_alert_time = {}
        
        # Simple detection animation variables
        self.scan_line_position = 0
        self.scan_line_direction = 1
        
        # GUI Variables
        self.setup_variables()
        
        # Create GUI layout with animations
        self.create_widgets()
        
        # Start animation loops
        self.start_animations()
        
        # Start GUI update loop
        self.update_gui()
    
    def setup_window(self):
        """Setup main window properties with modern styling"""
        self.root.title("🚗 Advanced Driver Monitoring System")
        self.root.geometry("1600x1000")  # Larger window for better camera display
        self.root.configure(bg=self.colors['primary'])
        
        # Set window to be resizable with constraints
        self.root.minsize(1400, 900)
        
        # Configure modern ttk styling
        self.setup_modern_styling()
        
        # Set window icon (if available)
        try:
            icon_path = "data/icons/app_icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Configure window protocol for smooth closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_modern_styling(self):
        """Setup modern ttk styling with custom themes"""
        style = ttk.Style()
        
        # Configure modern ttk styling with white theme
        style.configure('Modern.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none',
                       relief='solid',
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['highlight']),
                           ('pressed', self.colors['secondary']),
                           ('disabled', '#cccccc')])
        
        # Configure modern labelframe style
        style.configure('Modern.TLabelframe',
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=2,
                       relief='solid',
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['primary'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 12, 'bold'))
        
        # Configure modern frame style
        style.configure('Modern.TFrame',
                       background=self.colors['primary'],
                       borderwidth=1,
                       relief='solid')
        
        # Configure modern label style
        style.configure('Modern.TLabel',
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        # Configure status labels
        style.configure('Status.TLabel',
                       background=self.colors['primary'],
                       foreground=self.colors['success'],
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Alert.TLabel',
                       background=self.colors['primary'],
                       foreground=self.colors['danger'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure checkbutton style
        style.configure('Modern.TCheckbutton',
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       focuscolor='none',
                       font=('Segoe UI', 10))
    
    def start_animations(self):
        """Start essential animation loops only - minimal to prevent artifacts"""
        self.animate_interface()
        # Disable status and border animations that may cause black box artifacts
        # self.animate_status_indicators()
        # self.animate_border_glow()
        # Disable complex animations that might cause box effects
        # self.animate_futuristic_effects()
        # self.animate_hud_systems()
        # self.animate_quantum_effects()

    def animate_futuristic_effects(self):
        """Animate futuristic visual effects"""
        try:
            # Update hologram intensity
            self.hologram_intensity += 0.03 * self.hologram_direction
            if self.hologram_intensity >= 1.0:
                self.hologram_intensity = 1.0
                self.hologram_direction = -1
            elif self.hologram_intensity <= 0.0:
                self.hologram_intensity = 0.0
                self.hologram_direction = 1

            # Update quantum effect time
            self.quantum_effect_time += 0.05

            # Schedule next animation frame
            self.root.after(50, self.animate_futuristic_effects)
            
        except Exception as e:
            logger.error(f"Error in futuristic effects animation: {e}")
            self.root.after(100, self.animate_futuristic_effects)

    def animate_hud_systems(self):
        """Animate HUD system elements"""
        try:
            # Update cyber grid offset
            self.cyber_grid_offset += 0.01

            # Update scan line positions
            if hasattr(self, 'scan_line_position'):
                self.scan_line_position += 2 * self.scan_line_direction

            # Schedule next animation frame
            self.root.after(33, self.animate_hud_systems)  # ~30 FPS
            
        except Exception as e:
            logger.error(f"Error in HUD systems animation: {e}")
            self.root.after(100, self.animate_hud_systems)

    def animate_quantum_effects(self):
        """Animate quantum particle effects"""
        try:
            # Update quantum effect parameters
            self.quantum_effect_time += 0.02
            
            # Create new quantum particles occasionally
            if hasattr(self, 'quantum_particles') and random.random() < 0.1:
                if len(self.quantum_particles) < 50:
                    new_particle = {
                        'x': random.random() * 800,
                        'y': random.random() * 600,
                        'vx': (random.random() - 0.5) * 2,
                        'vy': (random.random() - 0.5) * 2,
                        'size': 1 + random.random() * 2,
                        'life': 1.0,
                        'color_phase': random.random() * 2 * math.pi
                    }
                    self.quantum_particles.append(new_particle)

            # Schedule next animation frame
            self.root.after(67, self.animate_quantum_effects)  # ~15 FPS for particles
            
        except Exception as e:
            logger.error(f"Error in quantum effects animation: {e}")
            self.root.after(100, self.animate_quantum_effects)
    
    def setup_variables(self):
        """Setup GUI variables"""
        self.var_drowsiness = tk.BooleanVar(value=True)
        self.var_distraction = tk.BooleanVar(value=True)
        self.var_seatbelt = tk.BooleanVar(value=True)
        self.var_attention = tk.BooleanVar(value=True)
        self.var_hand_position = tk.BooleanVar(value=True)
        self.var_facial_recognition = tk.BooleanVar(value=True)
        self.var_emotion = tk.BooleanVar(value=True)
        
        self.var_sound_alerts = tk.BooleanVar(value=True)
        self.var_visual_alerts = tk.BooleanVar(value=True)
        
        # Status variables
        self.var_status = tk.StringVar(value="Not Monitoring")
        self.var_fps = tk.StringVar(value="0 FPS")
        self.var_driver_name = tk.StringVar(value="Unknown")
        self.var_alert_count = tk.StringVar(value="0")
    
    def create_widgets(self):
        """Create all GUI widgets with improved layout"""
        # Create main container with proper spacing
        main_container = tk.Frame(self.root, bg=self.colors['primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top section for menu and controls
        self.create_menu_bar()
        self.create_control_panel(main_container)
        
        # Create main content area with three sections
        content_frame = tk.Frame(main_container, bg=self.colors['primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel for detection settings
        left_panel = tk.Frame(content_frame, bg=self.colors['primary'], width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Center panel for large camera feed
        center_panel = tk.Frame(content_frame, bg=self.colors['primary'])
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Right panel for status and driver info
        right_panel = tk.Frame(content_frame, bg=self.colors['primary'], width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Create content in each panel
        self.create_detection_panel(left_panel)
        self.create_video_display(center_panel)
        self.create_status_panel(right_panel)
        self.create_alert_panel()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export Alert Log", command=self.export_alert_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Add Driver Face", command=self.add_driver_face)
        tools_menu.add_command(label="Calibrate Camera", command=self.calibrate_camera)
        tools_menu.add_command(label="Test Alerts", command=self.test_alerts)
        tools_menu.add_separator()
        tools_menu.add_command(label="Dashboard", command=self.open_dashboard)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
    
    def create_control_panel(self, parent):
        """Create animated control panel with modern styling"""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Control Panel", style='Modern.TLabelframe', padding=15)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Create animated button container
        button_container = ttk.Frame(control_frame, style='Modern.TFrame')
        button_container.pack(side=tk.LEFT, fill=tk.Y)
        
        # Monitoring controls with modern styling
        self.start_btn = self.create_animated_button(button_container, "▶️ Start Monitoring", 
                                                    self.start_monitoring, self.colors['success'])
        self.start_btn.pack(side=tk.LEFT, padx=8, pady=5)
        
        self.stop_btn = self.create_animated_button(button_container, "⏹️ Stop Monitoring", 
                                                   self.stop_monitoring, self.colors['danger'])
        self.stop_btn.pack(side=tk.LEFT, padx=8, pady=5)
        
        self.pause_btn = self.create_animated_button(button_container, "⏸️ Pause", 
                                                    self.pause_monitoring, self.colors['warning'])
        self.pause_btn.pack(side=tk.LEFT, padx=8, pady=5)
        
        # Animated status display
        status_container = ttk.Frame(control_frame, style='Modern.TFrame')
        status_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        # Status with animated indicator
        self.status_frame = tk.Frame(status_container, bg=self.colors['primary'])
        self.status_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(self.status_frame, text="Status:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.status_indicator = tk.Label(self.status_frame, text="●", 
                                       foreground=self.colors['danger'], 
                                       background=self.colors['primary'],
                                       font=('Segoe UI', 14, 'bold'))
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(self.status_frame, textvariable=self.var_status, 
                                     style='Modern.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Animated FPS counter
        self.fps_frame = tk.Frame(status_container, bg=self.colors['primary'])
        self.fps_frame.pack(side=tk.RIGHT, padx=10)
        
        self.fps_label = ttk.Label(self.fps_frame, textvariable=self.var_fps, 
                                  style='Status.TLabel', font=('Segoe UI', 12, 'bold'))
        self.fps_label.pack(side=tk.RIGHT, padx=5)
    
    def create_animated_button(self, parent, text, command, color):
        """Create an animated button with hover effects"""
        button = tk.Button(parent, text=text, command=command,
                          bg=color, fg=self.colors['text_primary'],
                          font=('Segoe UI', 10, 'bold'),
                          relief='flat', borderwidth=0,
                          padx=15, pady=8,
                          cursor='hand2')
        
        # Add hover animations
        def on_enter(e):
            self.animate_button_hover(button, color, True)
        
        def on_leave(e):
            self.animate_button_hover(button, color, False)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def animate_button_hover(self, button, base_color, is_hover):
        """Animate button hover effect"""
        if is_hover:
            # Brighten color on hover
            rgb = self.hex_to_rgb(base_color)
            bright_rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
            bright_color = self.rgb_to_hex(bright_rgb)
            button.config(bg=bright_color)
        else:
            button.config(bg=base_color)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex color"""
        return '#%02x%02x%02x' % rgb
    
    def create_video_display(self, parent):
        """Create futuristic video display area"""
        # Create container for the futuristic video feed
        self.video_frame = ttk.LabelFrame(parent, text="🎥 NEURAL VISION SYSTEM", 
                                         style='Modern.TLabelframe', padding=15)
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize the futuristic video feed
        self.futuristic_video = FuturisticVideoFeed(self.video_frame, width=800, height=600)
        
        # Keep reference to old canvas for compatibility (if needed)
        self.video_canvas = self.futuristic_video.video_canvas
        self.video_container = self.futuristic_video.main_frame
        
        # Initialize canvas-related variables for compatibility
        self.current_canvas_width = 800
        self.current_canvas_height = 600
        self.canvas_image = None
        self.current_photo = None
        
        # Remove placeholder reference since futuristic feed handles it
        self.placeholder_text = None
        
    def on_canvas_click(self, event):
        """Handle canvas click event to create interactive effects"""
        if self.is_monitoring:
            # Create ripple effect at click position
            self.create_ripple_effect(event.x, event.y)
    
    def on_canvas_motion(self, event):
        """Handle mouse motion over canvas"""
        # No action required, but kept for future enhancements
        pass
    
    def create_ripple_effect(self, x, y):
        """Create animated ripple effect at the given coordinates"""
        try:
            # Create a new ripple
            ripple_id = f"ripple_{time.time()}"
            self.animate_ripple(ripple_id, x, y, 0)
        except Exception as e:
            logger.error(f"Error creating ripple effect: {e}")
    
    def animate_ripple(self, ripple_id, x, y, size):
        """Animate a ripple effect growing from center point"""
        try:
            max_size = 100
            if size <= max_size:
                # Remove old ripple
                self.video_canvas.delete(ripple_id)
                
                # Calculate opacity based on size
                alpha = 1.0 - (size / max_size)
                color = self.interpolate_color("#ffffff", self.colors['accent'], alpha)
                
                # Draw new ripple
                self.video_canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    outline=color, width=2, tags=ripple_id
                )
                
                # Schedule next animation frame
                self.root.after(30, self.animate_ripple, ripple_id, x, y, size + 5)
            else:
                # Remove ripple when animation completes
                self.video_canvas.delete(ripple_id)
        except Exception as e:
            logger.error(f"Error animating ripple: {e}")
    
    def on_canvas_resize(self, event):
        """Handle canvas resize event"""
        # Store the new canvas dimensions
        self.pending_canvas_width = event.width
        self.pending_canvas_height = event.height
        
        # Use a more efficient approach to debounce resize events
        if hasattr(self, 'resize_timer') and self.resize_timer is not None:
            self.root.after_cancel(self.resize_timer)
            
        # Schedule resize application with debouncing
        self.resize_timer = self.root.after(150, self.apply_pending_resize)
            
    def apply_pending_resize(self):
        """Apply pending canvas resize"""
        self.resize_timer = None
        
        # Only update if there's an actual frame to redisplay
        if hasattr(self, 'current_frame') and self.current_frame is not None and self.is_monitoring:
            # Force a frame refresh with new dimensions
            detection_results = getattr(self, 'detection_results', {})
            self.display_frame(self.current_frame, detection_results)
    
    def create_detection_indicators(self, parent):
        """Create status indicators for each detection type"""
        # Create container for indicators
        indicators_frame = tk.Frame(parent, bg=self.colors['secondary'])
        indicators_frame.pack(fill=tk.X, expand=True, pady=5)
        
        # Define detection types
        detection_types = [
            ("Drowsiness", "drowsiness"),
            ("Distraction", "distraction"),
            ("Attention", "attention"),
            ("Seatbelt", "seatbelt"),
            ("Hands", "hands"),
            ("Face ID", "face"),
            ("Emotion", "emotion")
        ]
        
        # Create indicator for each detection type
        self.detection_indicators = {}
        
        for i, (label_text, key) in enumerate(detection_types):
            # Create frame for each indicator
            frame = tk.Frame(indicators_frame, bg=self.colors['secondary'])
            frame.pack(side=tk.LEFT, expand=True, padx=5)
            
            # Create indicator circle
            indicator = tk.Canvas(frame, width=12, height=12, bg=self.colors['secondary'],
                                highlightthickness=0)
            indicator.pack(side=tk.LEFT)
            
            # Draw initial gray circle
            circle_id = indicator.create_oval(2, 2, 10, 10, fill="#808080", outline="")
            
            # Create label
            label = tk.Label(frame, text=label_text, bg=self.colors['secondary'],
                           fg=self.colors['text_primary'], font=('Segoe UI', 9))
            label.pack(side=tk.LEFT, padx=2)
            
            # Store references
            self.detection_indicators[key] = {
                'canvas': indicator,
                'circle_id': circle_id,
                'label': label,
                'status': False,
                'pulse': 0
            }
    
    def display_frame(self, frame, detection_results=None):
        """Display video frame using the futuristic video feed"""
        try:
            # Store detection results for other methods
            if detection_results:
                self.detection_results = detection_results
            
            # Use the futuristic video feed to display the frame
            if hasattr(self, 'futuristic_video'):
                self.futuristic_video.display_frame(frame, detection_results)
            
            # Update detection indicators (keep existing functionality)
            try:
                self.update_detection_indicators()
            except Exception as indicator_error:
                logger.error(f"Error updating indicators: {indicator_error}")
                
        except Exception as e:
            logger.error(f"Error displaying frame: {e}", exc_info=True)
                
    def apply_visual_effects(self, frame):
        """Apply visual effects and detection overlays to the frame"""
        try:
            # Create a copy to avoid modifying the original
            result = frame.copy()
            
            # Get frame dimensions
            height, width = result.shape[:2]
            
            # Apply detection overlays if results are available
            if hasattr(self, 'detection_results') and self.detection_results:
                # Draw detection outlines based on detection results
                if self.detection_results.get('drowsiness', False):
                    # Red outline for drowsiness
                    cv2.rectangle(result, (0, 0), (width, height), (0, 0, 255), 5)
                    cv2.putText(result, "DROWSINESS DETECTED!", (width//2-150, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                if self.detection_results.get('distraction', False):
                    # Orange overlay for distraction
                    cv2.rectangle(result, (0, 0), (width, height), (0, 165, 255), 5)
                    cv2.putText(result, "DISTRACTION DETECTED!", (width//2-150, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                
                # Add more detection visualizations here
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying visual effects: {e}")
            return frame
    
    def draw_detection_overlays(self, width, height):
        """Draw modern HD detection overlays with smooth animations"""
        try:
            # Clear previous overlays
            self.video_canvas.delete("detection_overlay")
            
            # Only draw if we have valid dimensions and detection results
            if width > 50 and height > 50 and hasattr(self, 'detection_results') and self.detection_results:
                # Draw modern corner indicators
                self.draw_modern_corner_indicators(width, height)
                
                # Draw detection status overlay
                self.draw_detection_status_overlay(width, height)
                
                # Draw scanning animation if monitoring
                if self.is_monitoring:
                    self.draw_smooth_scanning_animation(width, height)
                
        except Exception as e:
            logger.error(f"Error drawing detection overlays: {e}")
    
    def draw_modern_corner_indicators(self, width, height):
        """Draw modern HD corner indicators with smooth animations"""
        try:
            # Calculate responsive corner size based on video dimensions
            corner_size = min(40, width // 20, height // 15)
            margin = 20
            
            # Animated glow effect
            glow_intensity = 0.5 + 0.3 * math.sin(time.time() * 2)
            
            # Modern corner positions
            corners = [
                {"x": margin, "y": margin, "type": "tl"},
                {"x": width - margin - corner_size, "y": margin, "type": "tr"},
                {"x": margin, "y": height - margin - corner_size, "type": "bl"},
                {"x": width - margin - corner_size, "y": height - margin - corner_size, "type": "br"}
            ]
            
            for corner in corners:
                x, y = corner["x"], corner["y"]
                corner_type = corner["type"]
                
                # Base color with glow
                base_color = self.colors['accent']
                glow_color = self.interpolate_color(base_color, "#ffffff", glow_intensity * 0.5)
                
                # Draw modern L-shaped corners
                if corner_type == "tl":
                    # Top-left corner
                    self.video_canvas.create_line(
                        x, y + corner_size, x, y, x + corner_size, y,
                        fill=glow_color, width=3, capstyle="round", tags="detection_overlay"
                    )
                elif corner_type == "tr":
                    # Top-right corner
                    self.video_canvas.create_line(
                        x + corner_size, y + corner_size, x + corner_size, y, x, y,
                        fill=glow_color, width=3, capstyle="round", tags="detection_overlay"
                    )
                elif corner_type == "bl":
                    # Bottom-left corner
                    self.video_canvas.create_line(
                        x, y, x, y + corner_size, x + corner_size, y + corner_size,
                        fill=glow_color, width=3, capstyle="round", tags="detection_overlay"
                    )
                elif corner_type == "br":
                    # Bottom-right corner
                    self.video_canvas.create_line(
                        x, y + corner_size, x + corner_size, y + corner_size, x + corner_size, y,
                        fill=glow_color, width=3, capstyle="round", tags="detection_overlay"
                    )
                
                # Add subtle inner glow
                inner_size = corner_size // 2
                inner_offset = corner_size // 4
                inner_color = self.interpolate_color(base_color, "#ffffff", glow_intensity * 0.3)
                
                if corner_type == "tl":
                    self.video_canvas.create_line(
                        x + inner_offset, y + inner_offset + inner_size,
                        x + inner_offset, y + inner_offset,
                        x + inner_offset + inner_size, y + inner_offset,
                        fill=inner_color, width=1, tags="detection_overlay"
                    )
                # Similar for other corners...
                
        except Exception as e:
            logger.error(f"Error drawing modern corner indicators: {e}")
    
    def draw_detection_status_overlay(self, width, height):
        """Draw modern detection status overlay"""
        try:
            # Status bar at bottom
            status_height = 60
            status_y = height - status_height - 10
            
            if status_y > 20:
                # Modern status background with transparency effect
                self.video_canvas.create_rectangle(
                    20, status_y, width - 20, status_y + status_height,
                    fill=self.colors['secondary'], outline=self.colors['accent'],
                    width=1, tags="detection_overlay"
                )
                
                # Detection status indicators in a clean row
                indicator_width = (width - 80) // 7
                start_x = 40
                
                detection_states = [
                    ("DROWSINESS", self.detection_results.get('drowsiness', False)),
                    ("DISTRACTION", self.detection_results.get('distraction', False)),
                    ("ATTENTION", self.detection_results.get('attention', False)),
                    ("SEATBELT", self.detection_results.get('seatbelt', False)),
                    ("HANDS", self.detection_results.get('hand_position', False)),
                    ("FACE ID", self.detection_results.get('facial_recognition', False)),
                    ("EMOTION", self.detection_results.get('emotion', False))
                ]
                
                for i, (label, active) in enumerate(detection_states):
                    x = start_x + i * indicator_width
                    
                    # Modern indicator dot
                    dot_color = self.colors['success'] if active else "#888888"
                    if active:
                        # Pulsing effect for active indicators
                        pulse = 1 + 0.3 * math.sin(time.time() * 3 + i)
                        dot_size = 4 * pulse
                    else:
                        dot_size = 3
                    
                    self.video_canvas.create_oval(
                        x - dot_size, status_y + 15 - dot_size,
                        x + dot_size, status_y + 15 + dot_size,
                        fill=dot_color, outline="", tags="detection_overlay"
                    )
                    
                    # Label text
                    text_color = self.colors['text_primary'] if active else "#666666"
                    self.video_canvas.create_text(
                        x, status_y + 35,
                        text=label, fill=text_color,
                        font=("Segoe UI", 8, "bold"),
                        tags="detection_overlay"
                    )
                
        except Exception as e:
            logger.error(f"Error drawing detection status overlay: {e}")
    
    def draw_smooth_scanning_animation(self, width, height):
        """Draw smooth HD scanning animation"""
        try:
            # Initialize scan position if needed
            if not hasattr(self, 'scan_position'):
                self.scan_position = 0
                self.scan_direction = 1
                self.scan_speed = 2
            
            # Update scan position
            self.scan_position += self.scan_speed * self.scan_direction
            
            # Bounce at edges
            if self.scan_position >= height - 40:
                self.scan_direction = -1
            elif self.scan_position <= 40:
                self.scan_direction = 1
            
            # Draw main scanning beam
            beam_alpha = 0.7 + 0.3 * math.sin(time.time() * 4)
            beam_color = self.interpolate_color(self.colors['accent'], "#ffffff", beam_alpha)
            
            # Horizontal scanning line
            self.video_canvas.create_line(
                30, self.scan_position,
                width - 30, self.scan_position,
                fill=beam_color, width=2,
                tags="detection_overlay"
            )
            
            # Scanning trail effect
            for i in range(1, 6):
                trail_y = self.scan_position - (i * 5 * self.scan_direction)
                if 40 <= trail_y <= height - 40:
                    trail_alpha = beam_alpha * (1 - i * 0.15)
                    trail_color = self.interpolate_color(self.colors['accent'], self.colors['secondary'], trail_alpha)
                    self.video_canvas.create_line(
                        30 + i * 5, trail_y,
                        width - 30 - i * 5, trail_y,
                        fill=trail_color, width=max(1, 3 - i),
                        tags="detection_overlay"
                    )
            
            # Vertical scanning indicators
            v_scan_left = 60 + 20 * math.sin(time.time() * 1.5)
            v_scan_right = width - 60 - 20 * math.sin(time.time() * 1.5 + math.pi)
            
            for v_pos in [v_scan_left, v_scan_right]:
                if 40 <= v_pos <= width - 40:
                    self.video_canvas.create_line(
                        v_pos, 40,
                        v_pos, height - 40,
                        fill=beam_color, width=1,
                        dash=(8, 4), tags="detection_overlay"
                    )
                
        except Exception as e:
            logger.error(f"Error drawing smooth scanning animation: {e}")
    
    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two hex colors"""
        try:
            # Convert hex to RGB
            c1_rgb = self.hex_to_rgb(color1)
            c2_rgb = self.hex_to_rgb(color2)
            
            # Interpolate
            r = int(c1_rgb[0] + (c2_rgb[0] - c1_rgb[0]) * factor)
            g = int(c1_rgb[1] + (c2_rgb[1] - c1_rgb[1]) * factor)
            b = int(c1_rgb[2] + (c2_rgb[2] - c1_rgb[2]) * factor)
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color1
    
    def update_detection_indicators(self):
        """Update detection status indicators based on detection results"""
        try:
            if hasattr(self, 'detection_indicators') and hasattr(self, 'detection_results'):
                # Update indicators based on detection results
                for key, indicator in self.detection_indicators.items():
                    # Get detection status - handle different detection result keys
                    if key == 'hands':
                        is_active = self.detection_results.get('hand_position', False)
                    elif key == 'face':
                        is_active = self.detection_results.get('facial_recognition', False)
                    else:
                        is_active = self.detection_results.get(key, False)
                    
                    # Set color based on status
                    color = self.colors['success'] if is_active else "#808080"
                    
                    # Update indicator
                    indicator['canvas'].itemconfig(indicator['circle_id'], fill=color)
                    indicator['status'] = is_active
                    
                    # Pulse animation for active indicators
                    if is_active:
                        # Add pulse effect for active indicators
                        indicator['pulse'] = (indicator['pulse'] + 1) % 20
                        indicator['canvas'].itemconfig(
                            indicator['circle_id'],
                            outline=self.colors['success'],
                            width=1
                        )
                    else:
                        # No outline for inactive indicators
                        indicator['canvas'].itemconfig(
                            indicator['circle_id'],
                            outline="",
                            width=0
                        )
        except Exception as e:
            logger.error(f"Error updating detection indicators: {e}", exc_info=True)

    # Removed camera overlay drawing methods - no longer needed
    # def draw_holographic_border_effect(self):
    # def apply_visual_effects(self, frame):
    # def draw_stable_detection_overlays(self):
    # def draw_simple_scanning_lines(self, width, height):
    # def draw_simple_corner_brackets(self, width, height):
    # def draw_simple_crosshair(self, width, height):
    # All other drawing methods commented out...

    def draw_cyber_grid(self, width, height):
        """Draw animated cyber grid background"""
        try:
            grid_size = 40
            line_color = self.interpolate_color("#00ffff", "#0080ff", 
                                              abs(math.sin(self.cyber_grid_offset)))
            
            # Animate grid offset
            self.cyber_grid_offset += 0.02
            
            # Draw vertical lines
            for x in range(0, width, grid_size):
                offset_x = x + int(20 * math.sin(self.cyber_grid_offset + x * 0.01))
                self.video_canvas.create_line(
                    offset_x, 0, offset_x, height,
                    fill=line_color, width=1, tags="hud_overlay",
                    stipple="gray25"
                )
            
            # Draw horizontal lines
            for y in range(0, height, grid_size):
                offset_y = y + int(10 * math.cos(self.cyber_grid_offset + y * 0.01))
                self.video_canvas.create_line(
                    0, offset_y, width, offset_y,
                    fill=line_color, width=1, tags="hud_overlay",
                    stipple="gray25"
                )
                
        except Exception as e:
            logger.error(f"Error drawing cyber grid: {e}")

    def draw_scanning_lines(self, width, height):
        """Draw animated scanning lines with particle effects"""
        try:
            # Vertical scanning line
            scan_speed = 3
            self.scan_line_position += scan_speed * self.scan_line_direction
            
            if self.scan_line_position >= width:
                self.scan_line_direction = -1
                self.scan_line_position = width
            elif self.scan_line_position <= 0:
                self.scan_line_direction = 1
                self.scan_line_position = 0
            
            # Draw main scanning line with gradient effect
            for i in range(5):
                alpha = 1.0 - (i * 0.2)
                line_color = self.interpolate_color("#00ff00", "#ffffff", alpha)
                
                self.video_canvas.create_line(
                    self.scan_line_position - i * 2, 0,
                    self.scan_line_position - i * 2, height,
                    fill=line_color, width=max(1, 3-i), tags="hud_overlay"
                )
            
            # Horizontal scanning line
            h_scan_pos = int(height * (0.5 + 0.3 * math.sin(time.time() * 1.5)))
            self.video_canvas.create_line(
                0, h_scan_pos, width, h_scan_pos,
                fill="#ff00ff", width=2, tags="hud_overlay"
            )
            
            # Add scanning particles
            self.create_scan_particles(self.scan_line_position, h_scan_pos)
            
        except Exception as e:
            logger.error(f"Error drawing scanning lines: {e}")

    def draw_holographic_corners(self, width, height):
        """Draw animated holographic corner elements"""
        try:
            corner_size = 60
            glow_intensity = 0.5 + 0.5 * math.sin(time.time() * 2)
            
            # Define corner positions
            corners = [
                (20, 20, "tl"),          # Top-left
                (width - 80, 20, "tr"),   # Top-right
                (20, height - 80, "bl"),  # Bottom-left
                (width - 80, height - 80, "br")  # Bottom-right
            ]
            
            for x, y, corner_type in corners:
                # Main corner frame
                frame_color = self.interpolate_color("#00ffff", "#ffffff", glow_intensity)
                
                # Draw L-shaped corner brackets
                if corner_type in ["tl", "tr"]:
                    # Top corners
                    self.video_canvas.create_line(
                        x, y + corner_size, x, y, x + corner_size, y,
                        fill=frame_color, width=3, tags="hud_overlay"
                    )
                else:
                    # Bottom corners
                    self.video_canvas.create_line(
                        x, y, x, y + corner_size, x + corner_size, y + corner_size,
                        fill=frame_color, width=3, tags="hud_overlay"
                    )
                
                # Add pulsing inner lines
                pulse_offset = int(10 * math.sin(time.time() * 3))
                inner_color = self.interpolate_color("#ff0080", "#80ff00", glow_intensity)
                
                if corner_type == "tl":
                    self.video_canvas.create_line(
                        x + 5, y + 5 + pulse_offset, x + 5, y + 5, 
                        x + 5 + pulse_offset, y + 5,
                        fill=inner_color, width=2, tags="hud_overlay"
                    )
                elif corner_type == "tr":
                    self.video_canvas.create_line(
                        x + corner_size - 5, y + 5 + pulse_offset, 
                        x + corner_size - 5, y + 5, 
                        x + corner_size - 5 - pulse_offset, y + 5,
                        fill=inner_color, width=2, tags="hud_overlay"
                    )
                elif corner_type == "bl":
                    self.video_canvas.create_line(
                        x + 5, y + corner_size - 5 - pulse_offset, 
                        x + 5, y + corner_size - 5, 
                        x + 5 + pulse_offset, y + corner_size - 5,
                        fill=inner_color, width=2, tags="hud_overlay"
                    )
                elif corner_type == "br":
                    self.video_canvas.create_line(
                        x + corner_size - 5, y + corner_size - 5 - pulse_offset, 
                        x + corner_size - 5, y + corner_size - 5, 
                        x + corner_size - 5 - pulse_offset, y + corner_size - 5,
                        fill=inner_color, width=2, tags="hud_overlay"
                    )
                
                # Add holographic text labels
                self.draw_holographic_text(x, y, corner_type, glow_intensity)
                
        except Exception as e:
            logger.error(f"Error drawing holographic corners: {e}")

    def draw_neural_network_visualization(self, width, height):
        """Draw animated neural network nodes and connections"""
        try:
            # Initialize nodes if not exists
            if not hasattr(self, 'neural_nodes_initialized'):
                self.neural_network_nodes = []
                for i in range(12):
                    node = {
                        'x': width * 0.1 + (width * 0.8 * (i % 4) / 3),
                        'y': height * 0.2 + (height * 0.6 * (i // 4) / 2),
                        'size': 8 + (i % 3) * 3,
                        'pulse_phase': i * 0.5,
                        'active': False
                    }
                    self.neural_network_nodes.append(node)
                self.neural_nodes_initialized = True
            
            # Update and draw nodes
            for i, node in enumerate(self.neural_network_nodes):
                # Animate node activity
                node['pulse_phase'] += 0.1
                pulse_size = node['size'] + 3 * math.sin(node['pulse_phase'])
                
                # Randomly activate nodes
                if time.time() % 3 < 0.1:
                    node['active'] = not node['active']
                
                # Draw node
                color = "#00ff00" if node['active'] else "#0080ff"
                glow_color = "#ffffff" if node['active'] else "#40a0ff"
                
                # Outer glow
                self.video_canvas.create_oval(
                    node['x'] - pulse_size, node['y'] - pulse_size,
                    node['x'] + pulse_size, node['y'] + pulse_size,
                    outline=glow_color, width=1, fill="", tags="hud_overlay"
                )
                
                # Inner node (outline only, no fill)
                self.video_canvas.create_oval(
                    node['x'] - node['size'], node['y'] - node['size'],
                    node['x'] + node['size'], node['y'] + node['size'],
                    outline=color, width=2, fill="", tags="hud_overlay"
                )
                
                # Draw connections to nearby nodes
                for j, other_node in enumerate(self.neural_network_nodes):
                    if i != j:
                        distance = math.sqrt((node['x'] - other_node['x'])**2 + 
                                           (node['y'] - other_node['y'])**2)
                        if distance < 150:
                            connection_alpha = 1.0 - (distance / 150)
                            if node['active'] or other_node['active']:
                                connection_color = "#ffff00"
                            else:
                                connection_color = "#4080ff"
                            
                            self.video_canvas.create_line(
                                node['x'], node['y'], other_node['x'], other_node['y'],
                                fill=connection_color, width=int(connection_alpha * 2) + 1,
                                tags="hud_overlay", stipple="gray50"
                            )
                
        except Exception as e:
            logger.error(f"Error drawing neural network: {e}")

    def draw_biometric_scanners(self, width, height):
        """Draw animated biometric scanning elements"""
        try:
            # Face detection scanner
            face_center_x = width // 2
            face_center_y = height // 2
            scanner_radius = 80 + 20 * math.sin(time.time() * 2)
            
            # Draw scanning circle
            for i in range(3):
                radius = scanner_radius + i * 10
                alpha = 1.0 - (i * 0.3)
                color = self.interpolate_color("#ff0080", "#80ff00", alpha)
                
                self.video_canvas.create_oval(
                    face_center_x - radius, face_center_y - radius,
                    face_center_x + radius, face_center_y + radius,
                    outline=color, width=2, fill="", tags="hud_overlay"
                )
            
            # Draw crosshair
            crosshair_size = 30
            self.video_canvas.create_line(
                face_center_x - crosshair_size, face_center_y,
                face_center_x + crosshair_size, face_center_y,
                fill="#ff0000", width=2, tags="hud_overlay"
            )
            self.video_canvas.create_line(
                face_center_x, face_center_y - crosshair_size,
                face_center_x, face_center_y + crosshair_size,
                fill="#ff0000", width=2, tags="hud_overlay"
            )
            
            # Eye tracking indicators
            eye_positions = [
                (face_center_x - 40, face_center_y - 20),
                (face_center_x + 40, face_center_y - 20)
            ]
            
            for eye_x, eye_y in eye_positions:
                eye_pulse = 5 + 3 * math.sin(time.time() * 4)
                self.video_canvas.create_rectangle(
                    eye_x - eye_pulse, eye_y - eye_pulse,
                    eye_x + eye_pulse, eye_y + eye_pulse,
                    outline="#00ffff", width=2, fill="", tags="hud_overlay"
                )
                
        except Exception as e:
            logger.error(f"Error drawing biometric scanners: {e}")

    def draw_threat_assessment_display(self, width, height):
        """Draw animated threat level and status displays - outline only"""
        try:
            # Threat level indicator
            threat_x = width - 200
            threat_y = 50
            
            # Animated threat level bars (outline only)
            threat_level = 0.3 + 0.2 * math.sin(time.time() * 1.5)  # Simulated threat level
            
            for i in range(5):
                bar_y = threat_y + i * 15
                bar_width = 80 * (1 - i * 0.1)
                
                if i < threat_level * 5:
                    bar_color = "#ff0000" if i >= 3 else "#ffff00" if i >= 2 else "#00ff00"
                else:
                    bar_color = "#404040"
                
                # Draw outline only, no fill
                self.video_canvas.create_rectangle(
                    threat_x, bar_y, threat_x + bar_width, bar_y + 10,
                    outline=bar_color, width=2, fill="", tags="hud_overlay"
                )
            
            # Status text
            self.video_canvas.create_text(
                threat_x, threat_y - 20,
                text="THREAT ASSESSMENT",
                fill="#00ffff", font=("Courier", 10, "bold"),
                anchor="nw", tags="hud_overlay"
            )
            
            # Detection status indicators
            detection_types = [
                ("DROWSINESS", self.var_drowsiness.get()),
                ("DISTRACTION", self.var_distraction.get()),
                ("ATTENTION", self.var_attention.get()),
                ("SEATBELT", self.var_seatbelt.get())
            ]
            
            for i, (detection_type, active) in enumerate(detection_types):
                indicator_y = threat_y + 120 + i * 25
                status_color = "#00ff00" if active else "#ff0000"
                
                # Animated status dot (outline only)
                dot_size = 4 + 2 * math.sin(time.time() * 3 + i)
                self.video_canvas.create_oval(
                    threat_x - 15, indicator_y - dot_size,
                    threat_x - 15 + dot_size * 2, indicator_y + dot_size,
                    outline=status_color, width=2, fill="", tags="hud_overlay"
                )
                
                self.video_canvas.create_text(
                    threat_x, indicator_y,
                    text=detection_type,
                    fill=status_color, font=("Courier", 8, "bold"),
                    anchor="nw", tags="hud_overlay"
                )
                
        except Exception as e:
            logger.error(f"Error drawing threat assessment: {e}")

    def draw_matrix_rain_effect(self, width, height):
        """Draw matrix-style digital rain effect"""
        try:
            # Initialize rain drops if not exists
            if not hasattr(self, 'matrix_rain_initialized'):
                self.matrix_rain_drops = []
                for i in range(20):
                    drop = {
                        'x': (i * width // 20) + (width // 40),
                        'y': -50 - (i * 20),
                        'speed': 2 + (i % 3),
                        'chars': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'],
                        'trail_length': 10 + (i % 5)
                    }
                    self.matrix_rain_drops.append(drop)
                self.matrix_rain_initialized = True
            
            # Update and draw rain drops
            for drop in self.matrix_rain_drops:
                drop['y'] += drop['speed']
                
                # Reset drop when it goes off screen
                if drop['y'] > height + 50:
                    drop['y'] = -50
                    drop['x'] = (drop['x'] + 30) % width
                
                # Draw trail of characters
                for i in range(drop['trail_length']):
                    char_y = drop['y'] - i * 15
                    if char_y > -20 and char_y < height + 20:
                        alpha = 1.0 - (i / drop['trail_length'])
                        char_color = self.interpolate_color("#00ff00", "#004000", alpha)
                        
                        import random
                        char = random.choice(drop['chars'])
                        
                        self.video_canvas.create_text(
                            drop['x'], char_y,
                            text=char,
                            fill=char_color, font=("Courier", 8, "bold"),
                            tags="hud_overlay"
                        )
                        
        except Exception as e:
            logger.error(f"Error drawing matrix rain: {e}")

    def draw_quantum_particles(self, width, height):
        """Draw animated quantum particle effects"""
        try:
            # Initialize particles if not exists
            if not hasattr(self, 'quantum_particles_initialized'):
                self.quantum_particles = []
                for i in range(30):
                    particle = {
                        'x': width * 0.1 + (width * 0.8 * random.random()),
                        'y': height * 0.1 + (height * 0.8 * random.random()),
                        'vx': (random.random() - 0.5) * 2,
                        'vy': (random.random() - 0.5) * 2,
                        'size': 1 + random.random() * 3,
                        'life': 1.0,
                        'color_phase': random.random() * 2 * math.pi
                    }
                    self.quantum_particles.append(particle)
                self.quantum_particles_initialized = True
            
            # Update and draw particles
            for particle in self.quantum_particles:
                # Update position
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 0.01
                particle['color_phase'] += 0.1
                
                # Boundary bouncing
                if particle['x'] < 0 or particle['x'] > width:
                    particle['vx'] *= -1
                if particle['y'] < 0 or particle['y'] > height:
                    particle['vy'] *= -1
                
                # Reset particle if life is over
                if particle['life'] <= 0:
                    particle['x'] = width * 0.1 + (width * 0.8 * random.random())
                    particle['y'] = height * 0.1 + (height * 0.8 * random.random())
                    particle['life'] = 1.0
                
                # Draw particle with quantum effect
                if particle['life'] > 0:
                    # Color cycling
                    r = int(128 + 127 * math.sin(particle['color_phase']))
                    g = int(128 + 127 * math.sin(particle['color_phase'] + 2))
                    b = int(128 + 127 * math.sin(particle['color_phase'] + 4))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    size = particle['size'] * particle['life']
                    self.video_canvas.create_oval(
                        particle['x'] - size, particle['y'] - size,
                        particle['x'] + size, particle['y'] + size,
                        fill=color, outline=color, tags="hud_overlay"
                    )
                    
        except Exception as e:
            logger.error(f"Error drawing quantum particles: {e}")

    def draw_ai_analysis_overlay(self, width, height):
        """Draw AI analysis and data processing overlay - outline only"""
        try:
            # Analysis window
            analysis_x = 50
            analysis_y = height - 150
            window_width = 300
            window_height = 120
            
            # Draw analysis window background (outline only)
            self.video_canvas.create_rectangle(
                analysis_x, analysis_y, analysis_x + window_width, analysis_y + window_height,
                outline="#00ffff", width=2, fill="", tags="hud_overlay"
            )
            
            # Title
            self.video_canvas.create_text(
                analysis_x + 10, analysis_y + 10,
                text="AI NEURAL ANALYSIS",
                fill="#00ffff", font=("Courier", 10, "bold"),
                anchor="nw", tags="hud_overlay"
            )
            
            # Animated progress bars (outline only)
            progress_items = [
                ("FACIAL RECOGNITION", 0.85),
                ("EMOTION ANALYSIS", 0.72),
                ("ATTENTION LEVEL", 0.91),
                ("STRESS DETECTION", 0.63)
            ]
            
            for i, (item, progress) in enumerate(progress_items):
                bar_y = analysis_y + 30 + i * 20
                bar_width = 200
                
                # Background bar (outline only)
                self.video_canvas.create_rectangle(
                    analysis_x + 80, bar_y, analysis_x + 80 + bar_width, bar_y + 12,
                    outline="#404040", width=1, fill="", tags="hud_overlay"
                )
                
                # Progress bar with animation (outline only)
                animated_progress = progress + 0.1 * math.sin(time.time() * 2 + i)
                progress_width = int(bar_width * max(0, min(1, animated_progress)))
                
                progress_color = "#00ff00" if animated_progress > 0.8 else "#ffff00" if animated_progress > 0.6 else "#ff8000"
                
                if progress_width > 0:
                    self.video_canvas.create_rectangle(
                        analysis_x + 80, bar_y, analysis_x + 80 + progress_width, bar_y + 12,
                        outline=progress_color, width=2, fill="", tags="hud_overlay"
                    )
                
                # Label
                self.video_canvas.create_text(
                    analysis_x + 10, bar_y + 6,
                    text=item,
                    fill="#ffffff", font=("Courier", 8),
                    anchor="nw", tags="hud_overlay"
                )
                
        except Exception as e:
            logger.error(f"Error drawing AI analysis overlay: {e}")

    def draw_energy_pulse_rings(self, width, height):
        """Draw animated energy pulse rings"""
        try:
            # Initialize pulses if not exists
            if not hasattr(self, 'energy_pulses_initialized'):
                self.energy_pulses = []
                self.energy_pulses_initialized = True
            
            # Create new pulses occasionally
            if len(self.energy_pulses) < 3 and random.random() < 0.05:
                pulse = {
                    'x': width * 0.2 + (width * 0.6 * random.random()),
                    'y': height * 0.2 + (height * 0.6 * random.random()),
                    'radius': 0,
                    'max_radius': 50 + random.random() * 100,
                    'speed': 2 + random.random() * 3,
                    'color': random.choice(["#ff0080", "#00ff80", "#8000ff", "#ff8000"])
                }
                self.energy_pulses.append(pulse)
            
            # Update and draw pulses
            for pulse in self.energy_pulses[:]:
                pulse['radius'] += pulse['speed']
                
                if pulse['radius'] > pulse['max_radius']:
                    self.energy_pulses.remove(pulse)
                    continue
                
                # Draw pulse ring
                alpha = 1.0 - (pulse['radius'] / pulse['max_radius'])
                
                for i in range(3):
                    ring_radius = pulse['radius'] + i * 5
                    ring_alpha = alpha * (1 - i * 0.3)
                    
                    if ring_alpha > 0:
                        self.video_canvas.create_oval(
                            pulse['x'] - ring_radius, pulse['y'] - ring_radius,
                            pulse['x'] + ring_radius, pulse['y'] + ring_radius,
                            outline=pulse['color'], width=max(1, int(ring_alpha * 3)),
                            fill="", tags="hud_overlay"
                        )
                        
        except Exception as e:
            logger.error(f"Error drawing energy pulse rings: {e}")

    def draw_holographic_data_streams(self, width, height):
        """Draw animated holographic data streams"""
        try:
            # Initialize data streams if not exists
            if not hasattr(self, 'data_streams_initialized'):
                self.data_streams = []
                for i in range(5):
                    stream = {
                        'x': width * 0.1 + (width * 0.8 * i / 4),
                        'y': height + 50,
                        'target_y': height * 0.1 + (height * 0.8 * random.random()),
                        'speed': 3 + random.random() * 2,
                        'data': ['█', '▓', '▒', '░', '▄', '▀', '■', '□'],
                        'color': random.choice(["#00ffff", "#ff00ff", "#ffff00", "#00ff00"])
                    }
                    self.data_streams.append(stream)
                self.data_streams_initialized = True
            
            # Update and draw data streams
            for stream in self.data_streams:
                stream['y'] -= stream['speed']
                
                # Reset stream when it reaches target
                if stream['y'] < stream['target_y']:
                    stream['y'] = height + 50
                    stream['target_y'] = height * 0.1 + (height * 0.8 * random.random())
                
                # Draw data characters
                for i in range(10):
                    char_y = stream['y'] + i * 20
                    if char_y > 0 and char_y < height:
                        alpha = 1.0 - (i / 10)
                        char_color = self.interpolate_color(stream['color'], "#000000", alpha)
                        
                        char = random.choice(stream['data'])
                        self.video_canvas.create_text(
                            stream['x'], char_y,
                            text=char,
                            fill=char_color, font=("Courier", 12, "bold"),
                            tags="hud_overlay"
                        )
                        
        except Exception as e:
            logger.error(f"Error drawing holographic data streams: {e}")

    def draw_holographic_text(self, x, y, corner_type, intensity):
        """Draw holographic text labels for corners"""
        try:
            labels = {
                "tl": ["FACIAL", "RECOG"],
                "tr": ["EMOTION", "DETECT"],
                "bl": ["DROWSY", "ALERT"],
                "br": ["THREAT", "ASSESS"]
            }
            
            if corner_type in labels:
                for i, text in enumerate(labels[corner_type]):
                    text_color = self.interpolate_color("#00ffff", "#ffffff", intensity)
                    
                    # Add text with glow effect
                    text_x = x + 5 if corner_type.startswith('l') else x + 35
                    text_y = y + 70 + i * 15
                    
                    # Glow effect
                    for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        self.video_canvas.create_text(
                            text_x + offset[0], text_y + offset[1],
                            text=text,
                            fill="#004080", font=("Courier", 8, "bold"),
                            tags="hud_overlay"
                        )
                    
                    # Main text
                    self.video_canvas.create_text(
                        text_x, text_y,
                        text=text,
                        fill=text_color, font=("Courier", 8, "bold"),
                        tags="hud_overlay"
                    )
                    
        except Exception as e:
            logger.error(f"Error drawing holographic text: {e}")

    def create_scan_particles(self, x, y):
        """Create particle effects for scanning lines - outline only"""
        try:
            # Add scan particles to the scanning lines (outline only)
            for i in range(5):
                particle_x = x + random.randint(-10, 10)
                particle_y = y + random.randint(-10, 10)
                
                self.video_canvas.create_oval(
                    particle_x - 2, particle_y - 2,
                    particle_x + 2, particle_y + 2,
                    outline="#ffffff", width=1, fill="", tags="hud_overlay"
                )
                
        except Exception as e:
            logger.error(f"Error creating scan particles: {e}")

    def animate_border_glow(self):
        """Smoothly animate the border glow effect with stable timing"""
        try:
            # Use a smoother, slower animation
            self.border_glow_intensity += 0.02 * self.border_glow_direction

            if self.border_glow_intensity >= 1.0:
                self.border_glow_intensity = 1.0
                self.border_glow_direction = -1
            elif self.border_glow_intensity <= 0.2:  # Don't go to complete zero
                self.border_glow_intensity = 0.2
                self.border_glow_direction = 1

            # Update border color based on intensity with smoother transitions
            if hasattr(self, 'video_container'):
                base_color = self.colors['accent']
                rgb = self.hex_to_rgb(base_color)
                
                # Apply intensity smoothly
                adjusted_rgb = tuple(int(c * (0.3 + 0.7 * self.border_glow_intensity)) for c in rgb)
                adjusted_color = self.rgb_to_hex(adjusted_rgb)

                self.video_container.config(highlightbackground=adjusted_color)

            # Schedule next animation frame with stable timing
            self.root.after(100, self.animate_border_glow)  # Slower, more stable animation
            
        except Exception as e:
            logger.error(f"Error in border glow animation: {e}")
            # Retry after a longer delay if there's an error
            self.root.after(200, self.animate_border_glow)
    
    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors"""
        factor = max(0, min(1, factor))
        
        if color1.startswith('#'):
            r1, g1, b1 = self.hex_to_rgb(color1)
        else:
            return color1
            
        if color2.startswith('#'):
            r2, g2, b2 = self.hex_to_rgb(color2)
        else:
            return color2
        
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        return self.rgb_to_hex((r, g, b))
    
    def on_closing(self):
        """Handle the window close event gracefully"""
        if self.is_monitoring:
            self.stop_monitoring()
        
        # Make sure camera is released
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.release()
            
        self.root.destroy()
    
    def load_config(self):
        """Placeholder for loading configuration"""
        print("Load configuration functionality is not yet implemented.")
    
    def save_config(self):
        """Placeholder for saving configuration"""
        print("Save configuration functionality is not yet implemented.")
    
    def export_alert_log(self):
        """Placeholder for exporting alert log"""
        print("Export alert log functionality is not yet implemented.")
    
    def add_driver_face(self):
        """Placeholder for adding driver face"""
        print("Add driver face functionality is not yet implemented.")
    
    def calibrate_camera(self):
        """Placeholder for camera calibration"""
        print("Camera calibration functionality is not yet implemented.")
    
    def test_alerts(self):
        """Placeholder for testing alerts"""
        print("Test alerts functionality is not yet implemented.")
    
    def open_dashboard(self):
        """Placeholder for opening dashboard"""
        print("Dashboard functionality is not yet implemented.")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Driver Monitoring System v1.0\nAdvanced AI-powered driver safety monitoring")
    
    def show_help(self):
        """Show help dialog"""
        messagebox.showinfo("Help", "Driver Monitoring System Help\n\n1. Click 'Start Monitoring' to begin\n2. Configure detection settings in the left panel\n3. Monitor alerts in the right panel")
    
    def start_monitoring(self):
        """Start the monitoring system"""
        try:
            if not self.is_monitoring:
                self.monitoring_system = DriverMonitoringSystem()
                
                # Start the monitoring system (it will handle camera initialization)
                if self.monitoring_system.start():
                    self.is_monitoring = True
                    self.var_status.set("Monitoring Active")
                    self.status_indicator.config(foreground=self.colors['success'])
                    
                    # Start futuristic video feed monitoring mode
                    if hasattr(self, 'futuristic_video'):
                        self.futuristic_video.start_monitoring()
                    
                    # Start frame processing thread
                    self.start_frame_processing()
                    
                    print("Monitoring started successfully")
                else:
                    raise Exception("Failed to start monitoring system")
        except Exception as e:
            print(f"Error starting monitoring: {e}")
            # Use print instead of messagebox to avoid black box overlay
            print(f"Failed to start monitoring: {e}")
    
    def start_frame_processing(self):
        """Start frame processing in a separate thread"""
        try:
            # Start processing thread
            self.capture_thread = threading.Thread(target=self.process_frames, daemon=True)
            self.capture_thread.start()
            
            print("Frame processing started successfully")
            
        except Exception as e:
            print(f"Error starting frame processing: {e}")
            # Use print instead of messagebox to avoid black box overlay
            print(f"Failed to start frame processing: {e}")
    
    def process_frames(self):
        """Process frames from monitoring system in a loop"""
        last_frame_time = time.time()
        frame_count = 0
        min_frame_interval = 1.0/30.0  # Target 30 FPS for processing
        
        while self.is_monitoring and self.monitoring_system and self.monitoring_system.is_running:
            try:
                # Implement frame rate control for consistent timing
                current_time = time.time()
                elapsed = current_time - last_frame_time
                
                if elapsed < min_frame_interval:
                    # Sleep only the needed amount to maintain target framerate
                    time.sleep(min_frame_interval - elapsed)
                
                # Get processed frame and detection results from monitoring system
                try:
                    processed_frame, detection_results = self.monitoring_system.process_frame()
                except Exception as e:
                    print(f"Error getting frame from monitoring system: {e}")
                    processed_frame, detection_results = None, {}
                    
                last_frame_time = time.time()  # Update timing after processing
                
                if processed_frame is not None:
                    # Don't set frame_ready if another frame is still waiting to be displayed
                    # to avoid frame buildup and memory issues
                    if not self.frame_ready:
                        # Make a deep copy to avoid reference issues between threads
                        self.current_frame = processed_frame.copy()
                        self.frame_ready = True
                    
                    # Store detection results
                    if detection_results:
                        self.detection_results = detection_results
                        
                        # Update GUI with detection results
                        self.update_detection_display(detection_results)
                    
                    frame_count += 1
                else:
                    # No frame available, short sleep to avoid CPU spinning
                    time.sleep(0.03)
                    
            except Exception as e:
                logger.error(f"Error in frame processing: {e}", exc_info=True)
                # Longer sleep on error to allow recovery
                time.sleep(0.1)
    
    def update_detection_display(self, results):
        """Update the GUI with detection results"""
        try:
            # Update alert count
            active_alerts = results.get('active_alerts', [])
            self.var_alert_count.set(str(len(active_alerts)))
            
            # Update driver name if available
            if 'facial_recognition' in results:
                facial = results['facial_recognition']
                driver_name = facial.get('driver_name', 'Unknown')
                self.var_driver_name.set(driver_name)
            
            # Map detection types to indicator keys
            detection_mapping = {
                'drowsiness': 'drowsiness',
                'distraction': 'distraction',
                'attention': 'attention',
                'seatbelt': 'seatbelt',
                'hands': 'hands',
                'facial_recognition': 'face',
                'emotion': 'emotion'
            }
            
            # Update detection indicators
            for detection_type, indicator_key in detection_mapping.items():
                if detection_type in results:
                    # Handle different types of result structures
                    if isinstance(results[detection_type], dict):
                        value = results[detection_type].get('detected', False)
                    elif isinstance(results[detection_type], bool):
                        value = results[detection_type]
                    else:
                        value = bool(results[detection_type])
                    
                    # Update detection results
                    self.detection_results[indicator_key] = value
            
            # Update status on right panel if available
            if hasattr(self, 'update_status_panel'):
                self.update_status_panel(results)
            
        except Exception as e:
            logger.error(f"Error updating detection display: {e}")
    
    def start_camera_capture(self):
        """Legacy method - now replaced by monitoring system camera handling"""
        pass  # Camera is now handled by monitoring system
    
    def capture_frames(self):
        """Legacy method - now replaced by process_frames"""
        pass  # Frame processing is now handled by process_frames method
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        if self.is_monitoring:
            # Set flag first to stop processing loop
            self.is_monitoring = False
            
            # Stop futuristic video feed monitoring mode
            if hasattr(self, 'futuristic_video'):
                self.futuristic_video.stop_monitoring()
            
            # Stop camera
            if hasattr(self, 'camera') and self.camera is not None:
                self.camera.release()
                self.camera = None
            
            # Wait for capture thread to finish
            if hasattr(self, 'capture_thread') and self.capture_thread is not None:
                if self.capture_thread.is_alive():
                    self.capture_thread.join(timeout=1.0)  # Wait up to 1 second
                self.capture_thread = None
            
            # Stop monitoring system
            if self.monitoring_system:
                self.monitoring_system.stop() if hasattr(self.monitoring_system, 'stop') else None
                self.monitoring_system = None
                
            # Clear current frame
            self.current_frame = None
            self.frame_ready = False
            self.detection_results = {}
            
            # Reset display - properly cleanup resources
            if hasattr(self, 'video_canvas'):
                # Remove existing image to free memory
                if hasattr(self, 'canvas_image') and self.canvas_image:
                    self.video_canvas.delete(self.canvas_image)
                    self.canvas_image = None
                
                # Clear all other canvas items
                self.video_canvas.delete('all')
                
                # Show placeholder text again
                if hasattr(self, 'placeholder_text'):
                    self.placeholder_text.place(relx=0.5, rely=0.5, anchor='center')
                else:
                    # Create placeholder text if it doesn't exist
                    placeholder = tk.Label(self.video_canvas,
                                        text="Camera feed will appear here when monitoring starts",
                                        bg=self.colors['secondary'],
                                        fg=self.colors['text_primary'],
                                        font=('Segoe UI', 12))
                    placeholder.place(relx=0.5, rely=0.5, anchor='center')
                    self.placeholder_text = placeholder
            
            # Reset indicators
            if hasattr(self, 'detection_indicators'):
                for key, indicator in self.detection_indicators.items():
                    indicator['canvas'].itemconfig(indicator['circle_id'], fill="#808080", outline="")
                    indicator['status'] = False
                    if 'pulse' in indicator:
                        indicator['pulse'] = 0
            
            # Update status display
            self.var_status.set("Not Monitoring")
            self.status_indicator.config(foreground=self.colors['danger'])
            
            print("Monitoring stopped")
    
    def pause_monitoring(self):
        """Pause the monitoring system"""
        if self.is_monitoring:
            self.var_status.set("Paused")
            self.status_indicator.config(foreground=self.colors['warning'])
            print("Monitoring paused")
    
    def save_screenshot(self):
        """Save screenshot of current frame"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)
            print(f"Screenshot saved as {filename}")
        else:
            print("No frame available for screenshot")
    
    def toggle_recording(self):
        """Toggle video recording"""
        print("Recording functionality is not yet implemented.")
    
    def create_detection_panel(self, parent):
        """Create detection settings panel"""
        detection_frame = ttk.LabelFrame(parent, text="⚙️ Detection Settings", 
                                       style='Modern.TLabelframe', padding=15)
        detection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Detection options
        options = [
            ("😴 Drowsiness Detection", self.var_drowsiness),
            ("👀 Distraction Detection", self.var_distraction),
            ("🔗 Seatbelt Detection", self.var_seatbelt),
            ("🎯 Attention Detection", self.var_attention),
            ("✋ Hand Position Detection", self.var_hand_position),
            ("👤 Facial Recognition", self.var_facial_recognition),
            ("😊 Emotion Detection", self.var_emotion)
        ]
        
        for text, var in options:
            cb = ttk.Checkbutton(detection_frame, text=text, variable=var, 
                               style='Modern.TCheckbutton')
            cb.pack(anchor=tk.W, pady=5)
    
    def create_status_panel(self, parent):
        """Create status panel"""
        # Driver info frame
        driver_frame = ttk.LabelFrame(parent, text="👤 Driver Information", 
                                    style='Modern.TLabelframe', padding=15)
        driver_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(driver_frame, text="Driver:", style='Modern.TLabel').pack(anchor=tk.W)
        ttk.Label(driver_frame, textvariable=self.var_driver_name, 
                 style='Modern.TLabel').pack(anchor=tk.W, padx=(10, 0))
        
        # Alert count
        ttk.Label(driver_frame, text="Active Alerts:", style='Modern.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.alert_count_label = ttk.Label(driver_frame, textvariable=self.var_alert_count, 
                                         style='Alert.TLabel')
        self.alert_count_label.pack(anchor=tk.W, padx=(10, 0))
    
    def create_alert_panel(self):
        """Create alert panel (placeholder)"""
        pass
    
    def animate_interface(self):
        """Animate the interface elements"""
        self.animation_time += 0.1
        
        # Update pulse animation for status indicator
        if hasattr(self, 'status_indicator'):
            pulse_scale = 1.0 + 0.1 * math.sin(self.animation_time * 2)
            # Note: Tkinter doesn't support scaling directly, so we'll just change the text
        
        # Schedule next animation frame
        self.root.after(50, self.animate_interface)
    
    def animate_status_indicators(self):
        """Animate status indicators"""
        # Simple color cycling for status indicators
        if hasattr(self, 'status_indicator'):
            if self.is_monitoring:
                # Cycle through green shades when monitoring
                intensity = 0.5 + 0.5 * math.sin(time.time() * 2)
                green_val = int(76 + (155 - 76) * intensity)  # Vary green component
                color = f"#{76:02x}{green_val:02x}{80:02x}"
                self.status_indicator.config(foreground=color)
        
        # Schedule next animation frame
        self.root.after(100, self.animate_status_indicators)
    
    # Removed show_camera_placeholder method - no longer needed

    def update_gui(self):
        """Main GUI update loop"""
        try:
            # Calculate actual FPS
            current_time = time.time()
            if not hasattr(self, 'last_fps_time'):
                self.last_fps_time = current_time
                self.frame_count_since_last = 0
            
            # Update FPS display every second
            if current_time - self.last_fps_time >= 1.0:
                if self.is_monitoring:
                    # Calculate real FPS based on processed frames
                    fps = self.frame_count_since_last
                    self.var_fps.set(f"{fps} FPS")
                    
                    # Reset counters
                    self.last_fps_time = current_time
                    self.frame_count_since_last = 0
                else:
                    self.var_fps.set("0 FPS")
            
            # If we have a new frame ready, display it
            if self.current_frame is not None and self.frame_ready:
                detection_results = getattr(self, 'detection_results', {})
                self.display_frame(self.current_frame, detection_results)
                self.frame_ready = False
                self.frame_count_since_last += 1
            
        except Exception as e:
            logger.error(f"Error in GUI update: {e}", exc_info=True)
        
        # Schedule next update with more consistent timing
        self.root.after(16, self.update_gui)  # ~60 FPS update rate for smoother UI
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

def main():
    """Main function to run the advanced animated GUI"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting Advanced Animated Driver Monitoring System")
    
    # Create and run GUI
    try:
        app = DriverMonitoringGUI()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start GUI: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
