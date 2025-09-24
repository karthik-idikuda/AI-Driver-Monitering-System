"""
Futuristic Video Feed Component
Modern, high-tech video display with advanced animations and detection overlays
"""

import cv2
import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import time
import math
import threading
import logging
import random

logger = logging.getLogger(__name__)

class FuturisticVideoFeed:
    def __init__(self, parent, width=800, height=600):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Animation variables
        self.animation_time = 0
        self.scan_position = 0
        self.scan_direction = 1
        self.grid_offset = 0
        self.particle_systems = []
        self.glow_intensity = 0
        self.hud_elements = {}
        
        # Detection states
        self.detection_results = {}
        self.alert_states = {}
        self.is_monitoring = False
        
        # Colors - Modern futuristic theme
        self.colors = {
            'primary': '#00F5FF',      # Cyan
            'secondary': '#0080FF',    # Blue
            'accent': '#00FFAA',       # Green
            'warning': '#FFD700',      # Gold
            'danger': '#FF4444',       # Red
            'success': '#00FF88',      # Bright Green
            'background': '#0A0A0A',   # Dark
            'surface': '#1A1A1A',      # Dark surface
            'text': '#FFFFFF',         # White text
            'glow': '#88FFFF'          # Glow effect
        }
        
        self.setup_ui()
        self.init_animations()
        
    def setup_ui(self):
        """Setup the futuristic video feed UI"""
        # Main container with gradient background
        self.main_frame = tk.Frame(
            self.parent,
            bg=self.colors['background'],
            relief=tk.RIDGE,
            bd=2
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Video canvas with enhanced styling
        self.video_canvas = tk.Canvas(
            self.main_frame,
            width=self.width,
            height=self.height,
            bg=self.colors['background'],
            highlightthickness=3,
            highlightbackground=self.colors['primary'],
            highlightcolor=self.colors['accent']
        )
        self.video_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar at bottom
        self.create_status_bar()
        
        # Initialize placeholder
        self.create_placeholder()
        
    def create_status_bar(self):
        """Create futuristic status bar"""
        self.status_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['surface'],
            height=60
        )
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        self.status_frame.pack_propagate(False)
        
        # Detection status indicators
        self.detection_indicators = {}
        indicators = [
            ('DROWSINESS', 'danger'),
            ('DISTRACTION', 'warning'),
            ('ATTENTION', 'primary'),
            ('SEATBELT', 'success'),
            ('HANDS', 'accent'),
            ('FACE_ID', 'secondary'),
            ('EMOTION', 'glow')
        ]
        
        for i, (name, color_key) in enumerate(indicators):
            frame = tk.Frame(self.status_frame, bg=self.colors['surface'])
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
            
            # LED-style indicator
            indicator_canvas = tk.Canvas(
                frame,
                width=40,
                height=40,
                bg=self.colors['surface'],
                highlightthickness=0
            )
            indicator_canvas.pack(pady=5)
            
            # Create glowing dot
            dot_id = indicator_canvas.create_oval(
                12, 12, 28, 28,
                fill='#333333',
                outline=self.colors[color_key],
                width=1
            )
            
            # Label
            label = tk.Label(
                frame,
                text=name.replace('_', ' '),
                font=('Consolas', 8, 'bold'),
                fg=self.colors['text'],
                bg=self.colors['surface']
            )
            label.pack()
            
            self.detection_indicators[name.lower()] = {
                'canvas': indicator_canvas,
                'dot_id': dot_id,
                'color': self.colors[color_key],
                'active': False,
                'pulse_phase': i * 0.5
            }
    
    def create_placeholder(self):
        """Create futuristic placeholder when no video"""
        self.placeholder_items = []
        
        # Center message
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Animated loading ring
        self.loading_ring = self.video_canvas.create_oval(
            center_x - 50, center_y - 50,
            center_x + 50, center_y + 50,
            outline=self.colors['primary'],
            width=3,
            tags='placeholder'
        )
        
        # Text
        self.placeholder_text = self.video_canvas.create_text(
            center_x, center_y + 80,
            text="INITIALIZING NEURAL VISION SYSTEM...",
            fill=self.colors['text'],
            font=('Consolas', 14, 'bold'),
            tags='placeholder'
        )
        
        # Scanning lines
        for i in range(5):
            line = self.video_canvas.create_line(
                center_x - 100, center_y - 30 + i * 15,
                center_x + 100, center_y - 30 + i * 15,
                fill=self.colors['accent'],
                width=1,
                tags='placeholder'
            )
            self.placeholder_items.append(line)
    
    def init_animations(self):
        """Initialize animation system"""
        self.animation_running = True
        self.animation_thread = threading.Thread(target=self.animation_loop, daemon=True)
        self.animation_thread.start()
    
    def animation_loop(self):
        """Main animation loop"""
        while self.animation_running:
            try:
                self.animation_time += 0.05
                self.update_animations()
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                logger.error(f"Animation error: {e}")
    
    def update_animations(self):
        """Update all animations"""
        try:
            # Update placeholder animations
            if hasattr(self, 'loading_ring'):
                # Rotate loading ring
                angle = self.animation_time * 2
                self.animate_loading_ring(angle)
            
            # Update scanning lines
            self.animate_scanning_lines()
            
            # Update detection indicators
            self.animate_detection_indicators()
            
            # Update HUD elements if monitoring
            if self.is_monitoring:
                self.update_hud_overlays()
                
        except Exception as e:
            logger.error(f"Animation update error: {e}")
    
    def animate_loading_ring(self, angle):
        """Animate the loading ring"""
        try:
            # Create gradient effect by drawing multiple arcs
            center_x = self.width // 2
            center_y = self.height // 2
            
            # Clear previous ring
            self.video_canvas.delete('loading_ring')
            
            # Draw gradient ring segments
            for i in range(8):
                start_angle = angle + i * 45
                extent = 30
                alpha = 1.0 - (i * 0.1)
                
                # Calculate color with alpha
                color = self.interpolate_color(
                    self.colors['primary'], 
                    self.colors['background'], 
                    1 - alpha
                )
                
                if alpha > 0.1:
                    self.video_canvas.create_arc(
                        center_x - 50, center_y - 50,
                        center_x + 50, center_y + 50,
                        start=start_angle,
                        extent=extent,
                        outline=color,
                        width=3,
                        style='arc',
                        tags='loading_ring'
                    )
        except Exception as e:
            logger.error(f"Loading ring animation error: {e}")
    
    def animate_scanning_lines(self):
        """Animate scanning lines in placeholder"""
        try:
            if hasattr(self, 'placeholder_items'):
                for i, line_id in enumerate(self.placeholder_items):
                    # Pulsing effect
                    pulse = 0.5 + 0.5 * math.sin(self.animation_time * 3 + i * 0.5)
                    color = self.interpolate_color(
                        self.colors['accent'],
                        self.colors['background'],
                        1 - pulse
                    )
                    self.video_canvas.itemconfig(line_id, fill=color)
        except Exception as e:
            logger.error(f"Scanning lines animation error: {e}")
    
    def animate_detection_indicators(self):
        """Animate detection status indicators"""
        try:
            for name, indicator in self.detection_indicators.items():
                phase = self.animation_time * 4 + indicator['pulse_phase']
                
                if indicator['active']:
                    # Pulsing glow effect for active indicators
                    intensity = 0.7 + 0.3 * math.sin(phase)
                    glow_color = self.interpolate_color(
                        indicator['color'],
                        '#FFFFFF',
                        intensity * 0.3
                    )
                    
                    # Update dot with glow
                    indicator['canvas'].itemconfig(
                        indicator['dot_id'],
                        fill=indicator['color'],
                        outline=glow_color,
                        width=2
                    )
                    
                    # Create glow effect
                    if intensity > 0.8:
                        # Add outer glow ring
                        glow_ring = indicator['canvas'].create_oval(
                            8, 8, 32, 32,
                            outline=glow_color,
                            width=1,
                            tags='glow'
                        )
                        # Remove after short time
                        indicator['canvas'].after(50, lambda: indicator['canvas'].delete('glow'))
                else:
                    # Dim indicator
                    indicator['canvas'].itemconfig(
                        indicator['dot_id'],
                        fill='#333333',
                        outline='#666666',
                        width=1
                    )
        except Exception as e:
            logger.error(f"Detection indicators animation error: {e}")
    
    def display_frame(self, frame, detection_results=None):
        """Display video frame with futuristic overlays"""
        try:
            # Update detection results
            if detection_results:
                self.detection_results = detection_results
                self.update_detection_states()
            
            # Hide placeholder when video starts
            self.video_canvas.delete('placeholder')
            self.video_canvas.delete('loading_ring')
            
            if frame is not None:
                # Get canvas dimensions
                canvas_width = self.video_canvas.winfo_width()
                canvas_height = self.video_canvas.winfo_height()
                
                # Use default dimensions if canvas not ready
                if canvas_width <= 1:
                    canvas_width = self.width
                if canvas_height <= 1:
                    canvas_height = self.height
                
                # Ensure minimum size to prevent shrinking
                display_width = max(canvas_width - 40, 640)  # Minimum 640px width
                display_height = max(canvas_height - 40, 480)  # Minimum 480px height
                
                # Apply futuristic frame processing
                processed_frame = self.process_frame_futuristic(frame)
                
                # Resize frame maintaining aspect ratio
                frame_height, frame_width = processed_frame.shape[:2]
                aspect_ratio = frame_width / frame_height
                
                # Calculate new dimensions preserving aspect ratio
                if display_width / aspect_ratio <= display_height:
                    new_width = display_width
                    new_height = int(display_width / aspect_ratio)
                else:
                    new_height = display_height
                    new_width = int(display_height * aspect_ratio)
                
                # Ensure minimum dimensions
                new_width = max(new_width, 640)
                new_height = max(new_height, 480)
                
                # Resize the frame
                resized_frame = cv2.resize(processed_frame, (new_width, new_height))
                
                # Convert to RGB for display
                display_frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(display_frame_rgb)
                self.current_photo = ImageTk.PhotoImage(image=img)
                
                # Center the image on canvas
                x_pos = canvas_width // 2
                y_pos = canvas_height // 2
                
                # Update or create image
                if hasattr(self, 'canvas_image'):
                    self.video_canvas.itemconfig(self.canvas_image, image=self.current_photo)
                    self.video_canvas.coords(self.canvas_image, x_pos, y_pos)
                else:
                    # Clear canvas first
                    self.video_canvas.delete("all")
                    self.canvas_image = self.video_canvas.create_image(
                        x_pos, y_pos, anchor='center', image=self.current_photo
                    )
                
                # Draw futuristic overlays with proper dimensions
                self.draw_futuristic_overlays(canvas_width, canvas_height, new_width, new_height)
                
        except Exception as e:
            logger.error(f"Error displaying frame: {e}")
            import traceback
            traceback.print_exc()
    
    def process_frame_futuristic(self, frame):
        """Apply futuristic image processing effects"""
        try:
            result = frame.copy()
            
            # Apply subtle blue tint for sci-fi look
            blue_tint = np.zeros_like(result)
            blue_tint[:, :] = [20, 5, 0]  # Subtle blue tint
            result = cv2.addWeighted(result, 0.95, blue_tint, 0.05, 0)
            
            # Enhance contrast slightly
            result = cv2.convertScaleAbs(result, alpha=1.05, beta=5)
            
            # Add edge enhancement for digital look
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            edges_colored = cv2.applyColorMap(edges_colored, cv2.COLORMAP_WINTER)
            
            # Blend edges subtly
            result = cv2.addWeighted(result, 0.97, edges_colored, 0.03, 0)
            
            return result
            
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return frame
    
    def draw_futuristic_overlays(self, canvas_width, canvas_height, video_width, video_height):
        """Draw all futuristic overlays with proper scaling"""
        try:
            # Clear previous overlays
            self.hud_canvas.delete("all")
            
            # Calculate video position on canvas
            video_x_start = (canvas_width - video_width) // 2
            video_y_start = (canvas_height - video_height) // 2
            video_x_end = video_x_start + video_width
            video_y_end = video_y_start + video_height
            
            # Set overlay bounds to video area only
            overlay_bounds = {
                'x_start': video_x_start,
                'y_start': video_y_start,
                'x_end': video_x_end,
                'y_end': video_y_end,
                'width': video_width,
                'height': video_height
            }
            
            # Update animations
            current_time = time.time()
            self.animation_phase = (current_time - self.animation_start_time) % (2 * math.pi)
            
            # Draw overlays in order
            self.draw_hud_frame(overlay_bounds)
            self.draw_detection_hud(overlay_bounds)
            self.draw_particle_system(overlay_bounds)
            self.draw_scanning_animation(overlay_bounds)
            self.draw_holographic_overlay(overlay_bounds)
            
        except Exception as e:
            logger.error(f"Error drawing futuristic overlays: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_hud_frame(self, bounds):
        """Draw the main HUD frame with HD quality"""
        try:
            x_start, y_start = bounds['x_start'], bounds['y_start']
            x_end, y_end = bounds['x_end'], bounds['y_end']
            width, height = bounds['width'], bounds['height']
            
            # Main HUD border with glow effect
            border_color = "#00ffff" if self.system_active else "#404040"
            glow_color = "#004080"
            
            # Draw multiple border layers for glow effect
            for i in range(3):
                offset = i * 2
                alpha = 100 - i * 30
                color = f"#{hex(alpha)[2:].zfill(2)}80ff"
                
                self.hud_canvas.create_rectangle(
                    x_start + offset, y_start + offset,
                    x_end - offset, y_end - offset,
                    outline=border_color, width=2-i, tags="hud_overlay"
                )
            
            # Corner indicators
            corner_size = min(width, height) // 15
            corners = [
                (x_start, y_start),  # Top-left
                (x_end - corner_size, y_start),  # Top-right
                (x_start, y_end - corner_size),  # Bottom-left
                (x_end - corner_size, y_end - corner_size)  # Bottom-right
            ]
            
            for i, (x, y) in enumerate(corners):
                # Animated corner brackets
                alpha = int(127 + 127 * math.sin(self.animation_phase + i * math.pi/2))
                color_intensity = hex(alpha)[2:].zfill(2)
                
                if i == 0:  # Top-left
                    self.hud_canvas.create_line(x, y + corner_size, x, y, x + corner_size, y,
                                               fill=f"#{color_intensity}ff{color_intensity}", width=3, tags="hud_overlay")
                elif i == 1:  # Top-right
                    self.hud_canvas.create_line(x, y, x + corner_size, y, x + corner_size, y + corner_size,
                                               fill=f"#{color_intensity}ff{color_intensity}", width=3, tags="hud_overlay")
                elif i == 2:  # Bottom-left
                    self.hud_canvas.create_line(x, y, x, y + corner_size, x + corner_size, y + corner_size,
                                               fill=f"#{color_intensity}ff{color_intensity}", width=3, tags="hud_overlay")
                else:  # Bottom-right
                    self.hud_canvas.create_line(x + corner_size, y, x + corner_size, y + corner_size, x, y + corner_size,
                                               fill=f"#{color_intensity}ff{color_intensity}", width=3, tags="hud_overlay")
            
        except Exception as e:
            logger.error(f"Error drawing HUD frame: {e}")

    def draw_detection_hud(self, bounds):
        """Draw advanced detection overlays with HD quality"""
        try:
            x_start, y_start = bounds['x_start'], bounds['y_start']
            width, height = bounds['width'], bounds['height']
            
            # Detection status panel
            panel_x = x_start + 20
            panel_y = y_start + 20
            panel_width = 200
            panel_height = 150
            
            # Semi-transparent background
            self.hud_canvas.create_rectangle(
                panel_x, panel_y, panel_x + panel_width, panel_y + panel_height,
                fill="#000000", stipple="gray50", outline="#00ffff", width=2, tags="hud_overlay"
            )
            
            # Title
            self.hud_canvas.create_text(
                panel_x + panel_width//2, panel_y + 15,
                text="DETECTION STATUS", fill="#00ffff", font=("Orbitron", 10, "bold"),
                tags="hud_overlay"
            )
            
            # Detection indicators
            detections = [
                ("DROWSINESS", self.detection_results.get('drowsiness', 0) > 0.7),
                ("DISTRACTION", self.detection_results.get('distraction', 0) > 0.7),
                ("SEATBELT", not self.detection_results.get('seatbelt', True)),
                ("HANDS", self.detection_results.get('hands_off_wheel', False)),
                ("EMOTION", self.detection_results.get('emotion', '') in ['angry', 'sad'])
            ]
            
            for i, (name, active) in enumerate(detections):
                y_pos = panel_y + 35 + i * 20
                color = "#ff4444" if active else "#44ff44"
                status = "ALERT" if active else "OK"
                
                # Status indicator light
                self.hud_canvas.create_oval(
                    panel_x + 10, y_pos - 5, panel_x + 20, y_pos + 5,
                    fill=color, outline=color, tags="hud_overlay"
                )
                
                # Detection name and status
                self.hud_canvas.create_text(
                    panel_x + 30, y_pos, text=f"{name}: {status}",
                    fill=color, font=("Courier", 8), anchor="w", tags="hud_overlay"
                )
            
        except Exception as e:
            logger.error(f"Error drawing detection HUD: {e}")

    def draw_particle_system(self, bounds):
        """Draw animated particle effects"""
        try:
            if not hasattr(self, 'particles'):
                self.particles = []
                # Initialize particles
                for _ in range(20):
                    self.particles.append({
                        'x': random.randint(bounds['x_start'], bounds['x_end']),
                        'y': random.randint(bounds['y_start'], bounds['y_end']),
                        'vx': random.uniform(-2, 2),
                        'vy': random.uniform(-2, 2),
                        'life': random.uniform(0.5, 2.0),
                        'max_life': random.uniform(0.5, 2.0)
                    })
            
            # Update and draw particles
            for particle in self.particles[:]:
                # Update position
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 0.02
                
                # Remove dead particles
                if particle['life'] <= 0:
                    self.particles.remove(particle)
                    # Add new particle
                    self.particles.append({
                        'x': random.randint(bounds['x_start'], bounds['x_end']),
                        'y': random.randint(bounds['y_start'], bounds['y_end']),
                        'vx': random.uniform(-2, 2),
                        'vy': random.uniform(-2, 2),
                        'life': random.uniform(0.5, 2.0),
                        'max_life': random.uniform(0.5, 2.0)
                    })
                    continue
                
                # Keep particles within bounds
                if particle['x'] < bounds['x_start'] or particle['x'] > bounds['x_end']:
                    particle['vx'] *= -1
                if particle['y'] < bounds['y_start'] or particle['y'] > bounds['y_end']:
                    particle['vy'] *= -1
                
                # Draw particle with alpha based on life
                alpha = int(255 * (particle['life'] / particle['max_life']))
                alpha_hex = hex(alpha)[2:].zfill(2)
                
                self.hud_canvas.create_oval(
                    particle['x'] - 2, particle['y'] - 2,
                    particle['x'] + 2, particle['y'] + 2,
                    fill=f"#{alpha_hex}ff{alpha_hex}", outline="", tags="hud_overlay"
                )
            
        except Exception as e:
            logger.error(f"Error drawing particle system: {e}")

    def draw_scanning_animation(self, bounds):
        """Draw scanning line animation"""
        try:
            x_start, y_start = bounds['x_start'], bounds['y_start']
            x_end, y_end = bounds['x_end'], bounds['y_end']
            width, height = bounds['width'], bounds['height']
            
            # Vertical scanning line
            scan_progress = (math.sin(self.animation_phase) + 1) / 2
            scan_x = x_start + width * scan_progress
            
            # Draw scanning line with gradient effect
            for i in range(5):
                alpha = 255 - i * 40
                alpha_hex = hex(alpha)[2:].zfill(2)
                
                self.hud_canvas.create_line(
                    scan_x - i, y_start, scan_x - i, y_end,
                    fill=f"#{alpha_hex}ff{alpha_hex}", width=1, tags="hud_overlay"
                )
            
            # Horizontal scanning grid
            grid_spacing = 40
            for y in range(y_start, y_end, grid_spacing):
                alpha = int(64 + 64 * math.sin(self.animation_phase + y/100))
                alpha_hex = hex(alpha)[2:].zfill(2)
                
                self.hud_canvas.create_line(
                    x_start, y, x_end, y,
                    fill=f"#{alpha_hex}80{alpha_hex}", width=1, tags="hud_overlay"
                )
            
        except Exception as e:
            logger.error(f"Error drawing scanning animation: {e}")

    def draw_holographic_overlay(self, bounds):
        """Draw holographic effects and data overlays"""
        try:
            x_start, y_start = bounds['x_start'], bounds['y_start']
            x_end, y_end = bounds['x_end'], bounds['y_end']
            width, height = bounds['width'], bounds['height']
            
            # Holographic data streams
            stream_count = 8
            for i in range(stream_count):
                angle = (self.animation_phase + i * math.pi / 4) % (2 * math.pi)
                radius = min(width, height) * 0.3
                
                center_x = x_start + width // 2
                center_y = y_start + height // 2
                
                start_x = center_x + radius * math.cos(angle)
                start_y = center_y + radius * math.sin(angle)
                
                end_x = center_x + (radius + 50) * math.cos(angle)
                end_y = center_y + (radius + 50) * math.sin(angle)
                
                # Only draw if within bounds
                if (x_start <= end_x <= x_end and y_start <= end_y <= y_end):
                    alpha = int(127 + 127 * math.sin(angle + self.animation_phase))
                    alpha_hex = hex(alpha)[2:].zfill(2)
                    
                    self.hud_canvas.create_line(
                        start_x, start_y, end_x, end_y,
                        fill=f"#{alpha_hex}ff{alpha_hex}", width=2, tags="hud_overlay"
                    )
                    
                    # Data point at end
                    self.hud_canvas.create_oval(
                        end_x - 3, end_y - 3, end_x + 3, end_y + 3,
                        fill=f"#ff{alpha_hex}ff", outline="", tags="hud_overlay"
                    )
            
            # Performance metrics
            metrics_x = x_end - 150
            metrics_y = y_start + 20
            
            self.hud_canvas.create_text(
                metrics_x, metrics_y, text="SYSTEM METRICS",
                fill="#00ffff", font=("Orbitron", 9, "bold"), anchor="nw", tags="hud_overlay"
            )
            
            fps = getattr(self, 'fps', 30)
            cpu_usage = random.randint(20, 60)  # Simulated
            
            metrics = [
                f"FPS: {fps:.1f}",
                f"CPU: {cpu_usage}%",
                f"STATUS: {'ACTIVE' if self.system_active else 'STANDBY'}"
            ]
            
            for i, metric in enumerate(metrics):
                self.hud_canvas.create_text(
                    metrics_x, metrics_y + 20 + i * 15, text=metric,
                    fill="#44ff44", font=("Courier", 8), anchor="nw", tags="hud_overlay"
                )
            
        except Exception as e:
            logger.error(f"Error drawing holographic overlay: {e}")
        """Draw animated corner brackets"""
        try:
            bracket_size = min(50, width // 16, height // 12)
            margin = 20
            
            # Animated glow intensity
            glow = 0.5 + 0.5 * math.sin(self.animation_time * 2)
            color = self.interpolate_color(self.colors['primary'], '#FFFFFF', glow * 0.3)
            
            corners = [
                (margin, margin, 'tl'),
                (width - margin, margin, 'tr'),
                (margin, height - margin, 'bl'),
                (width - margin, height - margin, 'br')
            ]
            
            for x, y, corner_type in corners:
                if corner_type == 'tl':
                    # Top-left
                    self.video_canvas.create_line(
                        x, y + bracket_size, x, y, x + bracket_size, y,
                        fill=color, width=2, tags='hud_overlay'
                    )
                elif corner_type == 'tr':
                    # Top-right
                    self.video_canvas.create_line(
                        x - bracket_size, y, x, y, x, y + bracket_size,
                        fill=color, width=2, tags='hud_overlay'
                    )
                elif corner_type == 'bl':
                    # Bottom-left
                    self.video_canvas.create_line(
                        x, y - bracket_size, x, y, x + bracket_size, y,
                        fill=color, width=2, tags='hud_overlay'
                    )
                elif corner_type == 'br':
                    # Bottom-right
                    self.video_canvas.create_line(
                        x - bracket_size, y, x, y, x, y - bracket_size,
                        fill=color, width=2, tags='hud_overlay'
                    )
        except Exception as e:
            logger.error(f"Corner brackets error: {e}")
    
    def draw_scanning_grid(self, width, height):
        """Draw animated scanning grid"""
        try:
            grid_spacing = 40
            self.grid_offset = (self.grid_offset + 1) % grid_spacing
            
            # Vertical lines
            for x in range(0, width, grid_spacing):
                offset_x = x + self.grid_offset
                if 0 <= offset_x <= width:
                    alpha = 0.3 + 0.2 * math.sin(self.animation_time + x * 0.1)
                    color = self.interpolate_color(
                        self.colors['accent'], 
                        self.colors['background'], 
                        1 - alpha
                    )
                    self.video_canvas.create_line(
                        offset_x, 0, offset_x, height,
                        fill=color, width=1, tags='hud_overlay'
                    )
            
            # Horizontal lines
            for y in range(0, height, grid_spacing):
                offset_y = y + self.grid_offset
                if 0 <= offset_y <= height:
                    alpha = 0.3 + 0.2 * math.sin(self.animation_time + y * 0.1)
                    color = self.interpolate_color(
                        self.colors['accent'], 
                        self.colors['background'], 
                        1 - alpha
                    )
                    self.video_canvas.create_line(
                        0, offset_y, width, offset_y,
                        fill=color, width=1, tags='hud_overlay'
                    )
        except Exception as e:
            logger.error(f"Scanning grid error: {e}")
    
    def draw_detection_zones(self, width, height):
        """Draw detection zones and targets"""
        try:
            # Face detection zone (center)
            face_x = width // 2
            face_y = height // 3
            face_size = min(120, width // 6)
            
            # Animated face target
            pulse = 1 + 0.2 * math.sin(self.animation_time * 3)
            target_color = self.colors['success'] if self.detection_results.get('facial_recognition') else self.colors['primary']
            
            # Crosshair
            self.video_canvas.create_oval(
                face_x - face_size * pulse, face_y - face_size * pulse,
                face_x + face_size * pulse, face_y + face_size * pulse,
                outline=target_color, width=2, tags='hud_overlay'
            )
            
            # Center dot
            self.video_canvas.create_oval(
                face_x - 3, face_y - 3, face_x + 3, face_y + 3,
                fill=target_color, tags='hud_overlay'
            )
            
            # Eye tracking zones
            eye_offset = face_size // 3
            for eye_x in [face_x - eye_offset, face_x + eye_offset]:
                eye_size = 20
                self.video_canvas.create_rectangle(
                    eye_x - eye_size, face_y - 10,
                    eye_x + eye_size, face_y + 10,
                    outline=self.colors['accent'], width=1, tags='hud_overlay'
                )
                
        except Exception as e:
            logger.error(f"Detection zones error: {e}")
    
    def draw_hud_status(self, width, height):
        """Draw HUD status information"""
        try:
            # Top-left status
            status_x = 30
            status_y = 30
            
            status_items = [
                ("NEURAL VISION: ACTIVE", self.colors['success']),
                (f"SCAN RATE: {int(30)} FPS", self.colors['primary']),
                ("THREAT LEVEL: MONITORING", self.colors['accent'])
            ]
            
            for i, (text, color) in enumerate(status_items):
                self.video_canvas.create_text(
                    status_x, status_y + i * 20,
                    text=text, fill=color,
                    font=('Consolas', 10, 'bold'),
                    anchor='w', tags='hud_overlay'
                )
                
        except Exception as e:
            logger.error(f"HUD status error: {e}")
    
    def draw_threat_assessment(self, width, height):
        """Draw threat assessment display"""
        try:
            # Right side threat panel
            panel_x = width - 200
            panel_y = 50
            panel_width = 180
            panel_height = 150
            
            # Panel background
            self.video_canvas.create_rectangle(
                panel_x, panel_y, panel_x + panel_width, panel_y + panel_height,
                outline=self.colors['primary'], width=1,
                fill='', tags='hud_overlay'
            )
            
            # Title
            self.video_canvas.create_text(
                panel_x + panel_width // 2, panel_y + 15,
                text="THREAT ASSESSMENT", fill=self.colors['text'],
                font=('Consolas', 10, 'bold'), tags='hud_overlay'
            )
            
            # Threat levels
            threats = [
                ("DROWSINESS", self.detection_results.get('drowsiness'), self.colors['danger']),
                ("DISTRACTION", self.detection_results.get('distraction'), self.colors['warning']),
                ("ATTENTION", self.detection_results.get('attention'), self.colors['success'])
            ]
            
            for i, (name, active, color) in enumerate(threats):
                y_pos = panel_y + 40 + i * 25
                
                # Threat name
                self.video_canvas.create_text(
                    panel_x + 10, y_pos,
                    text=name, fill=self.colors['text'],
                    font=('Consolas', 8), anchor='w', tags='hud_overlay'
                )
                
                # Status bar
                bar_width = 80
                bar_x = panel_x + 90
                
                # Background bar
                self.video_canvas.create_rectangle(
                    bar_x, y_pos - 5, bar_x + bar_width, y_pos + 5,
                    outline='#444444', fill='#222222', tags='hud_overlay'
                )
                
                # Active bar
                if active:
                    fill_width = bar_width * 0.8  # Simulated threat level
                    self.video_canvas.create_rectangle(
                        bar_x, y_pos - 5, bar_x + fill_width, y_pos + 5,
                        outline=color, fill=color, tags='hud_overlay'
                    )
                    
        except Exception as e:
            logger.error(f"Threat assessment error: {e}")
    
    def update_detection_states(self):
        """Update detection indicator states"""
        try:
            for name, indicator in self.detection_indicators.items():
                # Map detection results to indicators
                if name == 'drowsiness':
                    indicator['active'] = self.detection_results.get('drowsiness', False)
                elif name == 'distraction':
                    indicator['active'] = self.detection_results.get('distraction', False)
                elif name == 'attention':
                    indicator['active'] = self.detection_results.get('attention', False)
                elif name == 'seatbelt':
                    indicator['active'] = self.detection_results.get('seatbelt', False)
                elif name == 'hands':
                    indicator['active'] = self.detection_results.get('hand_position', False)
                elif name == 'face_id':
                    indicator['active'] = self.detection_results.get('facial_recognition', False)
                elif name == 'emotion':
                    indicator['active'] = self.detection_results.get('emotion', False)
                    
        except Exception as e:
            logger.error(f"Detection states update error: {e}")
    
    def update_hud_overlays(self):
        """Update HUD overlay animations"""
        try:
            # This method can be used for real-time HUD updates
            pass
        except Exception as e:
            logger.error(f"HUD overlay update error: {e}")
    
    def start_monitoring(self):
        """Start monitoring mode"""
        self.is_monitoring = True
        
    def stop_monitoring(self):
        """Stop monitoring mode"""
        self.is_monitoring = False
        
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two hex colors"""
        try:
            factor = max(0, min(1, factor))
            rgb1 = self.hex_to_rgb(color1)
            rgb2 = self.hex_to_rgb(color2)
            
            r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * factor)
            g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * factor)
            b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color1
    
    def destroy(self):
        """Clean up resources"""
        self.animation_running = False
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
