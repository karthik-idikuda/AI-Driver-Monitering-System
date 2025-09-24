"""
Facial Recognition Module
Recognizes authorized drivers using face recognition
"""

import cv2
import numpy as np
import os
import pickle
import logging

# Try to import face_recognition, fall back to simple detection if not available
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition not available, using simple face detection")

logger = logging.getLogger(__name__)

class FacialRecognition:
    def __init__(self, known_faces_dir="data/known_faces", tolerance=0.6):
        self.known_faces_dir = known_faces_dir
        self.tolerance = tolerance
        
        # Storage for known faces
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Current detection state
        self.current_driver = "Unknown"
        self.recognition_confidence = 0.0
        self.is_authorized = False
        
        # Create directories if they don't exist
        os.makedirs(known_faces_dir, exist_ok=True)
        
        # Load known faces
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known faces from directory"""
        try:
            # Look for saved encodings
            encodings_file = os.path.join(self.known_faces_dir, "face_encodings.pkl")
            
            if os.path.exists(encodings_file):
                with open(encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                logger.info(f"Loaded {len(self.known_face_names)} known faces")
            else:
                # Load from individual image files
                self.load_faces_from_images()
                
        except Exception as e:
            logger.error(f"Error loading known faces: {str(e)}")
    
    def load_faces_from_images(self):
        """Load faces from individual image files"""
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp')
        
        for filename in os.listdir(self.known_faces_dir):
            if filename.lower().endswith(supported_formats):
                try:
                    # Extract name from filename (without extension)
                    name = os.path.splitext(filename)[0]
                    
                    # Load and encode face
                    image_path = os.path.join(self.known_faces_dir, filename)
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(name)
                        logger.info(f"Loaded face for {name}")
                    else:
                        logger.warning(f"No face found in {filename}")
                        
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")
        
        # Save encodings for faster loading next time
        self.save_face_encodings()
    
    def save_face_encodings(self):
        """Save face encodings to file"""
        try:
            encodings_file = os.path.join(self.known_faces_dir, "face_encodings.pkl")
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            with open(encodings_file, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Face encodings saved successfully")
        except Exception as e:
            logger.error(f"Error saving face encodings: {str(e)}")
    
    def add_new_face(self, frame, name):
        """Add a new face to the known faces database"""
        try:
            # Find face in current frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            if face_encodings:
                # Add to known faces
                self.known_face_encodings.append(face_encodings[0])
                self.known_face_names.append(name)
                
                # Save image
                face_image_path = os.path.join(self.known_faces_dir, f"{name}.jpg")
                cv2.imwrite(face_image_path, frame)
                
                # Save encodings
                self.save_face_encodings()
                
                logger.info(f"Added new face for {name}")
                return True
            else:
                logger.warning("No face detected for adding")
                return False
                
        except Exception as e:
            logger.error(f"Error adding new face: {str(e)}")
            return False
    
    def recognize_face(self, frame):
        """Main face recognition function"""
        if not self.known_face_encodings:
            return frame, "Unknown", 0.0, False
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces in current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        self.current_driver = "Unknown"
        self.recognition_confidence = 0.0
        self.is_authorized = False
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding, tolerance=self.tolerance)
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding)
            
            if matches and len(face_distances) > 0:
                # Find best match
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    self.current_driver = self.known_face_names[best_match_index]
                    self.recognition_confidence = 1.0 - face_distances[best_match_index]
                    self.is_authorized = True
            
            # Draw face rectangle
            color = (0, 255, 0) if self.is_authorized else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw name and confidence
            label = f"{self.current_driver} ({self.recognition_confidence:.2f})"
            cv2.putText(frame, label, (left, top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw authorization status
        status_text = f"Driver: {self.current_driver}"
        status_color = (0, 255, 0) if self.is_authorized else (0, 0, 255)
        
        cv2.putText(frame, status_text, (10, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        if not self.is_authorized and face_locations:
            cv2.putText(frame, "UNAUTHORIZED DRIVER!", (10, 220),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame, self.current_driver, self.recognition_confidence, self.is_authorized
    
    def get_known_drivers(self):
        """Get list of known driver names"""
        return self.known_face_names.copy()
    
    def remove_driver(self, name):
        """Remove a driver from the database"""
        try:
            if name in self.known_face_names:
                index = self.known_face_names.index(name)
                del self.known_face_names[index]
                del self.known_face_encodings[index]
                
                # Remove image file
                image_path = os.path.join(self.known_faces_dir, f"{name}.jpg")
                if os.path.exists(image_path):
                    os.remove(image_path)
                
                # Save updated encodings
                self.save_face_encodings()
                
                logger.info(f"Removed driver {name}")
                return True
            else:
                logger.warning(f"Driver {name} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error removing driver: {str(e)}")
            return False
