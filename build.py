"""
Build script for StarSticks
Creates a portable single-file .exe using PyInstaller
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path


def clean_build_dirs():
    """Clean up previous build directories"""
    print("Cleaning previous build directories...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")


def build_exe():
    """Build the executable using PyInstaller"""
    print("\nBuilding StarSticks.exe...")
    print("This may take a few minutes...\n")

    try:
        # Run PyInstaller with the spec file
        result = subprocess.run(
            ['pyinstaller', '--clean', 'StarSticks.spec'],
            check=True,
            capture_output=False
        )

        print("\n" + "="*60)
        print("BUILD SUCCESSFUL!")
        print("="*60)
        print("\nPortable executable created:")
        print("  Location: dist/StarSticks.exe")
        print(f"  Size: {os.path.getsize('dist/StarSticks.exe') / (1024*1024):.1f} MB")
        print("\nYou can now run StarSticks.exe directly!")
        print("="*60)

        return True

    except subprocess.CalledProcessError as e:
        print("\n" + "="*60)
        print("BUILD FAILED!")
        print("="*60)
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print("\n" + "="*60)
        print("ERROR: PyInstaller not found!")
        print("="*60)
        print("Please install PyInstaller first:")
        print("  pip install pyinstaller")
        return False


def main():
    """Main build process"""
    print("="*60)
    print("StarSticks Build Script")
    print("="*60)
    print("Building portable single-file .exe\n")

    # Check if spec file exists
    if not os.path.exists('StarSticks.spec'):
        print("ERROR: StarSticks.spec not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)

    # Clean previous builds
    clean_build_dirs()

    # Build the executable
    success = build_exe()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
