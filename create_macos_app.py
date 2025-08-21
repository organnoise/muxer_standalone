#!/usr/bin/env python3
"""
Create a proper macOS .app bundle for the muxer
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def create_app_bundle():
    """Create a proper .app bundle for macOS"""
    
    print("Creating macOS .app bundle...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Create the .app bundle using PyInstaller
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import platform
import os

block_cipher = None

# FFmpeg binaries for macOS
binaries = []
ffmpeg_dir = 'ffmpeg/macos'
if os.path.exists(ffmpeg_dir):
    binaries = [
        (os.path.join(ffmpeg_dir, 'ffmpeg'), '.'),
        (os.path.join(ffmpeg_dir, 'ffprobe'), '.')
    ]

print(f"Including FFmpeg binaries: {binaries}")

a = Analysis(
    ['muxer_app_bundled.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AudioVideoMuxer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AudioVideoMuxer',
)

app = BUNDLE(
    coll,
    name='AudioVideoMuxer.app',
    icon=None,
    bundle_identifier='com.yourname.audiovideomuxer',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Video Files',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': ['public.movie'],
                'LSHandlerRank': 'Owner'
            }
        ]
    },
)
'''
    
    # Write the spec file
    with open('macos_app.spec', 'w') as f:
        f.write(spec_content)
    
    try:
        # Build the .app bundle
        subprocess.check_call(['pyinstaller', 'macos_app.spec', '--clean'])
        
        print("\n✅ macOS .app bundle created successfully!")
        print(f"📁 Location: {os.path.abspath('dist/AudioVideoMuxer.app')}")
        
        # Check if app was created
        app_path = 'dist/AudioVideoMuxer.app'
        if os.path.exists(app_path):
            # Get size
            def get_size(start_path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(start_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if os.path.exists(fp):
                            total_size += os.path.getsize(fp)
                return total_size
            
            size_mb = get_size(app_path) / (1024 * 1024)
            print(f"📏 App bundle size: {size_mb:.1f} MB")
            
            print("\n📋 Usage:")
            print("1. Double-click AudioVideoMuxer.app to run")
            print("2. No terminal window will appear")
            print("3. Distribute the entire .app bundle")
            
            print("\n🧪 Testing:")
            print(f"open '{app_path}'")
            
        else:
            print("❌ App bundle was not created")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def main():
    # Check if we're on macOS
    if sys.platform != 'darwin':
        print("❌ This script is for macOS only")
        sys.exit(1)
    
    # Check for FFmpeg binaries
    if not os.path.exists('ffmpeg/macos'):
        print("❌ macOS FFmpeg binaries not found")
        print("Run 'python download_ffmpeg.py' first")
        sys.exit(1)
    
    # Check required files
    required_files = ['ffmpeg/macos/ffmpeg', 'ffmpeg/macos/ffprobe', 'muxer_app_bundled.py']
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Missing files: {missing}")
        sys.exit(1)
    
    if create_app_bundle():
        print("\n🎉 Success! Your app is ready for distribution.")
        print("\nTo test: Double-click dist/AudioVideoMuxer.app")
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()