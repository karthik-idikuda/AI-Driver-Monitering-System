# Driver Monitoring System

## Overview
A comprehensive computer vision-based system designed to enhance road safety by monitoring driver behavior in real-time. It detects drowsiness, distraction, seatbelt usage, and emotional state to prevent accidents and ensure compliance with safety regulations.

## Features
-   **Drowsiness Detection**: Analyzes eye closure patterns (EAR) to alert fatigued drivers.
-   **Distraction Alert**: Tracks head pose and gaze to ensure the driver is looking at the road.
-   **Facial Recognition**: Identifies authorized drivers and logs access.
-   **Seatbelt Check**: automated visual verification of seatbelt compliance.
-   **Emotion Analysis**: Detects stress or anger using facial expression analysis.

## Technology Stack
-   **Vision**: OpenCV, Dlib, MediaPipe.
-   **AI**: TensorFlow / Keras for emotion models.
-   **GUI**: Tkinter for the monitoring dashboard.
-   **Language**: Python 3.8+.

## Usage Flow
1.  **Initialize**: System starts and accesses the dashboard camera.
2.  **Authenticate**: Facial recognition verifies the driver's identity.
3.  **Monitor**: Continuous analysis of face, eyes, and body posture.
4.  **Alert**: Immediate audio-visual warnings if unsafe behavior is detected.

## Quick Start
```bash
# Clone the repository
git clone https://github.com/Nytrynox/AI-Driver-Monitoring-System.git

# Install dependencies
pip install -r requirements.txt

# Download required models
python download_models.py

# Run the system in GUI mode
python main.py --mode gui
```

## License
MIT License

## Author
**Karthik Idikuda**
