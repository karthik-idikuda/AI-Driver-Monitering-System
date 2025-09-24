"""
Distraction Detection Module
Detects driver distraction using head pose estimation and gaze tracking
"""

import cv2
import numpy as np
import mediapipe as mp
import logging

logger = logging.getLogger(__name__)

class DistractionDetector:
    def __init__(self, head_pose_threshold=30, consecutive_frames=15):
        self.HEAD_POSE_THRESHOLD = head_pose_threshold
        self.CONSECUTIVE_FRAMES = consecutive_frames
        self.distraction_counter = 0
        
        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # 3D model points for head pose estimation
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])
        
        self.is_distracted = False
        self.distraction_score = 0.0
        self.head_pose = {'yaw': 0, 'pitch': 0, 'roll': 0}
    
    def get_head_pose(self, landmarks, image_shape):
        """Calculate head pose angles"""
        height, width = image_shape[:2]
        
        # 2D image points from landmarks
        image_points = np.array([
            (landmarks[1].x * width, landmarks[1].y * height),     # Nose tip
            (landmarks[175].x * width, landmarks[175].y * height), # Chin
            (landmarks[33].x * width, landmarks[33].y * height),   # Left eye corner
            (landmarks[263].x * width, landmarks[263].y * height), # Right eye corner
            (landmarks[61].x * width, landmarks[61].y * height),   # Left mouth corner
            (landmarks[291].x * width, landmarks[291].y * height)  # Right mouth corner
        ], dtype="double")
        
        # Camera internals
        focal_length = width
        center = (width/2, height/2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        dist_coeffs = np.zeros((4,1))
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, image_points, camera_matrix, dist_coeffs)
        
        if success:
            # Convert rotation vector to angles
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # Calculate Euler angles
            sy = np.sqrt(rotation_matrix[0,0] * rotation_matrix[0,0] + 
                        rotation_matrix[1,0] * rotation_matrix[1,0])
            
            singular = sy < 1e-6
            
            if not singular:
                x = np.arctan2(rotation_matrix[2,1], rotation_matrix[2,2])
                y = np.arctan2(-rotation_matrix[2,0], sy)
                z = np.arctan2(rotation_matrix[1,0], rotation_matrix[0,0])
            else:
                x = np.arctan2(-rotation_matrix[1,2], rotation_matrix[1,1])
                y = np.arctan2(-rotation_matrix[2,0], sy)
                z = 0
            
            # Convert to degrees
            self.head_pose = {
                'pitch': np.degrees(x),
                'yaw': np.degrees(y),
                'roll': np.degrees(z)
            }
        
        return self.head_pose
    
    def detect_distraction(self, frame):
        """Main distraction detection function"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return frame, False, 0.0
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Get head pose
        head_pose = self.get_head_pose(face_landmarks.landmark, frame.shape)
        
        # Check for distraction based on head pose
        yaw_abs = abs(head_pose['yaw'])
        pitch_abs = abs(head_pose['pitch'])
        
        if yaw_abs > self.HEAD_POSE_THRESHOLD or pitch_abs > self.HEAD_POSE_THRESHOLD:
            self.distraction_counter += 1
            
            if self.distraction_counter >= self.CONSECUTIVE_FRAMES:
                self.is_distracted = True
                
                # Draw alert
                cv2.putText(frame, "DISTRACTION ALERT!", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            self.distraction_counter = 0
            self.is_distracted = False
        
        # Calculate distraction score
        self.distraction_score = min(1.0, self.distraction_counter / self.CONSECUTIVE_FRAMES)
        
        # Draw head pose information
        cv2.putText(frame, f"Yaw: {head_pose['yaw']:.1f}°", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Pitch: {head_pose['pitch']:.1f}°", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw face mesh
        self.mp_drawing.draw_landmarks(
            frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS,
            None, self.mp_drawing_styles.get_default_face_mesh_contours_style())
        
        return frame, self.is_distracted, self.distraction_score
    
    def reset_counters(self):
        """Reset detection counters"""
        self.distraction_counter = 0
        self.is_distracted = False
        self.distraction_score = 0.0
