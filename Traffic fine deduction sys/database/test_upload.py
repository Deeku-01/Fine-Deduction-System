import os
import sys
from PIL import Image
import numpy as np
from supabase import create_client, Client

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import SUPABASE_URL, SUPABASE_KEY

def create_test_image(filename, size=(300, 200)):
    """Create a simple test image"""
    # Create a random color image
    img_array = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(filename)
    return filename

def test_upload_to_buckets():
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase")

        # Create test directory if it doesn't exist
        test_dir = "static/uploads/test"
        os.makedirs(test_dir, exist_ok=True)

        # Test vehicle images bucket
        print("\nTesting vehicle-images bucket:")
        vehicle_test_image = os.path.join(test_dir, "test_vehicle.jpg")
        create_test_image(vehicle_test_image)
        try:
            with open(vehicle_test_image, 'rb') as f:
                result = supabase.storage.from_('vehicle-images').upload(
                    'test/test_vehicle.jpg',
                    f
                )
            print("✓ Successfully uploaded test image to vehicle-images bucket")
            
            # Get and print the public URL
            public_url = supabase.storage.from_('vehicle-images').get_public_url('test/test_vehicle.jpg')
            print(f"  Public URL: {public_url}")
        except Exception as e:
            print(f"✗ Error uploading to vehicle-images: {str(e)}")

        # Test challan images bucket
        print("\nTesting challan-images bucket:")
        challan_test_image = os.path.join(test_dir, "test_challan.jpg")
        create_test_image(challan_test_image)
        try:
            with open(challan_test_image, 'rb') as f:
                result = supabase.storage.from_('challan-images').upload(
                    'test/test_challan.jpg',
                    f
                )
            print("✓ Successfully uploaded test image to challan-images bucket")
            
            # Get and print the public URL
            public_url = supabase.storage.from_('challan-images').get_public_url('test/test_challan.jpg')
            print(f"  Public URL: {public_url}")
        except Exception as e:
            print(f"✗ Error uploading to challan-images: {str(e)}")

        # Clean up test files
        print("\nCleaning up test files...")
        try:
            os.remove(vehicle_test_image)
            os.remove(challan_test_image)
            print("✓ Test files cleaned up")
        except Exception as e:
            print(f"✗ Error cleaning up test files: {str(e)}")

        # List files in buckets
        print("\nListing files in buckets:")
        print("\nFiles in vehicle-images:")
        files = supabase.storage.from_('vehicle-images').list()
        for file in files:
            print(f"  - {file['name']}")

        print("\nFiles in challan-images:")
        files = supabase.storage.from_('challan-images').list()
        for file in files:
            print(f"  - {file['name']}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_upload_to_buckets() 