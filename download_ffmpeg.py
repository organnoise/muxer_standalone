#!/usr/bin/env python3
"""
Script to download FFmpeg binaries for bundling with the muxer app
"""

import os
import sys
import zipfile
import requests
import platform
from pathlib import Path
import tarfile

def download_file(url, filename):
    """Download a file with progress indicator"""
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='', flush=True)
    print(f"\n✅ Downloaded {filename}")

def extract_ffmpeg_windows(zip_path, extract_to):
    """Extract FFmpeg from Windows zip file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if member.endswith(('ffmpeg.exe', 'ffprobe.exe')):
                # Extract just the executable, not the full path
                filename = os.path.basename(member)
                with zip_ref.open(member) as source, open(os.path.join(extract_to, filename), 'wb') as target:
                    target.write(source.read())
                print(f"✅ Extracted {filename}")

def extract_ffmpeg_unix(tar_path, extract_to):
    """Extract FFmpeg from Unix tar.xz file"""
    with tarfile.open(tar_path, 'r:xz') as tar_ref:
        for member in tar_ref.getmembers():
            if member.name.endswith(('/ffmpeg', '/ffprobe')) and member.isfile():
                filename = os.path.basename(member.name)
                member.name = filename  # Change the extraction path
                tar_ref.extract(member, extract_to)
                # Make executable
                os.chmod(os.path.join(extract_to, filename), 0o755)
                print(f"✅ Extracted {filename}")

def download_windows_ffmpeg():
    """Download FFmpeg for Windows"""
    # Using a reliable Windows build from gyan.dev
    url = "https://github.com/GyanD/codexffmpeg/releases/download/6.1/ffmpeg-6.1-essentials_build.zip"
    zip_path = "ffmpeg_windows.zip"
    
    os.makedirs("ffmpeg/windows", exist_ok=True)
    
    try:
        download_file(url, zip_path)
        extract_ffmpeg_windows(zip_path, "ffmpeg/windows")
        os.remove(zip_path)
        print("✅ Windows FFmpeg setup complete")
    except Exception as e:
        print(f"❌ Error downloading Windows FFmpeg: {e}")
        print("Manual download: https://ffmpeg.org/download.html#build-windows")

def download_macos_ffmpeg():
    """Download FFmpeg for macOS"""
    # Using static builds from evermeet.cx
    ffmpeg_url = "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
    ffprobe_url = "https://evermeet.cx/ffmpeg/ffprobe-6.1.zip"
    
    os.makedirs("ffmpeg/macos", exist_ok=True)
    
    try:
        # Download ffmpeg
        download_file(ffmpeg_url, "ffmpeg_mac.zip")
        with zipfile.ZipFile("ffmpeg_mac.zip", 'r') as zip_ref:
            zip_ref.extract("ffmpeg", "ffmpeg/macos")
        os.chmod("ffmpeg/macos/ffmpeg", 0o755)
        os.remove("ffmpeg_mac.zip")
        
        # Download ffprobe
        download_file(ffprobe_url, "ffprobe_mac.zip")
        with zipfile.ZipFile("ffprobe_mac.zip", 'r') as zip_ref:
            zip_ref.extract("ffprobe", "ffmpeg/macos")
        os.chmod("ffmpeg/macos/ffprobe", 0o755)
        os.remove("ffprobe_mac.zip")
        
        print("✅ macOS FFmpeg setup complete")
    except Exception as e:
        print(f"❌ Error downloading macOS FFmpeg: {e}")
        print("Manual download: brew install ffmpeg or https://evermeet.cx/ffmpeg/")

def download_linux_ffmpeg():
    """Instructions for Linux FFmpeg"""
    print("🐧 Linux FFmpeg Setup:")
    print("Due to different architectures and distributions, please manually add FFmpeg:")
    print("1. Install FFmpeg: sudo apt install ffmpeg (Ubuntu/Debian)")
    print("2. Copy binaries: ")
    print("   cp /usr/bin/ffmpeg ffmpeg/linux/")
    print("   cp /usr/bin/ffprobe ffmpeg/linux/")
    print("3. Or download static builds from: https://johnvansickle.com/ffmpeg/")
    
    os.makedirs("ffmpeg/linux", exist_ok=True)

def main():
    """Main function to download FFmpeg for current platform or all platforms"""
    print("🎬 FFmpeg Download Script for Muxer App")
    print("=" * 40)
    
    # Install requests if not available
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    current_platform = platform.system().lower()
    
    print(f"Current platform: {current_platform}")
    print("\nChoose download option:")
    print("1. Download for current platform only")
    print("2. Download for all platforms")
    print("3. Download for specific platform")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        if current_platform == "windows":
            download_windows_ffmpeg()
        elif current_platform == "darwin":
            download_macos_ffmpeg()
        elif current_platform == "linux":
            download_linux_ffmpeg()
        else:
            print(f"❌ Unsupported platform: {current_platform}")
    
    elif choice == "2":
        print("Downloading for all platforms...")
        download_windows_ffmpeg()
        download_macos_ffmpeg()
        download_linux_ffmpeg()
    
    elif choice == "3":
        print("Available platforms:")
        print("1. Windows")
        print("2. macOS") 
        print("3. Linux")
        platform_choice = input("Enter platform (1-3): ").strip()
        
        if platform_choice == "1":
            download_windows_ffmpeg()
        elif platform_choice == "2":
            download_macos_ffmpeg()
        elif platform_choice == "3":
            download_linux_ffmpeg()
        else:
            print("❌ Invalid choice")
    
    else:
        print("❌ Invalid choice")
    
    print("\n📁 FFmpeg files structure:")
    for root, dirs, files in os.walk("ffmpeg"):
        level = root.replace("ffmpeg", '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

if __name__ == "__main__":
    main()