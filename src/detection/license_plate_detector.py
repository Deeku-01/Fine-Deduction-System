import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
from config.config import YOLO_MODEL_PATH, CONFIDENCE_THRESHOLD
import os

class LicensePlateDetector:
    def __init__(self, model_path: str = YOLO_MODEL_PATH):
        """Initialize the license plate detector with YOLO model and EasyOCR"""
        # Initialize YOLO
        if not os.path.exists(model_path):
            print("Downloading YOLOv8 model...")
            # Download a pre-trained model for license plate detection
            self.model = YOLO('yolov8n.pt')  # Using nano model as base
            # Save the model for future use
            self.model.save(model_path)
        else:
            self.model = YOLO(model_path)
            
        # Initialize EasyOCR with English
        self.reader = easyocr.Reader(['en'])
        print("License plate detector initialized successfully!")

    def detect_license_plate(self, image_path: str):
        """
        Detect license plate in an image and return the coordinates and confidence
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (license_plate_image, confidence, bbox)
        """
        try:
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image at {image_path}")

            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Run inference with increased confidence threshold
            results = self.model.predict(
                source=image_rgb,
                conf=CONFIDENCE_THRESHOLD,
                iou=0.5,
                verbose=False
            )
            
            # Process results
            highest_conf = 0
            best_bbox = None
            license_plate_img = None

            if len(results) > 0 and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    confidence = float(box.conf[0])
                    if confidence > highest_conf:
                        highest_conf = confidence
                        best_bbox = box.xyxy[0].cpu().numpy()  # Get box coordinates
            
            if best_bbox is not None:
                # Extract license plate region
                x1, y1, x2, y2 = map(int, best_bbox)
                # Add padding around the detected region
                padding = 5
                h, w = image.shape[:2]
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)
                license_plate_img = image[y1:y2, x1:x2]
                
                return license_plate_img, highest_conf, best_bbox
            
            return None, 0, None

        except Exception as e:
            print(f"Error in detect_license_plate: {str(e)}")
            return None, 0, None

    def preprocess_plate_image(self, plate_image):
        """
        Preprocess the license plate image for better OCR results
        
        Args:
            plate_image: numpy array of the license plate image
            
        Returns:
            preprocessed_image: processed numpy array
        """
        try:
            if plate_image is None:
                return None

            # Convert to grayscale
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to remove noise while keeping edges sharp
            denoised = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Resize image if too small
            min_width = 100
            if morph.shape[1] < min_width:
                scale = min_width / morph.shape[1]
                morph = cv2.resize(morph, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            return morph

        except Exception as e:
            print(f"Error in preprocess_plate_image: {str(e)}")
            return None

    def read_plate_text(self, plate_image):
        """
        Read text from a license plate image using OCR
        
        Args:
            plate_image: preprocessed plate image
            
        Returns:
            str: detected license plate text
        """
        try:
            if plate_image is None:
                return ""
            
            # Read text using EasyOCR with custom configuration
            results = self.reader.readtext(
                plate_image,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                batch_size=1,
                detail=1,
                paragraph=False
            )
            
            if not results:
                return ""
            
            # Process and combine detected text
            texts = []
            total_conf = 0
            
            for detection in results:
                bbox, text, conf = detection
                # Filter out low confidence detections
                if conf > 0.3:  # Lower confidence threshold for individual characters
                    # Clean up the text
                    cleaned_text = ''.join(c for c in text if c.isalnum())
                    if cleaned_text:
                        texts.append(cleaned_text)
                        total_conf += conf
            
            if not texts:
                return ""
            
            # Combine all detected text parts
            final_text = ''.join(texts)
            
            # Additional validation
            if len(final_text) < 4:  # Most license plates have at least 4 characters
                return ""
                
            return final_text

        except Exception as e:
            print(f"Error in read_plate_text: {str(e)}")
            return ""

    def save_detection_result(self, image_path: str, output_path: str):
        """
        Save the detection result with bounding box drawn
        
        Args:
            image_path (str): Path to the input image
            output_path (str): Path to save the output image
        """
        try:
            # Read original image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Detect license plate
            plate_img, conf, bbox = self.detect_license_plate(image_path)
            
            if bbox is not None:
                # Draw bounding box
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Process and read text
                if plate_img is not None:
                    processed_plate = self.preprocess_plate_image(plate_img)
                    plate_text = self.read_plate_text(processed_plate)
                    
                    # Add text and confidence
                    text = f"Plate: {plate_text} ({conf:.2f})"
                    cv2.putText(image, text, (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                # Save the result
                cv2.imwrite(output_path, image)
                return True
            
            return False

        except Exception as e:
            print(f"Error in save_detection_result: {str(e)}")
            return False

# Usage example:
# detector = LicensePlateDetector()
# plate_img, confidence, bbox = detector.detect_license_plate('path/to/image.jpg')
# if plate_img is not None:
#     processed_plate = detector.preprocess_plate_image(plate_img)
#     detector.save_detection_result('path/to/image.jpg', 'path/to/output.jpg') 