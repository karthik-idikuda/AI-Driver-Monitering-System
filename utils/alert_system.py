"""
Alert System for Driver Monitoring
Handles audio and visual alerts for various safety conditions
"""

import cv2
import pygame
import threading
import logging
import os
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self, config_path="config/config.json"):
        self.config = self.load_config(config_path)
        
        # Initialize pygame mixer for audio alerts
        pygame.mixer.init()
        
        # Alert states
        self.active_alerts = set()
        self.alert_history = []
        self.sound_enabled = self.config.get("alerts", {}).get("sound_enabled", True)
        self.visual_enabled = self.config.get("alerts", {}).get("visual_alerts", True)
        
        # Alert definitions
        self.alert_definitions = {
            "drowsiness": {
                "message": "DROWSINESS DETECTED!",
                "color": (0, 0, 255),
                "sound": "data/alerts/drowsiness_alert.wav",
                "priority": 5
            },
            "distraction": {
                "message": "DRIVER DISTRACTED!",
                "color": (0, 165, 255),
                "sound": "data/alerts/distraction_alert.wav",
                "priority": 4
            },
            "no_seatbelt": {
                "message": "SEATBELT NOT DETECTED!",
                "color": (255, 0, 0),
                "sound": "data/alerts/seatbelt_alert.wav",
                "priority": 3
            },
            "inattention": {
                "message": "DRIVER INATTENTIVE!",
                "color": (255, 165, 0),
                "sound": "data/alerts/attention_alert.wav",
                "priority": 4
            },
            "hands_off_wheel": {
                "message": "HANDS OFF STEERING WHEEL!",
                "color": (255, 0, 255),
                "sound": "data/alerts/hands_alert.wav",
                "priority": 4
            },
            "unauthorized_driver": {
                "message": "UNAUTHORIZED DRIVER!",
                "color": (128, 0, 128),
                "sound": "data/alerts/unauthorized_alert.wav",
                "priority": 5
            },
            "stress_detected": {
                "message": "DRIVER STRESS DETECTED!",
                "color": (255, 140, 0),
                "sound": "data/alerts/stress_alert.wav",
                "priority": 2
            }
        }
        
        # Create alert sounds directory
        self.create_alert_sounds()
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def create_alert_sounds(self):
        """Create alert sound directory and placeholder sounds"""
        sounds_dir = "data/alerts"
        os.makedirs(sounds_dir, exist_ok=True)
        
        # Create placeholder sound files (you would replace these with actual audio files)
        sound_files = [
            "drowsiness_alert.wav",
            "distraction_alert.wav", 
            "seatbelt_alert.wav",
            "attention_alert.wav",
            "hands_alert.wav",
            "unauthorized_alert.wav",
            "stress_alert.wav"
        ]
        
        for sound_file in sound_files:
            sound_path = os.path.join(sounds_dir, sound_file)
            if not os.path.exists(sound_path):
                # Create empty placeholder file
                with open(sound_path, 'w') as f:
                    f.write(f"# Placeholder for {sound_file}\n")
    
    def play_alert_sound(self, alert_type):
        """Play alert sound in a separate thread"""
        if not self.sound_enabled:
            return
        
        def play_sound():
            try:
                alert_def = self.alert_definitions.get(alert_type, {})
                sound_file = alert_def.get("sound")
                
                if sound_file and os.path.exists(sound_file):
                    # Check if it's an actual audio file
                    if sound_file.endswith('.wav') and os.path.getsize(sound_file) > 100:
                        pygame.mixer.music.load(sound_file)
                        pygame.mixer.music.play()
                    else:
                        # Fallback: generate beep sound
                        self.generate_beep_sound(alert_type)
                else:
                    # Generate system beep as fallback
                    self.generate_beep_sound(alert_type)
                    
            except Exception as e:
                logger.error(f"Error playing alert sound: {str(e)}")
        
        # Play sound in separate thread to avoid blocking
        sound_thread = threading.Thread(target=play_sound)
        sound_thread.daemon = True
        sound_thread.start()
    
    def generate_beep_sound(self, alert_type):
        """Generate a simple beep sound"""
        try:
            # Simple system beep (works on most systems)
            print(f"\a")  # ASCII bell character
            
            # Alternative: Generate tone using pygame
            # This is a simplified version - you might want to use a proper audio library
            duration = 0.5
            frequency = 800
            
            # Create a simple sine wave
            sample_rate = 22050
            samples = int(sample_rate * duration)
            wave_array = []
            
            for i in range(samples):
                wave_array.append(int(4095 * np.sin(frequency * 2 * np.pi * i / sample_rate)))
            
            # This would need proper audio handling - simplified for now
            
        except Exception as e:
            logger.error(f"Error generating beep: {str(e)}")
    
    def trigger_alert(self, alert_type, severity=1.0):
        """Trigger an alert with given type and severity"""
        if alert_type not in self.alert_definitions:
            logger.warning(f"Unknown alert type: {alert_type}")
            return
        
        # Add to active alerts
        self.active_alerts.add(alert_type)
        
        # Log alert
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "alert_type": alert_type,
            "severity": severity,
            "message": self.alert_definitions[alert_type]["message"]
        }
        
        self.alert_history.append(alert_data)
        logger.warning(f"ALERT: {alert_data['message']} (Severity: {severity})")
        
        # Play sound
        self.play_alert_sound(alert_type)
    
    def clear_alert(self, alert_type):
        """Clear a specific alert"""
        self.active_alerts.discard(alert_type)
    
    def clear_all_alerts(self):
        """Clear all active alerts"""
        self.active_alerts.clear()
    
    def draw_visual_alerts(self, frame):
        """Draw visual alerts on the frame"""
        if not self.visual_enabled or not self.active_alerts:
            return frame
        
        height, width = frame.shape[:2]
        
        # Sort alerts by priority (highest first)
        sorted_alerts = sorted(self.active_alerts, 
                             key=lambda x: self.alert_definitions[x]["priority"], 
                             reverse=True)
        
        # Draw alert panel background
        if sorted_alerts:
            panel_height = min(200, len(sorted_alerts) * 40 + 20)
            panel_width = 400
            
            # Semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(overlay, (width - panel_width - 10, 10), 
                         (width - 10, 10 + panel_height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # Draw alert border
            cv2.rectangle(frame, (width - panel_width - 10, 10), 
                         (width - 10, 10 + panel_height), (0, 0, 255), 2)
        
        # Draw individual alerts
        y_offset = 40
        for alert_type in sorted_alerts:
            alert_def = self.alert_definitions[alert_type]
            message = alert_def["message"]
            color = alert_def["color"]
            
            # Draw alert text
            cv2.putText(frame, message, (width - panel_width, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw priority indicator
            priority_text = f"P{alert_def['priority']}"
            cv2.putText(frame, priority_text, (width - 50, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            y_offset += 30
        
        # Draw alert count
        if len(self.active_alerts) > 0:
            alert_count_text = f"ACTIVE ALERTS: {len(self.active_alerts)}"
            cv2.putText(frame, alert_count_text, (10, height - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return frame
    
    def get_alert_statistics(self):
        """Get statistics about alerts"""
        if not self.alert_history:
            return {}
        
        # Count alerts by type
        alert_counts = {}
        for alert in self.alert_history:
            alert_type = alert["alert_type"]
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        # Recent alerts (last hour)
        current_time = datetime.now()
        recent_alerts = []
        
        for alert in self.alert_history:
            alert_time = datetime.fromisoformat(alert["timestamp"])
            time_diff = (current_time - alert_time).total_seconds()
            
            if time_diff <= 3600:  # Last hour
                recent_alerts.append(alert)
        
        return {
            "total_alerts": len(self.alert_history),
            "alert_counts": alert_counts,
            "recent_alerts": len(recent_alerts),
            "active_alerts": list(self.active_alerts)
        }
    
    def save_alert_log(self, filename="data/logs/alert_log.json"):
        """Save alert history to file"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(self.alert_history, f, indent=2)
            
            logger.info(f"Alert log saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving alert log: {str(e)}")
    
    def load_alert_log(self, filename="data/logs/alert_log.json"):
        """Load alert history from file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    self.alert_history = json.load(f)
                
                logger.info(f"Alert log loaded from {filename}")
            
        except Exception as e:
            logger.error(f"Error loading alert log: {str(e)}")

# Add numpy import for beep generation
import numpy as np
