import sys
import os
import subprocess
import platform
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QWidget, QFileDialog, QMessageBox,
    QCheckBox, QHBoxLayout, QFrame, QProgressDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QProcess, pyqtSignal

def get_bundled_ffmpeg_path():
    """Get the path to bundled FFmpeg executable"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = sys._MEIPASS
        system = platform.system().lower()
        
        if system == 'windows':
            return os.path.join(base_path, 'ffmpeg.exe'), os.path.join(base_path, 'ffprobe.exe')
        else:
            return os.path.join(base_path, 'ffmpeg'), os.path.join(base_path, 'ffprobe')
    else:
        # Running as script - look for local FFmpeg first, then system
        system = platform.system().lower()
        
        if system == 'windows':
            local_ffmpeg = os.path.join('ffmpeg', 'windows', 'ffmpeg.exe')
            local_ffprobe = os.path.join('ffmpeg', 'windows', 'ffprobe.exe')
            if os.path.exists(local_ffmpeg) and os.path.exists(local_ffprobe):
                return local_ffmpeg, local_ffprobe
            return 'ffmpeg.exe', 'ffprobe.exe'
        elif system == 'darwin':
            local_ffmpeg = os.path.join('ffmpeg', 'macos', 'ffmpeg')
            local_ffprobe = os.path.join('ffmpeg', 'macos', 'ffprobe')
            if os.path.exists(local_ffmpeg) and os.path.exists(local_ffprobe):
                return local_ffmpeg, local_ffprobe
            return 'ffmpeg', 'ffprobe'
        elif system == 'linux':
            local_ffmpeg = os.path.join('ffmpeg', 'linux', 'ffmpeg')
            local_ffprobe = os.path.join('ffmpeg', 'linux', 'ffprobe')
            if os.path.exists(local_ffmpeg) and os.path.exists(local_ffprobe):
                return local_ffmpeg, local_ffprobe
            return 'ffmpeg', 'ffprobe'
        else:
            return 'ffmpeg', 'ffprobe'

class DragDropWidget(QWidget):
    fileDropped = pyqtSignal(list)

    def __init__(self, prompt_text, filter_exts, parent=None):
        super().__init__(parent)
        self.filter_exts = filter_exts
        self.setAcceptDrops(True)
        self.setMinimumSize(220, 120)
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px dashed #aaa;
                border-radius: 8px;
            }
        """)
        self.layout = QVBoxLayout()
        self.label = QLabel(prompt_text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 15px; color: #888;")
        self.layout.addStretch()
        self.layout.addWidget(self.label)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(
            u.toLocalFile().lower().endswith(self.filter_exts) for u in event.mimeData().urls()
        ):
            self.setStyleSheet("""
                QWidget {
                    background: #e6f7ff;
                    border: 2px solid #1890ff;
                    border-radius: 8px;
                }
            """)
            self.label.setText("Release to drop file")
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px dashed #aaa;
                border-radius: 8px;
            }
        """)
        self.label.setText("Drag and drop file here")

    def dropEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px dashed #aaa;
                border-radius: 8px;
            }
        """)
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        valid = [f for f in files if f.lower().endswith(self.filter_exts)]
        if valid:
            self.fileDropped.emit(valid)
            self.label.setText(os.path.basename(valid[0]))
        else:
            self.label.setText("Invalid file type")
        event.acceptProposedAction()

class MuxerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mux Audio into Video")
        self.setGeometry(100, 100, 480, 480)

        self.video_path = ""
        self.audio_path = ""
        self.output_path = ""
        self.total_duration = 0
        self.last_video_dir = ""
        self.last_audio_dir = ""

        # Get FFmpeg paths
        self.ffmpeg_path, self.ffprobe_path = get_bundled_ffmpeg_path()

        # Central layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("Audio/Video Muxer")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label, 0, Qt.AlignCenter)

        # FFmpeg status indicator
        self.ffmpeg_status = QLabel()
        self.check_ffmpeg_status()
        layout.addWidget(self.ffmpeg_status, 0, Qt.AlignCenter)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Video drag & drop
        layout.addWidget(QLabel("Select Source Video:"))
        self.video_widget = DragDropWidget("Drag and drop video here\nor click below", (".mp4", ".mov"))
        self.video_btn = QPushButton("Choose Video")
        self.video_btn.clicked.connect(self.select_video)
        self.video_widget.fileDropped.connect(self.handle_video_drop)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.video_btn)

        # Audio drag & drop
        layout.addWidget(QLabel("Select New Audio Mix:"))
        self.audio_widget = DragDropWidget("Drag and drop audio here\nor click below", (".wav",))
        self.audio_btn = QPushButton("Choose Audio")
        self.audio_btn.clicked.connect(self.select_audio)
        self.audio_widget.fileDropped.connect(self.handle_audio_drop)
        layout.addWidget(self.audio_widget)
        layout.addWidget(self.audio_btn)

        # Output options
        layout.addSpacing(10)
        layout.addWidget(QLabel("Output Options:"))
        self.save_toggle = QCheckBox("Save to same location as video")
        self.save_toggle.setChecked(True)
        self.save_toggle.stateChanged.connect(self.toggle_save_option)
        layout.addWidget(self.save_toggle)

        # Output name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Output file name:"))
        self.output_name_input = QLineEdit()
        self.output_name_input.setPlaceholderText("my_video_mux.mp4")
        self.output_name_input.textChanged.connect(self.update_output_name)
        name_layout.addWidget(self.output_name_input)
        layout.addLayout(name_layout)

        # Output path selection
        output_layout = QHBoxLayout()
        self.output_btn = QPushButton("Choose Output Location")
        self.output_btn.clicked.connect(self.select_output)
        self.output_btn.setEnabled(False)
        output_layout.addWidget(self.output_btn)
        layout.addLayout(output_layout)
        self.output_label = QLabel("No output location selected")
        layout.addWidget(self.output_label)

        layout.addSpacing(20)

        # Mux button
        self.go_btn = QPushButton("Mux!")
        self.go_btn.clicked.connect(self.mux_files)
        self.go_btn.setEnabled(False)
        self.go_btn.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(self.go_btn)

        self.setCentralWidget(central_widget)

        # QProcess for ffmpeg
        self.progress = None  # Only create when needed
        self.process = QProcess(self)
        self.process.readyReadStandardError.connect(self.update_progress)
        self.process.finished.connect(self.process_finished)

    def check_ffmpeg_status(self):
        """Check if FFmpeg is available and update status"""
        try:
            subprocess.run([self.ffmpeg_path, "-version"], check=True, capture_output=True)
            self.ffmpeg_status.setText("✅ FFmpeg ready (bundled)")
            self.ffmpeg_status.setStyleSheet("color: green; font-size: 12px;")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.ffmpeg_status.setText("❌ FFmpeg not found")
            self.ffmpeg_status.setStyleSheet("color: red; font-size: 12px;")

    # ---- File selection and drag/drop handlers ----

    def select_video(self):
        start_dir = self.last_video_dir if self.last_video_dir else ""
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", start_dir, "Video Files (*.mp4 *.mov)")
        if path:
            self.set_video_path(path)

    def handle_video_drop(self, files):
        self.set_video_path(files[0])

    def set_video_path(self, path):
        self.video_path = path
        self.last_video_dir = os.path.dirname(path)
        self.video_widget.label.setText(os.path.basename(path))
        # Set default output filename: inputname_mux.mp4
        video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        default_name = f"{video_name}_mux.mp4"
        # Only set if user hasn't typed anything or if previous value was auto-generated
        if not self.output_name_input.text() or self.output_name_input.text().endswith("_mux.mp4"):
            self.output_name_input.setText(default_name)
        if self.save_toggle.isChecked():
            self.update_default_output_path()
        self.check_ready()

    def select_audio(self):
        start_dir = self.last_audio_dir if self.last_audio_dir else ""
        path, _ = QFileDialog.getOpenFileName(self, "Select Audio", start_dir, "Audio Files (*.wav)")
        if path:
            self.set_audio_path(path)

    def handle_audio_drop(self, files):
        self.set_audio_path(files[0])

    def set_audio_path(self, path):
        self.audio_path = path
        self.last_audio_dir = os.path.dirname(path)
        self.audio_widget.label.setText(os.path.basename(path))
        self.check_ready()

    # ---- Output path logic ----

    def toggle_save_option(self, state):
        if state == Qt.Checked:
            self.output_btn.setEnabled(False)
            if self.video_path:
                self.update_default_output_path()
            else:
                self.output_path = ""
            self.update_output_label()
        else:
            self.output_btn.setEnabled(True)
            self.update_output_label()

    def update_default_output_path(self):
        if self.video_path:
            video_dir = os.path.dirname(self.video_path)
            base_name = self.output_name_input.text().strip()
            if not base_name:
                video_name = os.path.splitext(os.path.basename(self.video_path))[0]
                base_name = f"{video_name}_mux.mp4"
            self.output_path = os.path.join(video_dir, base_name)
        else:
            self.output_path = ""
        self.update_output_label()

    def select_output(self):
        default_dir = os.path.dirname(self.video_path) if self.video_path else ""
        default_name = self.output_name_input.text().strip()
        if not default_name and self.video_path:
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            default_name = f"{video_name}_mux.mp4"
        path, _ = QFileDialog.getSaveFileName(
            self, "Set Output Location",
            os.path.join(default_dir, default_name),
            "MP4 Files (*.mp4);;MOV Files (*.mov)"
        )
        if path:
            self.output_path = path
            self.update_output_label()
            self.check_ready()

    def update_output_name(self, text):
        # Update output path if using default location
        if self.save_toggle.isChecked() and self.video_path:
            self.update_default_output_path()
        else:
            self.update_output_label()

    def update_output_label(self):
        # Always reflect the current filename, even if no directory yet
        if self.output_path:
            self.output_label.setText(f"Output: {os.path.basename(self.output_path)}")
        else:
            name = self.output_name_input.text().strip()
            if name:
                self.output_label.setText(f"Output: {name}")
            else:
                self.output_label.setText("No output location selected")

    def check_ready(self):
        if self.video_path and self.audio_path:
            if not self.save_toggle.isChecked() and not self.output_path:
                self.go_btn.setEnabled(False)
            else:
                self.go_btn.setEnabled(True)
        else:
            self.go_btn.setEnabled(False)

    # ---- Muxing logic with progress ----

    def mux_files(self):
        if self.save_toggle.isChecked():
            self.update_default_output_path()
        if not self.output_path:
            QMessageBox.warning(self, "Warning", "No output location specified")
            return

        # Check ffmpeg
        try:
            subprocess.run([self.ffmpeg_path, "-version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            QMessageBox.critical(self, "Error", "FFmpeg is not available. Please check the installation.")
            return

        # Get duration of video for progress
        self.total_duration = self.get_total_duration(self.video_path)
        if self.total_duration == 0:
            QMessageBox.warning(self, "Warning", "Could not determine video duration for progress bar. Progress will be estimated.")

        # Create and show progress dialog only when muxing starts
        self.progress = QProgressDialog("Muxing in progress...", "Cancel", 0, 100, self)
        self.progress.setWindowTitle("Processing")
        self.progress.setAutoClose(True)
        self.progress.setAutoReset(True)
        self.progress.canceled.connect(self.cancel_mux)
        self.progress.setValue(0)
        self.progress.show()

        # Prepare ffmpeg command
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", self.video_path,
            "-i", self.audio_path,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            self.output_path
        ]
        # Start ffmpeg process
        self.process.start(cmd[0], cmd[1:])

    def get_total_duration(self, file_path):
        try:
            cmd = [
                self.ffprobe_path, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip()) if result.returncode == 0 else 0
        except Exception:
            return 0

    def update_progress(self):
        # Parse ffmpeg stderr for time info
        data = self.process.readAllStandardError().data().decode(errors="ignore")
        import re
        match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", data)
        if match and self.total_duration > 0:
            h, m, s = match.groups()
            current = int(h) * 3600 + int(m) * 60 + float(s)
            percent = int((current / self.total_duration) * 100)
            if self.progress:
                self.progress.setValue(min(percent, 100))
        elif "frame=" in data and self.progress:
            val = self.progress.value()
            if val < 95:
                self.progress.setValue(val + 1)

    def process_finished(self):
        if self.progress:
            self.progress.setValue(100)
        if self.process.exitCode() == 0:
            QMessageBox.information(self, "Success", f"Saved to:\n{self.output_path}")
        else:
            err = self.process.readAllStandardError().data().decode(errors="ignore")
            QMessageBox.critical(self, "Error", f"FFmpeg failed:\n{err}")

    def cancel_mux(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
            QMessageBox.information(self, "Cancelled", "Muxing was cancelled.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MuxerApp()
    window.show()
    sys.exit(app.exec_())