"""
Driver Attention Detection Module
Analyzes driver attention using gaze tracking and head pose
"""

import cv2
import numpy as np
import mediapipe as mp
import logging

logger = logging.getLogger(__name__)

class AttentionDetector:
    def __init__(self, gaze_threshold=0.3, consecutive_frames=20):
        self.GAZE_THRESHOLD = gaze_threshold
        self.CONSECUTIVE_FRAMES = consecutive_frames
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks indices
        self.LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Attention state
        self.is_attentive = True
        self.attention_score = 1.0
        self.inattention_counter = 0
        
        # Gaze tracking
        self.gaze_direction = {'x': 0, 'y': 0}
        self.is_looking_forward = True
        
        # Road area definition (where driver should be looking)
        self.road_area = None
        
    def set_road_area(self, frame_shape, area_ratios=None):
        """Define the road area where driver should focus"""
        height, width = frame_shape[:2]
        
        if area_ratios:
            x1_ratio, y1_ratio, x2_ratio, y2_ratio = area_ratios
        else:
            # Default road area (upper center of frame)
            x1_ratio, y1_ratio, x2_ratio, y2_ratio = 0.2, 0.1, 0.8, 0.5
        
        self.road_area = [
            int(width * x1_ratio),
            int(height * y1_ratio),
            int(width * x2_ratio),
            int(height * y2_ratio)
        ]
    
    def get_eye_center(self, landmarks, eye_indices, frame_shape):
        """Calculate eye center from landmarks"""
        height, width = frame_shape[:2]
        
        x_coords = []
        y_coords = []
        
        for idx in eye_indices:
            landmark = landmarks[idx]
            x_coords.append(landmark.x * width)
            y_coords.append(landmark.y * height)
        
        center_x = int(np.mean(x_coords))
        center_y = int(np.mean(y_coords))
        
        return (center_x, center_y)
    
    def calculate_gaze_direction(self, landmarks, frame_shape):
        """Calculate gaze direction using eye landmarks"""
        # Get eye centers
        left_eye_center = self.get_eye_center(landmarks, self.LEFT_EYE_LANDMARKS, frame_shape)
        right_eye_center = self.get_eye_center(landmarks, self.RIGHT_EYE_LANDMARKS, frame_shape)
        
        # Calculate average eye center
        avg_eye_center = (
            (left_eye_center[0] + right_eye_center[0]) // 2,
            (left_eye_center[1] + right_eye_center[1]) // 2
        )
        
        # Get nose tip for reference
        nose_tip = landmarks[1]  # Nose tip landmark
        nose_x = int(nose_tip.x * frame_shape[1])
        nose_y = int(nose_tip.y * frame_shape[0])
        
        # Calculate gaze vector (simplified)
        gaze_x = avg_eye_center[0] - nose_x
        gaze_y = avg_eye_center[1] - nose_y
        
        # Normalize
        magnitude = np.sqrt(gaze_x**2 + gaze_y**2)
        if magnitude > 0:
            gaze_x /= magnitude
            gaze_y /= magnitude
        
        self.gaze_direction = {'x': gaze_x, 'y': gaze_y}
        
        return avg_eye_center
    
    def estimate_gaze_point(self, eye_center, gaze_direction, frame_shape):
        """Estimate where the driver is looking on screen"""
        # Simple projection of gaze onto screen
        scale_factor = 200  # Adjust this based on calibration
        
        gaze_x = eye_center[0] + gaze_direction['x'] * scale_factor
        gaze_y = eye_center[1] + gaze_direction['y'] * scale_factor
        
        # Clamp to frame boundaries
        gaze_x = max(0, min(frame_shape[1], gaze_x))
        gaze_y = max(0, min(frame_shape[0], gaze_y))
        
        return (int(gaze_x), int(gaze_y))
    
    def is_gaze_on_road(self, gaze_point):
        """Check if gaze point is in the road area"""
        if not self.road_area:
            return True  # Default to attentive if no road area defined
        
        x1, y1, x2, y2 = self.road_area
        gaze_x, gaze_y = gaze_point
        
        return x1 <= gaze_x <= x2 and y1 <= gaze_y <= y2
    
    def analyze_eye_openness(self, landmarks, frame_shape):
        """Analyze if eyes are open (for attention detection)"""
        # Get eye landmarks
        left_eye_points = []
        right_eye_points = []
        
        height, width = frame_shape[:2]
        
        for idx in self.LEFT_EYE_LANDMARKS[:6]:  # Use subset for speed
            landmark = landmarks[idx]
            left_eye_points.append([landmark.x * width, landmark.y * height])
        
        for idx in self.RIGHT_EYE_LANDMARKS[:6]:
            landmark = landmarks[idx]
            right_eye_points.append([landmark.x * width, landmark.y * height])
        
        left_eye_points = np.array(left_eye_points)
        right_eye_points = np.array(right_eye_points)
        
        # Calculate eye aspect ratios (simplified)
        def eye_aspect_ratio(eye_points):
            # Vertical distances
            A = np.linalg.norm(eye_points[1] - eye_points[5])
            B = np.linalg.norm(eye_points[2] - eye_points[4])
            # Horizontal distance
            C = np.linalg.norm(eye_points[0] - eye_points[3])
            return (A + B) / (2.0 * C) if C > 0 else 0
        
        left_ear = eye_aspect_ratio(left_eye_points)
        right_ear = eye_aspect_ratio(right_eye_points)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Eyes are considered open if EAR > threshold
        eyes_open = avg_ear > 0.2
        
        return eyes_open, avg_ear
    
    def detect_attention(self, frame):
        """Main attention detection function"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not self.road_area:
            self.set_road_area(frame.shape)
        
        # Draw road area
        x1, y1, x2, y2 = self.road_area
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, "Road Focus Area", (x1, y1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        if not results.multi_face_landmarks:
            # No face detected - not attentive
            self.inattention_counter += 1
            self.is_attentive = False
            self.attention_score = 0.0
            
            cv2.putText(frame, "NO FACE DETECTED!", (10, 350),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            return frame, False, 0.0
        
        # Process face landmarks
        face_landmarks = results.multi_face_landmarks[0]
        landmarks = face_landmarks.landmark
        
        # Calculate gaze direction
        eye_center = self.calculate_gaze_direction(landmarks, frame.shape)
        
        # Estimate gaze point
        gaze_point = self.estimate_gaze_point(eye_center, self.gaze_direction, frame.shape)
        
        # Check if looking at road
        self.is_looking_forward = self.is_gaze_on_road(gaze_point)
        
        # Analyze eye openness
        eyes_open, ear = self.analyze_eye_openness(landmarks, frame.shape)
        
        # Draw gaze visualization
        cv2.circle(frame, eye_center, 3, (255, 0, 0), -1)
        cv2.circle(frame, gaze_point, 5, (0, 255, 0) if self.is_looking_forward else (0, 0, 255), -1)
        cv2.line(frame, eye_center, gaze_point, (255, 255, 255), 1)
        
        # Determine overall attention
        if eyes_open and self.is_looking_forward:
            self.is_attentive = True
            self.inattention_counter = 0
            self.attention_score = 1.0
        else:
            self.inattention_counter += 1
            
            if self.inattention_counter >= self.CONSECUTIVE_FRAMES:
                self.is_attentive = False
            
            # Calculate attention score
            self.attention_score = max(0.0, 1.0 - (self.inattention_counter / self.CONSECUTIVE_FRAMES))
        
        # Draw attention status
        attention_text = "ATTENTIVE" if self.is_attentive else "INATTENTIVE"
        attention_color = (0, 255, 0) if self.is_attentive else (0, 0, 255)
        
        cv2.putText(frame, f"Attention: {attention_text}", (10, 350),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, attention_color, 2)
        
        cv2.putText(frame, f"Score: {self.attention_score:.2f}", (10, 370),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Additional indicators
        cv2.putText(frame, f"Eyes: {'OPEN' if eyes_open else 'CLOSED'}", (10, 390),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(frame, f"Gaze: {'ON ROAD' if self.is_looking_forward else 'OFF ROAD'}", (10, 410),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Alert for inattention
        if not self.is_attentive:
            cv2.putText(frame, "ATTENTION ALERT!", (10, 430),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, self.is_attentive, self.attention_score
    
    def reset_attention_state(self):
        """Reset attention detection state"""
        self.inattention_counter = 0
        self.is_attentive = True
        self.attention_score = 1.0
    
    def calibrate_gaze(self, frame):
        """Calibration mode for gaze tracking"""
        # This would be used during setup to improve gaze accuracy
        cv2.putText(frame, "GAZE CALIBRATION MODE", (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, "Look at the center of the screen", (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # Draw calibration point
        height, width = frame.shape[:2]
        center = (width//2, height//2)
        cv2.circle(frame, center, 10, (0, 255, 0), -1)
        
        return frame
