"""
Seatbelt Detection Module
Detects whether the driver is wearing a seatbelt using computer vision
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SeatbeltDetector:
    def __init__(self, confidence_threshold=0.7):
        self.CONFIDENCE_THRESHOLD = confidence_threshold
        self.seatbelt_cascade = cv2.CascadeClassifier()
        
        # Seatbelt detection using color and edge features
        self.is_wearing_seatbelt = False
        self.detection_confidence = 0.0
        
        # ROI for seatbelt detection (chest/shoulder area)
        self.roi_top_ratio = 0.2
        self.roi_bottom_ratio = 0.7
        self.roi_left_ratio = 0.3
        self.roi_right_ratio = 0.7
    
    def detect_seatbelt_by_color(self, frame):
        """Detect seatbelt using color segmentation"""
        height, width = frame.shape[:2]
        
        # Define ROI (Region of Interest) - chest/shoulder area
        roi_top = int(height * self.roi_top_ratio)
        roi_bottom = int(height * self.roi_bottom_ratio)
        roi_left = int(width * self.roi_left_ratio)
        roi_right = int(width * self.roi_right_ratio)
        
        roi = frame[roi_top:roi_bottom, roi_left:roi_right]
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for typical seatbelt colors (dark colors)
        # Black seatbelt
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])
        
        # Dark gray seatbelt
        lower_gray = np.array([0, 0, 50])
        upper_gray = np.array([180, 30, 100])
        
        # Create masks
        mask_black = cv2.inRange(hsv, lower_black, upper_black)
        mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
        
        # Combine masks
        combined_mask = cv2.bitwise_or(mask_black, mask_gray)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        return combined_mask, roi, (roi_left, roi_top, roi_right, roi_bottom)
    
    def detect_seatbelt_by_edges(self, roi):
        """Detect seatbelt using edge detection for diagonal lines"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Hough line detection for diagonal lines (typical seatbelt pattern)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
        
        diagonal_lines = 0
        if lines is not None:
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta)
                # Check for diagonal lines (30-60 degrees or 120-150 degrees)
                if (30 <= angle <= 60) or (120 <= angle <= 150):
                    diagonal_lines += 1
        
        return diagonal_lines, edges
    
    def detect_seatbelt(self, frame):
        """Main seatbelt detection function"""
        # Method 1: Color-based detection
        mask, roi, roi_coords = self.detect_seatbelt_by_color(frame)
        
        # Method 2: Edge-based detection
        diagonal_lines, edges = self.detect_seatbelt_by_edges(roi)
        
        # Calculate detection confidence
        mask_area = cv2.countNonZero(mask)
        roi_area = roi.shape[0] * roi.shape[1]
        color_confidence = mask_area / roi_area
        
        # Edge confidence based on diagonal lines
        edge_confidence = min(1.0, diagonal_lines / 5.0)
        
        # Combined confidence
        self.detection_confidence = (color_confidence * 0.6 + edge_confidence * 0.4)
        
        # Determine if seatbelt is detected
        self.is_wearing_seatbelt = self.detection_confidence > self.CONFIDENCE_THRESHOLD
        
        # Draw ROI rectangle
        roi_left, roi_top, roi_right, roi_bottom = roi_coords
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), 
                     (0, 255, 0) if self.is_wearing_seatbelt else (0, 0, 255), 2)
        
        # Draw detection result
        status_text = "SEATBELT: ON" if self.is_wearing_seatbelt else "SEATBELT: OFF"
        status_color = (0, 255, 0) if self.is_wearing_seatbelt else (0, 0, 255)
        
        cv2.putText(frame, status_text, (10, 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        cv2.putText(frame, f"Confidence: {self.detection_confidence:.2f}", (10, 160),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Alert if no seatbelt
        if not self.is_wearing_seatbelt:
            cv2.putText(frame, "SEATBELT ALERT!", (10, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, self.is_wearing_seatbelt, self.detection_confidence
    
    def calibrate_roi(self, frame):
        """Interactive ROI calibration (for setup)"""
        height, width = frame.shape[:2]
        
        # Draw current ROI
        roi_top = int(height * self.roi_top_ratio)
        roi_bottom = int(height * self.roi_bottom_ratio)
        roi_left = int(width * self.roi_left_ratio)
        roi_right = int(width * self.roi_right_ratio)
        
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)
        cv2.putText(frame, "Seatbelt Detection ROI", (roi_left, roi_top-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        return frame
