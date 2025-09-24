"""
Configuration Manager for Driver Monitoring System
Handles loading and saving of system configuration
"""

import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_file="config/config.json"):
        self.config_file = config_file
        self.config = {}
        self.default_config = self._get_default_config()
        
        # Load configuration
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "camera": {
                "device_id": 0,
                "resolution": [640, 480],
                "fps": 30,
                "auto_exposure": True
            },
            "detection_settings": {
                "drowsiness": {
                    "eye_aspect_ratio_threshold": 0.25,
                    "consecutive_frames": 20,
                    "enabled": True
                },
                "distraction": {
                    "head_pose_threshold": 30,
                    "consecutive_frames": 15,
                    "enabled": True
                },
                "seatbelt": {
                    "confidence_threshold": 0.7,
                    "enabled": True
                },
                "attention": {
                    "gaze_threshold": 0.3,
                    "consecutive_frames": 10,
                    "enabled": True
                },
                "hand_position": {
                    "steering_wheel_region": [200, 300, 400, 450],
                    "confidence_threshold": 0.6,
                    "min_hands_required": 1,
                    "enabled": True
                },
                "facial_recognition": {
                    "tolerance": 0.6,
                    "enabled": True
                },
                "emotion": {
                    "stress_threshold": 0.7,
                    "enabled": True
                }
            },
            "models": {
                "face_detection": "models/haarcascade_frontalface_default.xml",
                "eye_detection": "models/haarcascade_eye.xml",
                "landmarks": "models/shape_predictor_68_face_landmarks.dat",
                "emotion_model": "models/emotion_model.h5",
                "seatbelt_model": "models/seatbelt_detector.h5"
            },
            "alerts": {
                "sound_enabled": True,
                "visual_alerts": True,
                "log_alerts": True,
                "alert_cooldown": 5.0
            },
            "logging": {
                "level": "INFO",
                "file": "data/logs/driver_monitoring.log",
                "max_file_size": 10485760  # 10MB
            },
            "gui": {
                "window_title": "Driver Monitoring System",
                "window_size": [1200, 800],
                "theme": "dark",
                "show_fps": True,
                "show_debug_info": False
            },
            "system": {
                "auto_start_monitoring": False,
                "save_video_recordings": False,
                "recording_duration": 300,  # 5 minutes
                "enable_remote_monitoring": False
            }
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                
                # Merge with defaults (in case new settings were added)
                self.config = self._merge_configs(self.default_config, file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                # Use default config and save it
                self.config = self.default_config.copy()
                self.save_config()
                logger.info("Using default configuration")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'camera.fps')"""
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                value = value[key]
            
            return value
            
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            config_ref = self.config
            
            # Navigate to the parent of the final key
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # Set the final value
            config_ref[keys[-1]] = value
            
            logger.info(f"Configuration updated: {key_path} = {value}")
            
        except Exception as e:
            logger.error(f"Error setting configuration: {str(e)}")
    
    def get_camera_config(self):
        """Get camera configuration"""
        return self.get('camera', {})
    
    def get_detection_config(self, detector_name):
        """Get detection configuration for specific detector"""
        return self.get(f'detection_settings.{detector_name}', {})
    
    def get_model_path(self, model_name):
        """Get path to model file"""
        return self.get(f'models.{model_name}', '')
    
    def get_alert_config(self):
        """Get alert configuration"""
        return self.get('alerts', {})
    
    def get_gui_config(self):
        """Get GUI configuration"""
        return self.get('gui', {})
    
    def is_detector_enabled(self, detector_name):
        """Check if a detector is enabled"""
        return self.get(f'detection_settings.{detector_name}.enabled', True)
    
    def enable_detector(self, detector_name, enabled=True):
        """Enable or disable a detector"""
        self.set(f'detection_settings.{detector_name}.enabled', enabled)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.save_config()
        logger.info("Configuration reset to defaults")
    
    def validate_config(self):
        """Validate configuration values"""
        issues = []
        
        # Check camera settings
        camera_config = self.get_camera_config()
        if camera_config.get('fps', 0) <= 0:
            issues.append("Invalid camera FPS value")
        
        if not isinstance(camera_config.get('resolution', []), list) or len(camera_config.get('resolution', [])) != 2:
            issues.append("Invalid camera resolution format")
        
        # Check model files
        for model_name in ['face_detection', 'eye_detection', 'landmarks']:
            model_path = self.get_model_path(model_name)
            if model_path and not os.path.exists(model_path):
                issues.append(f"Model file not found: {model_path}")
        
        # Check thresholds
        detectors = ['drowsiness', 'distraction', 'seatbelt', 'attention']
        for detector in detectors:
            config = self.get_detection_config(detector)
            
            if 'threshold' in str(config):
                for key, value in config.items():
                    if 'threshold' in key and not (0 <= float(value) <= 1):
                        issues.append(f"Invalid threshold for {detector}.{key}: {value}")
        
        if issues:
            logger.warning(f"Configuration validation issues: {issues}")
        
        return len(issues) == 0, issues
    
    def export_config(self, filename):
        """Export configuration to a file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Configuration exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting configuration: {str(e)}")
            return False
    
    def import_config(self, filename):
        """Import configuration from a file"""
        try:
            with open(filename, 'r') as f:
                imported_config = json.load(f)
            
            # Validate and merge
            self.config = self._merge_configs(self.default_config, imported_config)
            self.save_config()
            
            logger.info(f"Configuration imported from {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing configuration: {str(e)}")
            return False
