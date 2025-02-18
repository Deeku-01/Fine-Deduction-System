import os
import sys
from supabase import create_client, Client

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import SUPABASE_URL, SUPABASE_KEY

def setup_supabase():
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully connected to Supabase!")

        # Required bucket names
        required_buckets = ['vehicle-images', 'challan-images']

        # List and verify buckets
        try:
            print("\nAttempting to list buckets...")
            buckets = supabase.storage.list_buckets()
            print(f"Found {len(buckets)} buckets:")
            
            # Print all bucket details for debugging
            for bucket in buckets:
                print(f"\nBucket details:")
                print(f"  Name: {bucket.name}")
                print(f"  ID: {bucket.id}")
                print(f"  Public: {bucket.public}")
            
            # Get existing bucket names
            existing_buckets = [bucket.name for bucket in buckets]
            print(f"\nExisting bucket names: {existing_buckets}")
            
            # Check required buckets
            for bucket_name in required_buckets:
                if bucket_name in existing_buckets:
                    print(f"\n✓ '{bucket_name}' bucket exists")
                    # Test bucket access
                    try:
                        print(f"  Testing access to '{bucket_name}'...")
                        files = supabase.storage.from_(bucket_name).list()
                        print(f"  ✓ Can list files in '{bucket_name}'")
                        if files:
                            print(f"    Files in {bucket_name}:")
                            for file in files:
                                print(f"    - {file['name']}")
                        else:
                            print(f"    No files in bucket yet")
                    except Exception as e:
                        print(f"  ✗ Error accessing '{bucket_name}': {str(e)}")
                        print("  Please check bucket permissions and RLS policies")
                else:
                    print(f"\n✗ '{bucket_name}' bucket is missing!")
                    print(f"  Please verify the bucket name is exactly '{bucket_name}' (case-sensitive)")
                    print(f"  If not found, create it in Supabase dashboard:")
                    print(f"  1. Go to https://supabase.com/dashboard")
                    print(f"  2. Select your project")
                    print(f"  3. Click on 'Storage' in the left sidebar")
                    print(f"  4. Click 'Create bucket'")
                    print(f"  5. Name it '{bucket_name}' and make it public")

        except Exception as e:
            print(f"\nError listing buckets: {str(e)}")
            print("Full error details:", e)
            print("\nPlease check:")
            print("1. Storage is enabled in your Supabase project")
            print("2. Your API key has storage permissions")
            print("3. RLS policies are configured correctly")
            print(f"\nAPI URL being used: {SUPABASE_URL}")
            print("API Key: [hidden for security]")

        print("\nSupabase setup check completed!")

    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        print("Full error details:", e)
        print("\nPlease verify your Supabase credentials in config.py:")
        print(f"URL: {SUPABASE_URL}")
        print("API Key: [hidden for security]")

def test_upload(supabase: Client, bucket_name: str, test_file_path: str):
    """Test upload functionality for a bucket"""
    try:
        with open(test_file_path, 'rb') as f:
            file_name = os.path.basename(test_file_path)
            result = supabase.storage.from_(bucket_name).upload(file_name, f)
            print(f"Successfully uploaded test file to {bucket_name}")
            return True
    except Exception as e:
        print(f"Error uploading to {bucket_name}: {e}")
        return False

if __name__ == "__main__":
    setup_supabase() 