"""
Drowsiness Detection Module
Detects driver drowsiness using eye aspect ratio and blinking patterns
"""

import cv2
import numpy as np
import logging
import time

# Try to import dlib, fall back to simple detection if not available
try:
    import dlib
    from scipy.spatial import distance
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False
    logging.warning("dlib not available, using simple drowsiness detection")

logger = logging.getLogger(__name__)

class DrowsinessDetector:
    def __init__(self, ear_threshold=0.25, consecutive_frames=20):
        self.EAR_THRESHOLD = ear_threshold
        self.CONSECUTIVE_FRAMES = consecutive_frames
        self.frame_counter = 0
        self.drowsy_counter = 0
        
        # Initialize face and eye detectors
        self.face_cascade = cv2.CascadeClassifier()
        self.eye_cascade = cv2.CascadeClassifier()
        
        # Dlib face detector and landmark predictor (if available)
        if DLIB_AVAILABLE:
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = None
        else:
            self.detector = None
            self.predictor = None
        
        # Eye landmark indices for 68-point model
        self.LEFT_EYE_LANDMARKS = list(range(36, 42))
        self.RIGHT_EYE_LANDMARKS = list(range(42, 48))
        
        self.is_drowsy = False
        self.drowsiness_score = 0.0
    
    def load_models(self, face_cascade_path, eye_cascade_path, landmarks_path):
        """Load detection models"""
        try:
            self.face_cascade.load(face_cascade_path)
            self.eye_cascade.load(eye_cascade_path)
            
            if DLIB_AVAILABLE and landmarks_path:
                self.predictor = dlib.shape_predictor(landmarks_path)
                logger.info("Drowsiness detection models loaded successfully (with dlib)")
            else:
                logger.info("Drowsiness detection models loaded successfully (without dlib)")
            return True
        except Exception as e:
            logger.error(f"Failed to load drowsiness models: {str(e)}")
            return False
    
    def calculate_ear(self, eye_landmarks):
        """Calculate Eye Aspect Ratio (EAR)"""
        if not DLIB_AVAILABLE:
            # Simple fallback calculation
            return 0.3  # Default neutral EAR value
            
        # Vertical eye landmarks
        A = distance.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = distance.euclidean(eye_landmarks[2], eye_landmarks[4])
        
        # Horizontal eye landmark
        C = distance.euclidean(eye_landmarks[0], eye_landmarks[3])
        
        # EAR formula
        ear = (A + B) / (2.0 * C)
        return ear
    
    def extract_eye_landmarks(self, landmarks, eye_indices):
        """Extract eye landmarks from face landmarks"""
        eye_points = []
        for i in eye_indices:
            eye_points.append((landmarks.part(i).x, landmarks.part(i).y))
        return np.array(eye_points)
    
    def detect_drowsiness(self, frame):
        """Main drowsiness detection function"""
        start_time = time.time()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if not DLIB_AVAILABLE or self.detector is None:
            # Use simple fallback detection using OpenCV face detection
            result = self._simple_drowsiness_detection(frame, gray)
            
            # Record processing time
            end_time = time.time()
            processing_time = end_time - start_time
            
            # If caller is the main detector with performance optimizer
            if hasattr(self, '_caller') and hasattr(self._caller, 'performance_optimizer'):
                self._caller.performance_optimizer.log_processing_time('drowsiness', processing_time)
                
            return result
        
        # Detect faces using dlib
        faces = self.detector(gray)
        
        if len(faces) == 0:
            return frame, False, 0.0
        
        # Process the first face
        face = faces[0]
        landmarks = self.predictor(gray, face)
        
        # Extract eye landmarks
        left_eye = self.extract_eye_landmarks(landmarks, self.LEFT_EYE_LANDMARKS)
        right_eye = self.extract_eye_landmarks(landmarks, self.RIGHT_EYE_LANDMARKS)
        
        # Calculate EAR for both eyes
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        ear = (left_ear + right_ear) / 2.0
        
        # Draw eye contours
        left_eye_hull = cv2.convexHull(np.array(left_eye, dtype=np.int32))
        right_eye_hull = cv2.convexHull(np.array(right_eye, dtype=np.int32))
        cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)
        
        # Check for drowsiness
        if ear < self.EAR_THRESHOLD:
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
        
        # Calculate drowsiness score (0-1)
        self.drowsiness_score = min(1.0, self.frame_counter / self.CONSECUTIVE_FRAMES)
        
        # Display EAR value
        cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame, self.is_drowsy, self.drowsiness_score
    
    def _simple_drowsiness_detection(self, frame, gray):
        """Simple drowsiness detection fallback when dlib is not available"""
        # Use face detection to detect basic drowsiness indicators
        if not self.face_cascade.empty():
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    # Simple heuristic: if face detected, not drowsy
                    self.frame_counter = 0
                    self.is_drowsy = False
                    self.drowsiness_score = 0.0
                    
                    cv2.putText(frame, "Simple Detection Mode", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    
                    return frame, self.is_drowsy, self.drowsiness_score
        
        # No face detected - could indicate drowsiness
        self.frame_counter += 1
        if self.frame_counter >= self.CONSECUTIVE_FRAMES:
            self.is_drowsy = True
            cv2.putText(frame, "POSSIBLE DROWSINESS - NO FACE", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        self.drowsiness_score = min(1.0, self.frame_counter / self.CONSECUTIVE_FRAMES)
        cv2.putText(frame, "Simple Detection Mode", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        return frame, self.is_drowsy, self.drowsiness_score
    
    def reset_counters(self):
        """Reset detection counters"""
        self.frame_counter = 0
        self.drowsy_counter = 0
        self.is_drowsy = False
        self.drowsiness_score = 0.0
