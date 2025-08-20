# -*- mode: python ; coding: utf-8 -*-
import platform
import os

block_cipher = None

# Determine platform-specific FFmpeg binaries to include
binaries = []
system = platform.system().lower()

if system == 'windows':
    ffmpeg_dir = 'ffmpeg/windows'
    if os.path.exists(ffmpeg_dir):
        binaries = [
            (os.path.join(ffmpeg_dir, 'ffmpeg.exe'), '.'),
            (os.path.join(ffmpeg_dir, 'ffprobe.exe'), '.')
        ]
elif system == 'darwin':  # macOS
    ffmpeg_dir = 'ffmpeg/macos'
    if os.path.exists(ffmpeg_dir):
        binaries = [
            (os.path.join(ffmpeg_dir, 'ffmpeg'), '.'),
            (os.path.join(ffmpeg_dir, 'ffprobe'), '.')
        ]
elif system == 'linux':
    ffmpeg_dir = 'ffmpeg/linux'
    if os.path.exists(ffmpeg_dir):
        binaries = [
            (os.path.join(ffmpeg_dir, 'ffmpeg'), '.'),
            (os.path.join(ffmpeg_dir, 'ffprobe'), '.')
        ]

print(f"Including FFmpeg binaries for {system}: {binaries}")

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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AudioVideoMuxer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    windowed=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Remove this line if you don't have an icon
)