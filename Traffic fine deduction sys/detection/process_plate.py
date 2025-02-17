import os
import sys
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
from PIL import Image
import json

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import YOLO_MODEL_PATH

class LicensePlateProcessor:
    def __init__(self):
        """Initialize YOLO model and EasyOCR reader"""
        # Initialize YOLO
        print("Loading YOLO model...")
        self.model = YOLO(YOLO_MODEL_PATH)
        
        # Initialize EasyOCR with English
        print("Loading OCR model...")
        self.reader = easyocr.Reader(['en'])
        
        print("Models loaded successfully!")

    def process_image(self, image_path, save_results=True):
        """Process an image to detect and read license plates"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image at {image_path}")

            # Run YOLO detection
            results = self.model(img)
            
            detections = []
            
            # Process each detection
            for result in results:
                for box in result.boxes:
                    # Get coordinates and confidence
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    # Extract plate region
                    plate_img = img[y1:y2, x1:x2]
                    if plate_img.size == 0:
                        continue
                    
                    # Read text from plate
                    ocr_result = self.reader.readtext(plate_img)
                    
                    # Process OCR results
                    plate_text = ""
                    plate_conf = 0.0
                    if ocr_result:
                        # Combine all detected text
                        texts = []
                        total_conf = 0
                        for detection in ocr_result:
                            text = detection[1]
                            conf = detection[2]
                            texts.append(text)
                            total_conf += conf
                        
                        plate_text = " ".join(texts)
                        plate_conf = total_conf / len(ocr_result)
                    
                    detection_info = {
                        'bbox': [x1, y1, x2, y2],
                        'detection_confidence': conf,
                        'plate_text': plate_text,
                        'ocr_confidence': plate_conf
                    }
                    detections.append(detection_info)
                    
                    # Draw on image if saving results
                    if save_results:
                        # Draw bounding box
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Add text with confidence
                        text = f"{plate_text} ({plate_conf:.2f})"
                        cv2.putText(img, text, (x1, y1-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Save results if requested
            if save_results and detections:
                # Create results directory if it doesn't exist
                results_dir = "static/processed_results"
                os.makedirs(results_dir, exist_ok=True)
                
                # Save annotated image
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                result_path = os.path.join(results_dir, f"processed_{base_name}.jpg")
                cv2.imwrite(result_path, img)
                
                # Save detection info as JSON
                json_path = os.path.join(results_dir, f"info_{base_name}.json")
                with open(json_path, 'w') as f:
                    json.dump(detections, f, indent=2)
                
                print(f"Results saved to {results_dir}")
            
            return detections

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return []

def test_processor():
    """Test the license plate processor on sample images"""
    processor = LicensePlateProcessor()
    
    # Process images in test_detection directory
    test_dir = "static/test_detection"
    if not os.path.exists(test_dir):
        print(f"Test directory not found: {test_dir}")
        return
    
    print("\nProcessing test images...")
    for filename in os.listdir(test_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(test_dir, filename)
            print(f"\nProcessing {filename}...")
            
            detections = processor.process_image(image_path)
            
            # Print results
            if detections:
                print(f"Found {len(detections)} license plates:")
                for i, detection in enumerate(detections, 1):
                    print(f"  {i}. Text: {detection['plate_text']}")
                    print(f"     Confidence: {detection['ocr_confidence']:.2f}")
            else:
                print("No license plates detected")

if __name__ == "__main__":
    test_processor() 