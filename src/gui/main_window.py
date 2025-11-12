"""
Main application window for StarSticks
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from src.core.joystick_detector import JoystickDetector
from src.core.binding_parser import BindingParser


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.joystick_detector = JoystickDetector()
        self.binding_parser = BindingParser()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("StarSticks - Star Citizen Joystick Binding Visualizer")
        self.setMinimumSize(1024, 768)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("StarSticks")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Star Citizen Instance Selection
        instance_group = QGroupBox("Star Citizen Instance")
        instance_layout = QHBoxLayout()
        instance_label = QLabel("Select Instance:")
        self.instance_combo = QComboBox()
        self.instance_combo.addItems(["LIVE", "PTU", "HOTFIX"])
        self.refresh_bindings_btn = QPushButton("Load Bindings")
        self.refresh_bindings_btn.clicked.connect(self.load_bindings)
        instance_layout.addWidget(instance_label)
        instance_layout.addWidget(self.instance_combo)
        instance_layout.addWidget(self.refresh_bindings_btn)
        instance_layout.addStretch()
        instance_group.setLayout(instance_layout)
        main_layout.addWidget(instance_group)

        # Joystick Detection Section
        joystick_group = QGroupBox("Detected Joysticks")
        joystick_layout = QVBoxLayout()
        self.joystick_list = QTextEdit()
        self.joystick_list.setReadOnly(True)
        self.joystick_list.setMaximumHeight(150)
        self.detect_btn = QPushButton("Detect Joysticks")
        self.detect_btn.clicked.connect(self.detect_joysticks)
        joystick_layout.addWidget(self.joystick_list)
        joystick_layout.addWidget(self.detect_btn)
        joystick_group.setLayout(joystick_layout)
        main_layout.addWidget(joystick_group)

        # Visualization Area (placeholder for now)
        viz_group = QGroupBox("Joystick Visualization")
        viz_layout = QVBoxLayout()
        self.viz_area = QLabel("Joystick visualization will appear here")
        self.viz_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viz_area.setStyleSheet("background-color: #2a2a2a; color: #ffffff; min-height: 300px;")
        viz_layout.addWidget(self.viz_area)
        viz_group.setLayout(viz_layout)
        main_layout.addWidget(viz_group)

        # Status Bar
        self.statusBar().showMessage("Ready")

        # Auto-detect joysticks on startup
        self.detect_joysticks()

    def detect_joysticks(self):
        """Detect connected joysticks and display them"""
        self.statusBar().showMessage("Detecting joysticks...")
        joysticks = self.joystick_detector.detect()

        if joysticks:
            output = f"Found {len(joysticks)} joystick(s):\n\n"
            for idx, joy in enumerate(joysticks):
                output += f"[{idx}] {joy['name']}\n"
                output += f"    Buttons: {joy['buttons']}\n"
                output += f"    Axes: {joy['axes']}\n"
                output += f"    Hats: {joy['hats']}\n\n"
            self.joystick_list.setText(output)
            self.statusBar().showMessage(f"Detected {len(joysticks)} joystick(s)")
        else:
            self.joystick_list.setText("No joysticks detected.\n\nPlease ensure your joysticks are connected.")
            self.statusBar().showMessage("No joysticks detected")

    def load_bindings(self):
        """Load Star Citizen bindings from the selected instance"""
        instance = self.instance_combo.currentText()
        self.statusBar().showMessage(f"Loading bindings from {instance}...")

        bindings = self.binding_parser.load_bindings(instance)

        if bindings:
            self.statusBar().showMessage(f"Loaded {len(bindings)} binding(s) from {instance}")
        else:
            self.statusBar().showMessage(f"No bindings found for {instance}")
