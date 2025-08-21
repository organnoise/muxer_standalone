#!/usr/bin/env python3
"""
Improved macOS .app bundle creator with proper compatibility settings
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
import platform

def create_app_bundle():
    """Create a proper .app bundle for macOS with compatibility settings"""
    
    print("Creating macOS .app bundle with compatibility settings...")
    
    # Set deployment target
    os.environ['MACOSX_DEPLOYMENT_TARGET'] = '12.0'
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Create improved spec content with compatibility settings
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import platform
import os

block_cipher = None

# Set deployment target
os.environ['MACOSX_DEPLOYMENT_TARGET'] = '12.0'

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
        'PyQt5.QtPrintSupport',  # Sometimes needed
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'PIL',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'nbconvert',
        'tornado',
        'zmq',
        'pygments',
        'jinja2',
        'markupsafe',
        'setuptools',
        'distutils',
        'email',
        'html',
        'http',
        'urllib3',
        'xml',
        'unittest',
        'test',
        'tests',
        '_testcapi',
    ],
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
    strip=True,  # Enable stripping for smaller size
    upx=True,   # Enable UPX compression
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,  # Enable stripping in COLLECT too
    upx=True,
    upx_exclude=['ffmpeg', 'ffprobe'],  # Don't compress FFmpeg binaries
    name='AudioVideoMuxer',
)

app = BUNDLE(
    coll,
    name='AudioVideoMuxer.app',
    icon=None,
    bundle_identifier='com.audiovideomuxer.app',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'AudioVideoMuxer',
        'CFBundleDisplayName': 'Audio Video Muxer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'AudioVideoMuxer',
        'CFBundleIdentifier': 'com.audiovideomuxer.app',
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSMinimumSystemVersion': '12.0',  # Minimum macOS version
        'LSApplicationCategoryType': 'public.app-category.video',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Video Files',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': [
                    'public.movie',
                    'com.apple.quicktime-movie',
                    'public.mpeg-4'
                ],
                'LSHandlerRank': 'Owner'
            },
            {
                'CFBundleTypeName': 'Audio Files', 
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': [
                    'public.audio',
                    'public.wav-audio'
                ],
                'LSHandlerRank': 'Owner'
            }
        ],
        'NSSupportsAutomaticGraphicsSwitching': True,
    },
)
'''
    
    # Write the improved spec file
    with open('macos_compatibility.spec', 'w') as f:
        f.write(spec_content)
    
    try:
        # Build the .app bundle with compatibility settings
        env = os.environ.copy()
        env['MACOSX_DEPLOYMENT_TARGET'] = '12.0'
        
        subprocess.check_call([
            'pyinstaller', 
            'macos_compatibility.spec', 
            '--clean',
            '--noconfirm'
        ], env=env)
        
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
            print(f"📦 App bundle size: {size_mb:.1f} MB")
            
            # Verify deployment target
            executable_path = os.path.join(app_path, 'Contents', 'MacOS', 'AudioVideoMuxer')
            if os.path.exists(executable_path):
                try:
                    result = subprocess.run(['otool', '-l', executable_path], 
                                          capture_output=True, text=True)
                    if 'version 12.0' in result.stdout:
                        print("✅ Deployment target correctly set to macOS 12.0")
                    else:
                        print("⚠️  Deployment target may not be set correctly")
                except:
                    print("ℹ️  Could not verify deployment target")
            
            print("\n📋 Compatibility:")
            print("✅ Should run on macOS 12.0 (Monterey) and later")
            print("✅ Built with forward compatibility for newer macOS versions")
            
            print("\n📋 Usage:")
            print("1. Double-click AudioVideoMuxer.app to run")
            print("2. No terminal window will appear")
            print("3. Distribute the entire .app bundle")
            
            print("\n🧪 Testing:")
            print(f"open '{app_path}'")
            
        else:
            print("❌ App bundle was not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def check_build_environment():
    """Check if the build environment is properly set up"""
    print("🔍 Checking build environment...")
    
    # Check macOS version
    if sys.platform != 'darwin':
        print("❌ This script must be run on macOS")
        return False
    
    try:
        result = subprocess.run(['sw_vers', '-productVersion'], 
                              capture_output=True, text=True)
        macos_version = result.stdout.strip()
        print(f"🍎 macOS version: {macos_version}")
    except:
        print("⚠️  Could not determine macOS version")
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("⚠️  Python 3.8+ recommended for best compatibility")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"📦 PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check PyQt5
    try:
        import PyQt5.QtCore
        print(f"🖥️  PyQt5 version: {PyQt5.QtCore.PYQT_VERSION_STR}")
    except ImportError:
        print("❌ PyQt5 not found")
        return False
    
    # Check for FFmpeg binaries
    if not os.path.exists('ffmpeg/macos'):
        print("❌ macOS FFmpeg binaries not found")
        print("Run 'python download_ffmpeg.py' first")
        return False
    
    # Check required files
    required_files = ['ffmpeg/macos/ffmpeg', 'ffmpeg/macos/ffprobe', 'muxer_app_bundled.py']
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    # Make FFmpeg binaries executable
    os.chmod('ffmpeg/macos/ffmpeg', 0o755)
    os.chmod('ffmpeg/macos/ffprobe', 0o755)
    
    print("✅ Build environment check passed")
    return True

def main():
    """Main function"""
    print("🎬 AudioVideoMuxer macOS App Builder")
    print("=" * 50)
    
    if not check_build_environment():
        print("\n❌ Build environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    if create_app_bundle():
        print("\n🎉 Success! Your app is ready for distribution.")
        print("\nTo test: Double-click dist/AudioVideoMuxer.app")
        print("\n📝 Notes:")
        print("- Built with macOS 12.0 deployment target")
        print("- Compatible with macOS Monterey (12.0) and later")
        print("- FFmpeg binaries are bundled")
        print("- No external dependencies required")
    else:
        print("\n❌ Build failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()