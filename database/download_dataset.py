import os
import sys
import kaggle
from zipfile import ZipFile
import shutil
from PIL import Image
from supabase import create_client
import io

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import SUPABASE_URL, SUPABASE_KEY

def process_image(img_path, output_path):
    """Process an image and save it as JPEG"""
    try:
        with Image.open(img_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img, mask=img.split()[1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            if max(img.size) > 1024:
                img.thumbnail((1024, 1024))
            
            # Save as JPEG
            img.save(output_path, "JPEG", quality=85)
            return True
    except Exception as e:
        print(f"Error processing image {os.path.basename(img_path)}: {str(e)}")
        return False

def download_and_process_dataset():
    """Download license plate dataset from Kaggle and process images"""
    try:
        print("Setting up directories...")
        # Create necessary directories
        dataset_dir = "datasets/license_plates"
        processed_dir = "datasets/processed"
        os.makedirs(dataset_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)

        print("\nDownloading dataset from Kaggle...")
        try:
            # Download Car License Plate Detection dataset
            kaggle.api.authenticate()
            print("Authentication successful!")
            
            # Download multiple relevant datasets
            datasets = [
                'andrewmvd/car-plate-detection',
                'andrewmvd/vehicle-detection',
                'aslanahmedov/number-plate-detection'
            ]
            
            for dataset in datasets:
                print(f"\nDownloading '{dataset}' dataset...")
                try:
                    kaggle.api.dataset_download_files(
                        dataset,
                        path=os.path.join(dataset_dir, dataset.split('/')[-1]),
                        unzip=True
                    )
                    print(f"Successfully downloaded {dataset}")
                except Exception as e:
                    print(f"Error downloading {dataset}: {str(e)}")

        except Exception as e:
            print(f"Error with Kaggle API: {str(e)}")
            return

        print("\nProcessing images...")
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Process and upload sample images
        processed_images = []
        for root, _, files in os.walk(dataset_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(root, file)
                    processed_path = os.path.join(processed_dir, f"processed_{len(processed_images)}.jpg")
                    
                    if process_image(img_path, processed_path):
                        processed_images.append(processed_path)
                        if len(processed_images) >= 20:  # Limit to 20 samples
                            break
            if len(processed_images) >= 20:
                break
            
        print(f"\nProcessed {len(processed_images)} images")
        print("Uploading to Supabase...")

        # Upload processed images
        for i, img_path in enumerate(processed_images):
            try:
                with open(img_path, 'rb') as f:
                    file_name = f'samples/vehicle_{i+1}.jpg'
                    supabase.storage.from_('vehicle-images').upload(
                        file_name,
                        f
                    )
                print(f"✓ Uploaded vehicle_{i+1}.jpg")
            except Exception as e:
                print(f"✗ Error uploading {os.path.basename(img_path)}: {str(e)}")

        print("\nCleaning up...")
        # Clean up downloaded and processed files
        shutil.rmtree(dataset_dir, ignore_errors=True)
        shutil.rmtree(processed_dir, ignore_errors=True)

        print("\nListing uploaded samples:")
        try:
            files = supabase.storage.from_('vehicle-images').list('samples')
            print(f"\nFound {len(files)} sample images:")
            for file in files:
                url = supabase.storage.from_('vehicle-images').get_public_url(f"samples/{file['name']}")
                print(f"  - {file['name']}")
                print(f"    URL: {url}")
        except Exception as e:
            print(f"Error listing files: {str(e)}")

        print("\nDataset processing completed!")
        print("\nYou can use these images to test the license plate detection system.")
        print("The images are available in the Supabase storage bucket 'vehicle-images' under the 'samples' folder.")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure you have:")
        print("1. Kaggle API credentials in ~/.kaggle/kaggle.json")
        print("2. Required packages installed (kaggle, Pillow)")
        print("3. Stable internet connection")

if __name__ == "__main__":
    download_and_process_dataset() 