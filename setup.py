"""
Setup script to create necessary directories and verify installation.
"""

from pathlib import Path
import sys

def setup_project():
    """Create necessary directories."""
    directories = ['data', 'models', 'outputs']
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created/verified directory: {dir_name}/")
    
    print("\n✓ Project structure ready!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Generate data and train models: python src/train.py")
    print("3. Launch dashboard: streamlit run dashboard.py")

if __name__ == '__main__':
    setup_project()
