import os

def create_directories():
    directories = [
        'static',
        'static/uploads',
        'models',
        'static/uploads/temp'
    ]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            else:
                print(f"Directory already exists: {directory}")
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")

if __name__ == "__main__":
    print("Setting up directories...")
    create_directories()
    print("\nDirectory setup completed!") 