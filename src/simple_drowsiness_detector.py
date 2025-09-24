"""
Simplified Drowsiness Detection Module
Uses built-in OpenCV cascade classifiers for basic detection
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SimpleDrowsinessDetector:
    def __init__(self, blink_threshold=20, consecutive_frames=20):
        self.BLINK_THRESHOLD = blink_threshold
        self.CONSECUTIVE_FRAMES = consecutive_frames
        self.frame_counter = 0
        self.drowsy_counter = 0
        
        # Initialize OpenCV face and eye cascades (built-in)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        self.is_drowsy = False
        self.drowsiness_score = 0.0
        self.eye_closed_frames = 0
        
    def detect_drowsiness(self, frame):
        """Simple drowsiness detection using eye detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return frame, False, 0.0
        
        # Process the first face
        (x, y, w, h) = faces[0]
        
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Extract face region
        face_gray = gray[y:y+h, x:x+w]
        face_color = frame[y:y+h, x:x+w]
        
        # Detect eyes in face region
        eyes = self.eye_cascade.detectMultiScale(face_gray, 1.1, 3)
        
        # Simple logic: if no eyes detected, person might be drowsy
        if len(eyes) == 0:
            self.eye_closed_frames += 1
        else:
            self.eye_closed_frames = 0
            
            # Draw eye rectangles
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(face_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
        
        # Check for drowsiness
        if self.eye_closed_frames > self.BLINK_THRESHOLD:
            self.frame_counter += 1
            
            if self.frame_counter >= self.CONSECUTIVE_FRAMES:
                self.is_drowsy = True
                self.drowsy_counter += 1
                
                # Draw alert
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            self.frame_counter = 0
            self.is_drowsy = False
        
        # Calculate drowsiness score
        self.drowsiness_score = min(1.0, self.eye_closed_frames / (self.BLINK_THRESHOLD + self.CONSECUTIVE_FRAMES))
        
        # Display status
        status = f"Eyes: {'CLOSED' if len(eyes) == 0 else 'OPEN'}"
        cv2.putText(frame, status, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(frame, f"Closed frames: {self.eye_closed_frames}", (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame, self.is_drowsy, self.drowsiness_score
    
    def reset_counters(self):
        """Reset detection counters"""
        self.frame_counter = 0
        self.drowsy_counter = 0
        self.is_drowsy = False
        self.drowsiness_score = 0.0
        self.eye_closed_frames = 0
