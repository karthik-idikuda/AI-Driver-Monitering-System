"""
Hand Position Detection Module
Detects driver hand positions on steering wheel using MediaPipe
"""

import cv2
import numpy as np
import mediapipe as mp
import logging

logger = logging.getLogger(__name__)

class HandPositionDetector:
    def __init__(self, steering_wheel_region=None):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.mp_draw = mp.solutions.drawing_utils
        
        # Steering wheel region (x1, y1, x2, y2)
        if steering_wheel_region:
            self.steering_wheel_region = steering_wheel_region
        else:
            # Default region (will be calibrated based on frame size)
            self.steering_wheel_region = None
        
        # Hand detection state
        self.hands_on_wheel = {"left": False, "right": False}
        self.hand_positions = {"left": None, "right": None}
        self.hands_detected = 0
        
        # Safety thresholds
        self.min_hands_on_wheel = 1  # Minimum hands required on wheel
        self.consecutive_frames_threshold = 30
        self.frames_without_hands = 0
        
    def set_steering_wheel_region(self, frame_shape, region_ratios=None):
        """Set steering wheel detection region"""
        height, width = frame_shape[:2]
        
        if region_ratios:
            x1_ratio, y1_ratio, x2_ratio, y2_ratio = region_ratios
        else:
            # Default ratios for steering wheel area
            x1_ratio, y1_ratio, x2_ratio, y2_ratio = 0.2, 0.4, 0.8, 0.9
        
        self.steering_wheel_region = [
            int(width * x1_ratio),
            int(height * y1_ratio),
            int(width * x2_ratio),
            int(height * y2_ratio)
        ]
    
    def is_hand_on_steering_wheel(self, hand_landmarks, frame_shape):
        """Check if hand is positioned on steering wheel"""
        if not self.steering_wheel_region:
            self.set_steering_wheel_region(frame_shape)
        
        height, width = frame_shape[:2]
        x1, y1, x2, y2 = self.steering_wheel_region
        
        # Get wrist position (landmark 0)
        wrist = hand_landmarks.landmark[0]
        wrist_x = int(wrist.x * width)
        wrist_y = int(wrist.y * height)
        
        # Check if wrist is in steering wheel region
        is_in_region = x1 <= wrist_x <= x2 and y1 <= wrist_y <= y2
        
        return is_in_region, (wrist_x, wrist_y)
    
    def classify_hand_side(self, hand_landmarks, handedness):
        """Classify if hand is left or right"""
        # MediaPipe provides handedness information
        if handedness.classification[0].label == "Left":
            return "right"  # MediaPipe's "Left" means right hand (mirrored)
        else:
            return "left"   # MediaPipe's "Right" means left hand (mirrored)
    
    def analyze_grip_quality(self, hand_landmarks):
        """Analyze quality of grip on steering wheel"""
        # Get key landmarks
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]
        
        wrist = hand_landmarks.landmark[0]
        
        # Calculate grip spread
        fingertips = [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]
        
        # Calculate average distance from wrist to fingertips
        total_distance = 0
        for tip in fingertips:
            distance = np.sqrt((tip.x - wrist.x)**2 + (tip.y - wrist.y)**2)
            total_distance += distance
        
        avg_distance = total_distance / len(fingertips)
        
        # Simple grip quality heuristic
        if avg_distance > 0.15:
            return "loose"
        elif avg_distance > 0.10:
            return "normal"
        else:
            return "tight"
    
    def detect_hand_positions(self, frame):
        """Main hand position detection function"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # Reset hand detection state
        self.hands_on_wheel = {"left": False, "right": False}
        self.hand_positions = {"left": None, "right": None}
        self.hands_detected = 0
        
        if not self.steering_wheel_region:
            self.set_steering_wheel_region(frame.shape)
        
        # Draw steering wheel region
        x1, y1, x2, y2 = self.steering_wheel_region
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
        cv2.putText(frame, "Steering Wheel Area", (x1, y1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Check if hand is on steering wheel
                on_wheel, wrist_pos = self.is_hand_on_steering_wheel(hand_landmarks, frame.shape)
                
                if on_wheel:
                    hand_side = self.classify_hand_side(hand_landmarks, handedness)
                    grip_quality = self.analyze_grip_quality(hand_landmarks)
                    
                    self.hands_on_wheel[hand_side] = True
                    self.hand_positions[hand_side] = {
                        'position': wrist_pos,
                        'grip': grip_quality
                    }
                    self.hands_detected += 1
                    
                    # Draw hand info
                    cv2.circle(frame, wrist_pos, 5, (0, 255, 0), -1)
                    cv2.putText(frame, f"{hand_side.upper()} ({grip_quality})", 
                               (wrist_pos[0]-30, wrist_pos[1]-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Update safety counter
        if self.hands_detected < self.min_hands_on_wheel:
            self.frames_without_hands += 1
        else:
            self.frames_without_hands = 0
        
        # Draw hand position status
        hands_status = f"Hands on wheel: {self.hands_detected}/2"
        status_color = (0, 255, 0) if self.hands_detected >= self.min_hands_on_wheel else (0, 0, 255)
        
        cv2.putText(frame, hands_status, (10, 280),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Safety alert
        if self.frames_without_hands > self.consecutive_frames_threshold:
            cv2.putText(frame, "HANDS OFF WHEEL ALERT!", (10, 300),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Show individual hand status
        left_status = "LEFT: ON" if self.hands_on_wheel["left"] else "LEFT: OFF"
        right_status = "RIGHT: ON" if self.hands_on_wheel["right"] else "RIGHT: OFF"
        
        cv2.putText(frame, left_status, (10, 320),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                   (0, 255, 0) if self.hands_on_wheel["left"] else (0, 0, 255), 1)
        cv2.putText(frame, right_status, (150, 320),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   (0, 255, 0) if self.hands_on_wheel["right"] else (0, 0, 255), 1)
        
        return frame, self.hands_detected, self.hands_on_wheel.copy()
    
    def is_safe_hand_position(self):
        """Check if current hand position is safe"""
        return self.hands_detected >= self.min_hands_on_wheel
    
    def get_hand_position_score(self):
        """Get hand position safety score (0-1)"""
        if self.hands_detected >= 2:
            return 1.0
        elif self.hands_detected == 1:
            return 0.7
        else:
            # Penalize based on consecutive frames without hands
            penalty = min(1.0, self.frames_without_hands / self.consecutive_frames_threshold)
            return max(0.0, 0.5 - penalty)
    
    def calibrate_steering_wheel_region(self, frame):
        """Interactive calibration for steering wheel region"""
        # This would be used in setup mode
        height, width = frame.shape[:2]
        
        if not self.steering_wheel_region:
            self.set_steering_wheel_region(frame.shape)
        
        x1, y1, x2, y2 = self.steering_wheel_region
        
        # Draw adjustable rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, "Adjust this region to match steering wheel area", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, "Press 'c' to confirm, arrow keys to adjust", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return frame
