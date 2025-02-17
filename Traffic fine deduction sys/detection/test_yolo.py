import os
import sys
from ultralytics import YOLO
import cv2

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import YOLO_MODEL_PATH

def test_yolo():
    try:
        # Initialize YOLO model
        if not os.path.exists(YOLO_MODEL_PATH):
            print(f"Model not found at {YOLO_MODEL_PATH}")
            print("Downloading YOLOv8n model...")
            model = YOLO('yolov8n.pt')  # This will download the model
            print("Model downloaded successfully!")
        else:
            model = YOLO(YOLO_MODEL_PATH)
            print("Loaded existing YOLO model")

        print("\nYOLO setup completed successfully!")
        print("\nNote: The model will need to be fine-tuned for license plate detection.")
        print("You can use the following steps to fine-tune the model:")
        print("1. Collect license plate images")
        print("2. Label the images with license plate bounding boxes")
        print("3. Train the model on your dataset")
        print("4. Export the model to the models directory")

    except Exception as e:
        print(f"Error setting up YOLO: {e}")

if __name__ == "__main__":
    test_yolo() 