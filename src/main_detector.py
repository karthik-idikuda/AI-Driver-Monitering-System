"""
Main Driver Monitoring System
Integrates all detection modules and coordinates their operation
"""

import cv2
import numpy as np
import logging
import time
import threading
from datetime import datetime
import os
import sys

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from drowsiness_detector import DrowsinessDetector
from distraction_detector import DistractionDetector
from seatbelt_detector import SeatbeltDetector
from facial_recognition import FacialRecognition
from emotion_detector import EmotionDetector
from hand_position_detector import HandPositionDetector
from attention_detector import AttentionDetector
from alert_system import AlertSystem
from config_manager import ConfigManager
from performance_optimizer import PerformanceOptimizer

logger = logging.getLogger(__name__)

class DriverMonitoringSystem:
    def __init__(self, config_path="config/config.json"):
        # Initialize configuration and alert system
        self.config_manager = ConfigManager(config_path)
        self.alert_system = AlertSystem(config_path)
        
        # Initialize camera
        self.camera = None
        self.camera_id = self.config_manager.get('camera.device_id', 0)
        self.fps = self.config_manager.get('camera.fps', 30)
        self.resolution = self.config_manager.get('camera.resolution', [640, 480])
        
        # Initialize all detectors
        self.detectors = {}
        self.init_detectors()
        
        # System state
        self.is_running = False
        self.is_paused = False
        self.frame_count = 0
        self.start_time = None
        
        # Performance monitoring and optimization
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.performance_optimizer = PerformanceOptimizer(self.config_manager)
        
        # Detection results
        self.detection_results = {}
        self.frame_buffer = None
        
        # Video recording
        self.video_writer = None
        self.is_recording = False
        
    def init_detectors(self):
        """Initialize all detection modules"""
        try:
            # Drowsiness detector
            if self.config_manager.is_detector_enabled('drowsiness'):
                self.detectors['drowsiness'] = DrowsinessDetector(
                    ear_threshold=self.config_manager.get('detection_settings.drowsiness.eye_aspect_ratio_threshold', 0.25),
                    consecutive_frames=self.config_manager.get('detection_settings.drowsiness.consecutive_frames', 20)
                )
                # Set reference to main detector for performance tracking
                self.detectors['drowsiness']._caller = self
                
                # Load models
                face_cascade = self.config_manager.get_model_path('face_detection')
                eye_cascade = self.config_manager.get_model_path('eye_detection')
                landmarks = self.config_manager.get_model_path('landmarks')
                
                if all([face_cascade, eye_cascade, landmarks]):
                    self.detectors['drowsiness'].load_models(face_cascade, eye_cascade, landmarks)
            
            # Distraction detector
            if self.config_manager.is_detector_enabled('distraction'):
                self.detectors['distraction'] = DistractionDetector(
                    head_pose_threshold=self.config_manager.get('detection_settings.distraction.head_pose_threshold', 30),
                    consecutive_frames=self.config_manager.get('detection_settings.distraction.consecutive_frames', 15)
                )
            
            # Seatbelt detector
            if self.config_manager.is_detector_enabled('seatbelt'):
                self.detectors['seatbelt'] = SeatbeltDetector(
                    confidence_threshold=self.config_manager.get('detection_settings.seatbelt.confidence_threshold', 0.7)
                )
            
            # Facial recognition
            if self.config_manager.is_detector_enabled('facial_recognition'):
                self.detectors['facial_recognition'] = FacialRecognition(
                    tolerance=self.config_manager.get('detection_settings.facial_recognition.tolerance', 0.6)
                )
            
            # Emotion detector
            if self.config_manager.is_detector_enabled('emotion'):
                self.detectors['emotion'] = EmotionDetector()
                
                face_cascade = self.config_manager.get_model_path('face_detection')
                emotion_model = self.config_manager.get_model_path('emotion_model')
                
                if face_cascade:
                    self.detectors['emotion'].load_model(emotion_model, face_cascade)
            
            # Hand position detector
            if self.config_manager.is_detector_enabled('hand_position'):
                steering_wheel_region = self.config_manager.get('detection_settings.hand_position.steering_wheel_region')
                self.detectors['hand_position'] = HandPositionDetector(steering_wheel_region)
            
            # Attention detector
            if self.config_manager.is_detector_enabled('attention'):
                self.detectors['attention'] = AttentionDetector(
                    gaze_threshold=self.config_manager.get('detection_settings.attention.gaze_threshold', 0.3),
                    consecutive_frames=self.config_manager.get('detection_settings.attention.consecutive_frames', 10)
                )
            
            logger.info(f"Initialized {len(self.detectors)} detection modules")
            
        except Exception as e:
            logger.error(f"Error initializing detectors: {str(e)}")
    
    def init_camera(self):
        """Initialize camera capture with improved error handling"""
        try:
            # Release any existing camera first
            if self.camera:
                self.camera.release()
                time.sleep(0.1)  # Brief pause
            
            # Try different backends in order of preference
            backends = [cv2.CAP_AVFOUNDATION, cv2.CAP_V4L2, cv2.CAP_DSHOW, cv2.CAP_ANY]
            
            for backend in backends:
                try:
                    logger.info(f"Attempting to initialize camera {self.camera_id} with backend {backend}")
                    self.camera = cv2.VideoCapture(self.camera_id, backend)
                    
                    if self.camera.isOpened():
                        # Set camera properties
                        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                        self.camera.set(cv2.CAP_PROP_FPS, self.fps)
                        
                        # Set additional properties for better performance
                        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to get latest frame
                        
                        # Test if we can actually read a frame
                        ret, test_frame = self.camera.read()
                        if ret and test_frame is not None:
                            logger.info(f"Camera initialized successfully: {self.resolution[0]}x{self.resolution[1]} @ {self.fps} FPS")
                            logger.info(f"Actual frame size: {test_frame.shape}")
                            return True
                        else:
                            logger.warning(f"Camera opened but cannot read frames with backend {backend}")
                            self.camera.release()
                    else:
                        logger.warning(f"Cannot open camera with backend {backend}")
                        
                except Exception as e:
                    logger.warning(f"Backend {backend} failed: {str(e)}")
                    if self.camera:
                        self.camera.release()
                    continue
            
            # If all backends failed, try with different camera IDs
            if self.camera_id == 0:
                logger.info("Trying alternative camera IDs...")
                for alt_id in [1, 2, -1]:  # Try common alternative IDs
                    try:
                        logger.info(f"Attempting camera ID {alt_id}")
                        self.camera = cv2.VideoCapture(alt_id)
                        if self.camera.isOpened():
                            ret, test_frame = self.camera.read()
                            if ret and test_frame is not None:
                                self.camera_id = alt_id
                                logger.info(f"Successfully switched to camera ID {alt_id}")
                                return True
                        self.camera.release()
                    except Exception as e:
                        logger.warning(f"Camera ID {alt_id} failed: {str(e)}")
                        continue
            
            raise Exception(f"Cannot initialize any camera")
            
        except Exception as e:
            logger.error(f"Error initializing camera: {str(e)}")
            if self.camera:
                self.camera.release()
                self.camera = None
            return False
    
    def start(self):
        """Start the monitoring system"""
        if self.is_running:
            return True
        
        if not self.init_camera():
            return False
        
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self.fps_start_time = time.time()
        
        logger.info("Driver monitoring system started")
        return True
    
    def stop(self):
        """Stop the monitoring system"""
        self.is_running = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        logger.info("Driver monitoring system stopped")
    
    def pause(self):
        """Pause/resume monitoring"""
        self.is_paused = not self.is_paused
        logger.info(f"Monitoring {'paused' if self.is_paused else 'resumed'}")
    
    def process_frame(self):
        """Process a single frame through all detectors with improved error handling"""
        if not self.is_running or not self.camera:
            return None, None

        # Try to read a frame from the camera with timeout handling
        try:
            ret, frame = self.camera.read()
        except Exception as e:
            logger.error(f"Exception reading frame: {str(e)}")
            ret, frame = False, None
        
        # If frame reading failed, try to reinitialize the camera
        if not ret or frame is None:
            logger.warning("Failed to read frame, attempting to reinitialize camera")
            
            # Try to reinitialize camera
            if self.init_camera():
                try:
                    ret, frame = self.camera.read()
                    if not ret or frame is None:
                        logger.error("Camera reinitialization succeeded but still cannot read frames")
                        return None, None
                    else:
                        logger.info("Camera reinitialization successful, frame reading resumed")
                except Exception as e:
                    logger.error(f"Exception after camera reinitialization: {str(e)}")
                    return None, None
            else:
                logger.error("Camera reinitialization failed")
                return None, None

        if self.is_paused:
            return frame, self.detection_results

        # Store original frame
        self.frame_buffer = frame.copy()
        original_frame = frame.copy()  # Keep original for display

        # Apply performance optimization (for processing only)
        optimized_frame = self.performance_optimizer.optimize_frame(frame)

        # If frame is skipped due to performance optimization, return original frame
        if optimized_frame is None:
            return original_frame, self.detection_results
            
        # Use optimized frame for processing, but keep original frame size info
        processed_frame = optimized_frame
        scale_factor = 1.0
        if self.performance_optimizer.resolution_scale < 1.0:
            scale_factor = 1.0 / self.performance_optimizer.resolution_scale
        
        # Clear previous detection results
        self.detection_results = {}
        
        # Process frame through each detector
        try:
            # Drowsiness detection
            if 'drowsiness' in self.detectors:
                processed_frame, is_drowsy, drowsiness_score = self.detectors['drowsiness'].detect_drowsiness(processed_frame)
                self.detection_results['drowsiness'] = {
                    'is_drowsy': is_drowsy,
                    'score': drowsiness_score,
                    'status': 'alert' if is_drowsy else 'normal'
                }
                
                if is_drowsy:
                    self.alert_system.trigger_alert('drowsiness', drowsiness_score)
                else:
                    self.alert_system.clear_alert('drowsiness')
            
            # Distraction detection
            if 'distraction' in self.detectors:
                processed_frame, is_distracted, distraction_score = self.detectors['distraction'].detect_distraction(processed_frame)
                self.detection_results['distraction'] = {
                    'is_distracted': is_distracted,
                    'score': distraction_score,
                    'status': 'alert' if is_distracted else 'normal'
                }
                
                if is_distracted:
                    self.alert_system.trigger_alert('distraction', distraction_score)
                else:
                    self.alert_system.clear_alert('distraction')
            
            # Seatbelt detection
            if 'seatbelt' in self.detectors:
                processed_frame, has_seatbelt, seatbelt_confidence = self.detectors['seatbelt'].detect_seatbelt(processed_frame)
                self.detection_results['seatbelt'] = {
                    'wearing_seatbelt': has_seatbelt,
                    'confidence': seatbelt_confidence,
                    'status': 'normal' if has_seatbelt else 'alert'
                }
                
                if not has_seatbelt:
                    self.alert_system.trigger_alert('no_seatbelt', 1.0 - seatbelt_confidence)
                else:
                    self.alert_system.clear_alert('no_seatbelt')
            
            # Facial recognition
            if 'facial_recognition' in self.detectors:
                processed_frame, driver_name, confidence, is_authorized = self.detectors['facial_recognition'].recognize_face(processed_frame)
                self.detection_results['facial_recognition'] = {
                    'driver_name': driver_name,
                    'confidence': confidence,
                    'is_authorized': is_authorized,
                    'status': 'normal' if is_authorized else 'alert'
                }
                
                if not is_authorized and driver_name != "Unknown":
                    self.alert_system.trigger_alert('unauthorized_driver', 1.0 - confidence)
                else:
                    self.alert_system.clear_alert('unauthorized_driver')
            
            # Emotion detection
            if 'emotion' in self.detectors:
                processed_frame, emotion, emotion_confidence = self.detectors['emotion'].detect_emotion(processed_frame)
                self.detection_results['emotion'] = {
                    'emotion': emotion,
                    'confidence': emotion_confidence,
                    'is_stressed': self.detectors['emotion'].is_driver_stressed(),
                    'status': 'warning' if self.detectors['emotion'].is_driver_stressed() else 'normal'
                }
                
                if self.detectors['emotion'].is_driver_stressed():
                    self.alert_system.trigger_alert('stress_detected', emotion_confidence)
                else:
                    self.alert_system.clear_alert('stress_detected')
            
            # Hand position detection
            if 'hand_position' in self.detectors:
                processed_frame, hands_count, hands_on_wheel = self.detectors['hand_position'].detect_hand_positions(processed_frame)
                self.detection_results['hand_position'] = {
                    'hands_detected': hands_count,
                    'hands_on_wheel': hands_on_wheel,
                    'is_safe': self.detectors['hand_position'].is_safe_hand_position(),
                    'status': 'normal' if self.detectors['hand_position'].is_safe_hand_position() else 'alert'
                }
                
                if not self.detectors['hand_position'].is_safe_hand_position():
                    self.alert_system.trigger_alert('hands_off_wheel', 1.0 - self.detectors['hand_position'].get_hand_position_score())
                else:
                    self.alert_system.clear_alert('hands_off_wheel')
            
            # Attention detection
            if 'attention' in self.detectors:
                processed_frame, is_attentive, attention_score = self.detectors['attention'].detect_attention(processed_frame)
                self.detection_results['attention'] = {
                    'is_attentive': is_attentive,
                    'score': attention_score,
                    'status': 'normal' if is_attentive else 'alert'
                }
                
                if not is_attentive:
                    self.alert_system.trigger_alert('inattention', 1.0 - attention_score)
                else:
                    self.alert_system.clear_alert('inattention')
            
            # Add active alerts to results
            self.detection_results['active_alerts'] = list(self.alert_system.active_alerts)
            
            # Draw visual alerts on the processed frame
            processed_frame = self.alert_system.draw_visual_alerts(processed_frame)
            
            # Scale processed frame back to original size for display
            if scale_factor > 1.0:
                original_height, original_width = original_frame.shape[:2]
                processed_frame = cv2.resize(processed_frame, (original_width, original_height))
            
            # Update performance counters
            self.update_performance_counters()
            
            # Record video if enabled (use original size frame)
            if self.is_recording and self.video_writer:
                self.video_writer.write(processed_frame)
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
        
        # Return the processed frame at original resolution for display
        return processed_frame, self.detection_results
    
    def update_performance_counters(self):
        """Update FPS and other performance metrics"""
        self.frame_count += 1
        self.fps_counter += 1
        
        current_time = time.time()
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
            
            # Dynamically adjust settings based on performance
            self.performance_optimizer.adjust_settings_for_performance(self.current_fps)
    
    def get_fps(self):
        """Get current FPS"""
        return self.current_fps
    
    def get_system_stats(self):
        """Get system statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        # Get performance data
        performance_data = {}
        if hasattr(self, 'performance_optimizer'):
            performance_data = {
                'avg_processing_times': self.performance_optimizer.get_average_processing_times(),
                'performance_profile': self.performance_optimizer.performance_profile,
                'resolution_scale': self.performance_optimizer.resolution_scale,
                'recommendations': self.performance_optimizer.get_recommendations()
            }
        
        return {
            'uptime': uptime,
            'frames_processed': self.frame_count,
            'fps': self.current_fps,
            'active_detectors': list(self.detectors.keys()),
            'active_alerts': len(self.alert_system.active_alerts),
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'performance': performance_data
        }
    
    def update_settings(self, settings):
        """Update system settings"""
        try:
            # Update detector enable/disable status
            for detector_name, enabled in settings.items():
                if detector_name in ['sound_alerts', 'visual_alerts']:
                    continue
                
                if enabled and detector_name not in self.detectors:
                    # Enable detector
                    self.config_manager.enable_detector(detector_name, True)
                    # Re-initialize this detector
                    # (This would require more sophisticated re-initialization logic)
                elif not enabled and detector_name in self.detectors:
                    # Disable detector
                    self.config_manager.enable_detector(detector_name, False)
                    del self.detectors[detector_name]
            
            # Update alert settings
            if 'sound_alerts' in settings:
                self.alert_system.sound_enabled = settings['sound_alerts']
            if 'visual_alerts' in settings:
                self.alert_system.visual_enabled = settings['visual_alerts']
            
            logger.info("Settings updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
    
    def add_driver_face(self, name, frame=None):
        """Add a new driver face"""
        if 'facial_recognition' not in self.detectors:
            return False
        
        if frame is None:
            frame = self.frame_buffer
        
        if frame is not None:
            return self.detectors['facial_recognition'].add_new_face(frame, name)
        
        return False
    
    def start_recording(self, filename=None):
        """Start video recording"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/recordings/recording_{timestamp}.avi"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(filename, fourcc, self.fps, tuple(self.resolution))
            
            if self.video_writer.isOpened():
                self.is_recording = True
                logger.info(f"Started recording to {filename}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            return False
    
    def stop_recording(self):
        """Stop video recording"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            logger.info("Recording stopped")
    
    def take_screenshot(self, filename=None):
        """Take a screenshot of current frame"""
        if self.frame_buffer is None:
            return False
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/screenshots/screenshot_{timestamp}.jpg"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            cv2.imwrite(filename, self.frame_buffer)
            
            logger.info(f"Screenshot saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return False
    
    def test_alerts(self):
        """Test all alert types"""
        alert_types = ['drowsiness', 'distraction', 'no_seatbelt', 'inattention', 
                      'hands_off_wheel', 'unauthorized_driver', 'stress_detected']
        
        for alert_type in alert_types:
            self.alert_system.trigger_alert(alert_type, 0.8)
            time.sleep(0.5)
            self.alert_system.clear_alert(alert_type)
    
    def calibrate_detectors(self):
        """Calibrate detection parameters"""
        # This would open calibration interfaces for each detector
        logger.info("Detector calibration not yet implemented")
    
    def get_detection_history(self):
        """Get detection history"""
        return self.alert_system.get_alert_statistics()
    
    def reset_all_detectors(self):
        """Reset all detector states"""
        for detector in self.detectors.values():
            if hasattr(detector, 'reset_counters'):
                detector.reset_counters()
            if hasattr(detector, 'reset_history'):
                detector.reset_history()
            if hasattr(detector, 'reset_attention_state'):
                detector.reset_attention_state()
        
        self.alert_system.clear_all_alerts()
        logger.info("All detectors reset")

def main():
    """Main function for testing"""
    logging.basicConfig(level=logging.INFO)
    
    # Create monitoring system
    system = DriverMonitoringSystem()
    
    # Start system
    if not system.start():
        print("Failed to start monitoring system")
        return
    
    print("Driver Monitoring System started. Press 'q' to quit.")
    
    try:
        while system.is_running:
            frame, results = system.process_frame()
            
            if frame is not None:
                # Display frame
                cv2.imshow('Driver Monitoring System', frame)
                
                # Check for quit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    system.pause()
                elif key == ord('r'):
                    system.reset_all_detectors()
            
            time.sleep(0.01)  # Small delay
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    finally:
        system.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
