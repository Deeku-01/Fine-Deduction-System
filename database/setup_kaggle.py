import os
import json
import shutil

def setup_kaggle_credentials():
    """Setup Kaggle credentials from the kaggle.json file"""
    print("Setting up Kaggle credentials...")
    
    # Source kaggle.json in current directory
    source_path = "kaggle.json"
    
    if not os.path.exists(source_path):
        print(f"Error: {source_path} not found in current directory")
        return
    
    # Create .kaggle directory if it doesn't exist
    kaggle_dir = os.path.expanduser('~/.kaggle')
    os.makedirs(kaggle_dir, exist_ok=True)
    
    # Copy credentials file
    credentials_path = os.path.join(kaggle_dir, 'kaggle.json')
    shutil.copy2(source_path, credentials_path)
    
    # Set appropriate permissions
    os.chmod(credentials_path, 0o600)
    
    print("\nKaggle credentials have been set up!")
    print(f"Credentials file copied to: {credentials_path}")
    print("\nYou can now run the dataset download script.")

if __name__ == "__main__":
    setup_kaggle_credentials() 