#!/usr/bin/env python3
"""
Build script to create standalone executable for the Muxer App with bundled FFmpeg
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def check_ffmpeg_binaries():
    """Check if FFmpeg binaries are available for bundling"""
    import platform
    system = platform.system().lower()
    
    if system == 'windows':
        ffmpeg_dir = 'ffmpeg/windows'
        required_files = ['ffmpeg.exe', 'ffprobe.exe']
    elif system == 'darwin':  # macOS
        ffmpeg_dir = 'ffmpeg/macos'  
        required_files = ['ffmpeg', 'ffprobe']
    elif system == 'linux':
        ffmpeg_dir = 'ffmpeg/linux'
        required_files = ['ffmpeg', 'ffprobe']
    else:
        print(f"❌ Unsupported platform: {system}")
        return False
    
    if not os.path.exists(ffmpeg_dir):
        print(f"❌ FFmpeg directory not found: {ffmpeg_dir}")
        print("Run 'python download_ffmpeg.py' first to download FFmpeg binaries")
        return False
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(ffmpeg_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing FFmpeg files in {ffmpeg_dir}: {missing_files}")
        print("Run 'python download_ffmpeg.py' to download missing binaries")
        return False
    
    print(f"✅ FFmpeg binaries found in {ffmpeg_dir}")
    return True

def main():
    """Build the standalone executable with bundled FFmpeg"""
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check for FFmpeg binaries
    if not check_ffmpeg_binaries():
        print("\n💡 To bundle FFmpeg with your app:")
        print("1. Run: python download_ffmpeg.py")
        print("2. Then run this build script again")
        
        choice = input("\nContinue building WITHOUT bundled FFmpeg? (y/n): ").lower()
        if choice != 'y':
            print("Build cancelled.")
            sys.exit(1)
        
        print("⚠️  Building without bundled FFmpeg - users will need FFmpeg installed")
        script_name = "muxer_app.py"  # Use original script
    else:
        print("🎬 Building with bundled FFmpeg - fully portable!")
        script_name = "muxer_app_bundled.py"  # Use bundled version
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    print("Building standalone executable...")
    
    # Choose the appropriate spec file
    spec_file = "muxer_app.spec"
    
    try:
        subprocess.check_call(["pyinstaller", spec_file, "--clean"])
        print("\n✅ Build successful!")
        
        # Get the executable path
        import platform
        system = platform.system().lower()
        if system == 'windows':
            exe_path = os.path.abspath('dist/AudioVideoMuxer.exe')
        else:
            exe_path = os.path.abspath('dist/AudioVideoMuxer')
        
        print(f"📁 Executable created: {exe_path}")
        
        # Check file size
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📏 File size: {size_mb:.1f} MB")
        
        print("\n📋 Next steps:")
        print("1. Test the executable in dist/ folder")
        if check_ffmpeg_binaries():
            print("2. ✅ FFmpeg is bundled - no additional installation needed!")
        else:
            print("2. ⚠️  Users will need FFmpeg installed on their systems")
        print("3. Distribute the executable file")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()