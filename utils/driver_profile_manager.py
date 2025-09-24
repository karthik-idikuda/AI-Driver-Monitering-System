"""
Driver Profile Manager for Driver Monitoring System
Handles storing, retrieving, and managing driver profiles
"""

import os
import json
import logging
import cv2
import numpy as np
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class DriverProfileManager:
    def __init__(self, profiles_dir="data/driver_profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Load existing profiles
        self.profiles = self.load_profiles()
        
        # Current active profile
        self.active_profile = None
    
    def load_profiles(self):
        """Load all existing driver profiles"""
        profiles = {}
        
        try:
            profile_files = [f for f in os.listdir(self.profiles_dir) if f.endswith('.json')]
            
            for profile_file in profile_files:
                profile_path = os.path.join(self.profiles_dir, profile_file)
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                    driver_id = profile.get('driver_id')
                    if driver_id:
                        profiles[driver_id] = profile
            
            logger.info(f"Loaded {len(profiles)} driver profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"Error loading driver profiles: {str(e)}")
            return {}
    
    def save_profile(self, profile):
        """Save a driver profile to disk"""
        try:
            driver_id = profile.get('driver_id')
            if not driver_id:
                logger.error("Cannot save profile without driver_id")
                return False
            
            filename = f"{driver_id}.json"
            profile_path = os.path.join(self.profiles_dir, filename)
            
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
            
            # Update in-memory profiles
            self.profiles[driver_id] = profile
            
            logger.info(f"Saved profile for driver: {profile.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving driver profile: {str(e)}")
            return False
    
    def create_profile(self, name, face_image=None, authorized=True):
        """Create a new driver profile"""
        try:
            # Generate unique ID
            driver_id = f"driver_{len(self.profiles) + 1}_{int(datetime.now().timestamp())}"
            
            # Create profile
            profile = {
                'driver_id': driver_id,
                'name': name,
                'authorized': authorized,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'recognition_data': {},
                'preferences': {
                    'alert_volume': 0.8,
                    'seat_position': 'default',
                    'mirror_positions': 'default'
                },
                'history': []
            }
            
            # Save face image if provided
            if face_image is not None:
                # Convert image to base64 for storage
                _, buffer = cv2.imencode('.jpg', face_image)
                encoded_image = base64.b64encode(buffer).decode('utf-8')
                profile['face_image'] = encoded_image
            
            # Save profile
            if self.save_profile(profile):
                return profile
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating driver profile: {str(e)}")
            return None
    
    def get_profile(self, driver_id):
        """Get a driver profile by ID"""
        return self.profiles.get(driver_id)
    
    def get_profile_by_name(self, name):
        """Get a driver profile by name"""
        for profile in self.profiles.values():
            if profile.get('name').lower() == name.lower():
                return profile
        return None
    
    def update_profile(self, driver_id, updates):
        """Update a driver profile"""
        profile = self.get_profile(driver_id)
        if not profile:
            return False
        
        # Apply updates
        for key, value in updates.items():
            if key != 'driver_id':  # Don't update ID
                profile[key] = value
        
        # Update timestamp
        profile['updated_at'] = datetime.now().isoformat()
        
        # Save updated profile
        return self.save_profile(profile)
    
    def delete_profile(self, driver_id):
        """Delete a driver profile"""
        try:
            profile = self.get_profile(driver_id)
            if not profile:
                return False
            
            # Remove file
            filename = f"{driver_id}.json"
            profile_path = os.path.join(self.profiles_dir, filename)
            
            if os.path.exists(profile_path):
                os.remove(profile_path)
            
            # Remove from memory
            if driver_id in self.profiles:
                del self.profiles[driver_id]
            
            logger.info(f"Deleted profile for driver: {profile.get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting driver profile: {str(e)}")
            return False
    
    def set_active_profile(self, driver_id):
        """Set the active driver profile"""
        profile = self.get_profile(driver_id)
        if profile:
            self.active_profile = profile
            logger.info(f"Active driver set to: {profile.get('name', 'Unknown')}")
            return True
        return False
    
    def get_active_profile(self):
        """Get the active driver profile"""
        return self.active_profile
    
    def clear_active_profile(self):
        """Clear the active driver profile"""
        self.active_profile = None
    
    def add_session_to_history(self, driver_id, session_data):
        """Add a driving session to a driver's history"""
        profile = self.get_profile(driver_id)
        if not profile:
            return False
        
        # Create session entry
        session = {
            'timestamp': datetime.now().isoformat(),
            'duration': session_data.get('duration', 0),
            'alerts': session_data.get('alerts', []),
            'metrics': session_data.get('metrics', {})
        }
        
        # Add to history
        if 'history' not in profile:
            profile['history'] = []
        
        profile['history'].append(session)
        
        # Limit history size
        if len(profile['history']) > 100:
            profile['history'] = profile['history'][-100:]
        
        # Save updated profile
        return self.save_profile(profile)
    
    def get_all_profiles(self):
        """Get all driver profiles"""
        return list(self.profiles.values())
    
    def get_authorized_drivers(self):
        """Get all authorized driver profiles"""
        return [p for p in self.profiles.values() if p.get('authorized', False)]
    
    def get_unauthorized_drivers(self):
        """Get all unauthorized driver profiles"""
        return [p for p in self.profiles.values() if not p.get('authorized', False)]
