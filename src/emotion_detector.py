"""
Emotion Detection Module
Detects driver emotions using facial expression analysis
"""

import cv2
import numpy as np
import logging

# Try to import tensorflow, fall back to simple detection if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("tensorflow not available, using simple emotion detection")

logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self):
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
        self.model = None
        self.face_cascade = cv2.CascadeClassifier()
        
        # Current emotion state
        self.current_emotion = "Neutral"
        self.emotion_confidence = 0.0
        self.emotion_history = []
        self.history_size = 30  # frames to keep in history
        
        # Alert thresholds
        self.stress_emotions = ['Angry', 'Fear', 'Sad']
        self.positive_emotions = ['Happy', 'Surprise']
        
    def load_model(self, model_path, face_cascade_path):
        """Load emotion detection model and face cascade"""
        try:
            # Load face cascade
            self.face_cascade.load(face_cascade_path)
            
            # Try to load custom emotion model
            if model_path.endswith('.h5'):
                try:
                    self.model = keras.models.load_model(model_path)
                    logger.info("Custom emotion model loaded successfully")
                except:
                    logger.warning("Custom model not found, using simple emotion detection")
                    self.model = None
            else:
                self.model = None
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading emotion detection model: {str(e)}")
            return False
    
    def preprocess_face(self, face_img):
        """Preprocess face image for emotion detection"""
        # Resize to 48x48 (common input size for emotion models)
        face_img = cv2.resize(face_img, (48, 48))
        
        # Convert to grayscale if needed
        if len(face_img.shape) == 3:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Normalize pixel values
        face_img = face_img.astype(np.float32) / 255.0
        
        # Reshape for model input
        face_img = np.expand_dims(face_img, axis=0)
        face_img = np.expand_dims(face_img, axis=-1)
        
        return face_img
    
    def detect_emotion_simple(self, face_img):
        """Simple emotion detection using basic features"""
        # Convert to grayscale
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
        
        # Simple feature extraction
        height, width = gray.shape
        
        # Divide face into regions
        upper_face = gray[:height//2, :]
        lower_face = gray[height//2:, :]
        
        # Calculate basic statistics
        upper_mean = np.mean(upper_face)
        lower_mean = np.mean(lower_face)
        overall_std = np.std(gray)
        
        # Simple heuristic classification
        if overall_std < 20:
            emotion = "Neutral"
            confidence = 0.6
        elif lower_mean > upper_mean * 1.1:
            emotion = "Happy"
            confidence = 0.7
        elif lower_mean < upper_mean * 0.9:
            emotion = "Sad"
            confidence = 0.6
        else:
            emotion = "Neutral"
            confidence = 0.5
        
        return emotion, confidence
    
    def detect_emotion_model(self, face_img):
        """Detect emotion using trained model"""
        try:
            processed_face = self.preprocess_face(face_img)
            predictions = self.model.predict(processed_face, verbose=0)
            
            # Get emotion with highest confidence
            emotion_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][emotion_idx])
            emotion = self.emotion_labels[emotion_idx]
            
            return emotion, confidence
            
        except Exception as e:
            logger.error(f"Error in model-based emotion detection: {str(e)}")
            return self.detect_emotion_simple(face_img)
    
    def detect_emotion(self, frame):
        """Main emotion detection function"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return frame, self.current_emotion, self.emotion_confidence
        
        # Process the largest face
        (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
        face_img = frame[y:y+h, x:x+w]
        
        # Detect emotion
        if self.model is not None:
            emotion, confidence = self.detect_emotion_model(face_img)
        else:
            emotion, confidence = self.detect_emotion_simple(face_img)
        
        # Update emotion state
        self.current_emotion = emotion
        self.emotion_confidence = confidence
        
        # Update history
        self.emotion_history.append(emotion)
        if len(self.emotion_history) > self.history_size:
            self.emotion_history.pop(0)
        
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Draw emotion label
        label = f"{emotion} ({confidence:.2f})"
        cv2.putText(frame, label, (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw emotion status
        cv2.putText(frame, f"Emotion: {emotion}", (10, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Check for stress emotions
        if emotion in self.stress_emotions and confidence > 0.6:
            cv2.putText(frame, "STRESS DETECTED!", (10, 260),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, emotion, confidence
    
    def get_emotion_statistics(self):
        """Get emotion statistics from history"""
        if not self.emotion_history:
            return {}
        
        # Count emotions
        emotion_counts = {}
        for emotion in self.emotion_labels:
            emotion_counts[emotion] = self.emotion_history.count(emotion)
        
        # Calculate percentages
        total = len(self.emotion_history)
        emotion_percentages = {emotion: (count/total)*100 
                             for emotion, count in emotion_counts.items()}
        
        return emotion_percentages
    
    def is_driver_stressed(self):
        """Check if driver shows signs of stress"""
        if len(self.emotion_history) < 10:
            return False
        
        # Check recent emotions
        recent_emotions = self.emotion_history[-10:]
        stress_count = sum(1 for emotion in recent_emotions if emotion in self.stress_emotions)
        
        return stress_count >= 5  # 50% of recent emotions are stress-related
    
    def reset_history(self):
        """Reset emotion history"""
        self.emotion_history = []
