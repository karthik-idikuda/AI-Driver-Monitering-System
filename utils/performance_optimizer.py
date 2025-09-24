"""
Performance Optimizer for Driver Monitoring System
Helps optimize system performance based on available resources
"""

import cv2
import time
import psutil
import logging
import platform
import numpy as np
from threading import Thread
import os

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        
        # Performance metrics
        self.processing_times = {
            'drowsiness': [],
            'distraction': [],
            'seatbelt': [],
            'facial_recognition': [],
            'emotion': [],
            'hand_position': [],
            'attention': []
        }
        
        # Hardware info
        self.system_info = self.get_system_info()
        self.performance_profile = self.determine_performance_profile()
        
        # Initial optimization settings
        self.resolution_scale = 1.0
        self.process_every_n_frames = 1
        self.current_frame_count = 0
        self.skip_frames = False
        
        logger.info(f"System performance profile: {self.performance_profile}")
    
    def get_system_info(self):
        """Get system hardware information"""
        info = {
            'cpu_count': os.cpu_count(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'platform': platform.system(),
            'opencv_version': cv2.__version__,
            'has_cuda': cv2.cuda.getCudaEnabledDeviceCount() > 0 if hasattr(cv2, 'cuda') else False,
            'has_opencl': cv2.ocl.useOpenCL()
        }
        
        return info
    
    def determine_performance_profile(self):
        """Determine the system performance profile"""
        # Basic heuristic to determine performance capability
        cpu_score = self.system_info['cpu_count'] * (1 - min(self.system_info['cpu_percent'] / 100, 0.8))
        memory_score = min(self.system_info['memory_available'] / (2 * 1024 * 1024 * 1024), 1.0)  # Normalize to 2GB
        
        # Calculate overall score (0-10)
        overall_score = (cpu_score * 5 + memory_score * 5)
        
        # Determine profile
        if overall_score >= 8:
            return "high"
        elif overall_score >= 5:
            return "medium"
        else:
            return "low"
    
    def optimize_frame(self, frame):
        """Optimize frame for processing based on performance profile"""
        # Skip frames if needed
        self.current_frame_count += 1
        if self.skip_frames and self.current_frame_count % self.process_every_n_frames != 0:
            return None
        
        # Apply resolution scaling if needed for processing optimization
        # Return both original and optimized frame
        optimized_frame = frame
        if self.resolution_scale < 1.0:
            h, w = frame.shape[:2]
            new_w = int(w * self.resolution_scale)
            new_h = int(h * self.resolution_scale)
            optimized_frame = cv2.resize(frame, (new_w, new_h))
        
        return optimized_frame
    
    def log_processing_time(self, detector_name, process_time):
        """Log processing time for a detector"""
        if detector_name in self.processing_times:
            self.processing_times[detector_name].append(process_time)
            # Keep only the last 100 measurements
            if len(self.processing_times[detector_name]) > 100:
                self.processing_times[detector_name].pop(0)
    
    def get_average_processing_times(self):
        """Get average processing times for each detector"""
        avg_times = {}
        for detector, times in self.processing_times.items():
            if times:
                avg_times[detector] = sum(times) / len(times)
            else:
                avg_times[detector] = 0
        return avg_times
    
    def adjust_settings_for_performance(self, current_fps):
        """Dynamically adjust settings based on current FPS"""
        target_fps = 20  # More reasonable target FPS
        
        if current_fps < 10 and self.resolution_scale > 0.7:
            # Reduce resolution if FPS is very low (but not too much)
            self.resolution_scale = max(self.resolution_scale - 0.1, 0.7)
            logger.info(f"Reducing resolution scale to {self.resolution_scale} to improve performance")
            return True
        
        elif current_fps < 5 and not self.skip_frames:
            # Start skipping frames if FPS is critically low
            self.skip_frames = True
            self.process_every_n_frames = 2
            logger.info("Enabling frame skipping to improve performance")
            return True
        
        elif current_fps > 18 and self.resolution_scale < 1.0:
            # Increase resolution if FPS is good
            self.resolution_scale = min(self.resolution_scale + 0.1, 1.0)
            logger.info(f"Increasing resolution scale to {self.resolution_scale}")
            return True
            
        elif current_fps > 25 and self.skip_frames:
            # Disable frame skipping if FPS is very good
            self.skip_frames = False
            self.process_every_n_frames = 1
            logger.info("Disabling frame skipping")
            return True
            
        return False  # No changes made
    
    def get_recommendations(self):
        """Get performance optimization recommendations"""
        avg_times = self.get_average_processing_times()
        
        recommendations = []
        
        # Find the slowest detector
        if avg_times:
            slowest_detector = max(avg_times.items(), key=lambda x: x[1])
            if slowest_detector[1] > 0.05:  # If taking more than 50ms
                recommendations.append(f"Consider optimizing the {slowest_detector[0]} detector")
        
        # Check system resources
        if self.system_info['cpu_percent'] > 90:
            recommendations.append("CPU usage is very high, consider closing other applications")
        
        if self.system_info['memory_available'] < 500 * 1024 * 1024:  # Less than 500MB
            recommendations.append("System is low on memory, consider closing other applications")
        
        # Hardware acceleration recommendations
        if not self.system_info['has_cuda'] and not self.system_info['has_opencl']:
            recommendations.append("Consider using a system with GPU acceleration for better performance")
        
        return recommendations
        
    def generate_performance_report(self):
        """Generate a performance report"""
        report = {
            'system_info': self.system_info,
            'performance_profile': self.performance_profile,
            'current_settings': {
                'resolution_scale': self.resolution_scale,
                'frame_skipping': self.skip_frames,
                'process_every_n_frames': self.process_every_n_frames
            },
            'average_processing_times': self.get_average_processing_times(),
            'recommendations': self.get_recommendations()
        }
        
        return report
