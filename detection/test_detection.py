import os
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import requests
from PIL import Image
from io import BytesIO
from supabase import create_client

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import SUPABASE_URL, SUPABASE_KEY, YOLO_MODEL_PATH

def download_image(url, save_path):
    """Download image from URL and save it"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.save(save_path)
        return True
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False

def test_license_plate_detection():
    try:
        print("Initializing YOLO model...")
        if not os.path.exists(YOLO_MODEL_PATH):
            print("Downloading YOLOv8n model...")
            model = YOLO('yolov8n.pt')
            # Save model for future use
            model.save(YOLO_MODEL_PATH)
        else:
            model = YOLO(YOLO_MODEL_PATH)
        print("Model loaded successfully!")

        # Create test directory
        test_dir = "static/test_detection"
        results_dir = "static/test_results"
        os.makedirs(test_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)

        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        print("\nFetching sample images from Supabase...")
        try:
            files = supabase.storage.from_('vehicle-images').list('samples')
            for file in files:
                # Get image URL
                url = supabase.storage.from_('vehicle-images').get_public_url(f"samples/{file['name']}")
                image_path = os.path.join(test_dir, file['name'])
                
                # Download image
                if download_image(url, image_path):
                    print(f"\nProcessing {file['name']}...")
                    
                    # Run detection
                    results = model(image_path)
                    
                    # Process results
                    for i, result in enumerate(results):
                        # Get the original image
                        img = cv2.imread(image_path)
                        
                        # Draw bounding boxes
                        for box in result.boxes:
                            # Get box coordinates
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            conf = float(box.conf[0])
                            
                            # Draw rectangle
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            
                            # Add confidence text
                            text = f"License Plate: {conf:.2f}"
                            cv2.putText(img, text, (x1, y1-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                            
                            # Extract license plate region
                            plate_img = img[y1:y2, x1:x2]
                            if plate_img.size > 0:
                                plate_path = os.path.join(results_dir, f"plate_{file['name']}")
                                cv2.imwrite(plate_path, plate_img)
                                print(f"  Extracted plate saved to: {plate_path}")
                        
                        # Save result image
                        result_path = os.path.join(results_dir, f"result_{file['name']}")
                        cv2.imwrite(result_path, img)
                        print(f"  Detection result saved to: {result_path}")

        except Exception as e:
            print(f"Error processing images: {str(e)}")

        print("\nTest completed! Check the results in:", results_dir)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_license_plate_detection() 