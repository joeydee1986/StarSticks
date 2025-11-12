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
from src.gui.joystick_widget import DualJoystickView


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.joystick_detector = JoystickDetector()
        self.binding_parser = BindingParser()
        self.detected_joysticks = []  # Store detected joysticks
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
        self.rescan_instances_btn = QPushButton("Rescan Instances")
        self.rescan_instances_btn.clicked.connect(self.scan_sc_instances)
        self.refresh_bindings_btn = QPushButton("Load Bindings")
        self.refresh_bindings_btn.clicked.connect(self.load_bindings)
        instance_layout.addWidget(instance_label)
        instance_layout.addWidget(self.instance_combo)
        instance_layout.addWidget(self.rescan_instances_btn)
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

        # Visualization Area
        viz_group = QGroupBox("Joystick Visualization")
        viz_layout = QVBoxLayout()
        self.viz_widget = DualJoystickView()
        viz_layout.addWidget(self.viz_widget)
        viz_group.setLayout(viz_layout)
        main_layout.addWidget(viz_group)

        # Status Bar
        self.statusBar().showMessage("Ready")

        # Auto-detect SC instances and joysticks on startup
        self.scan_sc_instances()
        self.detect_joysticks()

    def scan_sc_instances(self):
        """Scan for installed Star Citizen instances and populate dropdown"""
        self.statusBar().showMessage("Scanning for Star Citizen installations...")

        # Get list of installed instances
        installed_instances = self.binding_parser.detect_installed_instances()

        # Clear and repopulate combo box
        self.instance_combo.clear()

        if installed_instances:
            self.instance_combo.addItems(installed_instances)
            self.statusBar().showMessage(f"Found {len(installed_instances)} SC instance(s): {', '.join(installed_instances)}")
        else:
            # No instances found, add default options
            self.instance_combo.addItems(["LIVE", "PTU", "HOTFIX"])
            self.statusBar().showMessage("No Star Citizen installation found. Please check your installation path.")

    def detect_joysticks(self):
        """Detect connected joysticks and display them"""
        self.statusBar().showMessage("Detecting joysticks...")
        joysticks = self.joystick_detector.detect()

        # Store detected joysticks
        self.detected_joysticks = joysticks

        if joysticks:
            output = f"Found {len(joysticks)} joystick(s):\n\n"
            for idx, joy in enumerate(joysticks):
                output += f"[{idx}] {joy['name']}\n"
                output += f"    Buttons: {joy['buttons']}\n"
                output += f"    Axes: {joy['axes']}\n"
                output += f"    Hats: {joy['hats']}\n\n"
            self.joystick_list.setText(output)
            self.statusBar().showMessage(f"Detected {len(joysticks)} joystick(s)")

            # Update visualization
            self.viz_widget.set_joysticks(joysticks)
        else:
            self.joystick_list.setText("No joysticks detected.\n\nPlease ensure your joysticks are connected.")
            self.statusBar().showMessage("No joysticks detected")

            # Clear visualization
            self.viz_widget.set_joysticks([])

    def load_bindings(self):
        """Load Star Citizen bindings from the selected instance"""
        instance = self.instance_combo.currentText()
        self.statusBar().showMessage(f"Loading bindings from {instance}...")

        bindings = self.binding_parser.load_bindings(instance)

        if bindings:
            joystick_bindings = bindings.get('joystick_bindings', [])
            num_bindings = len(joystick_bindings)

            if num_bindings > 0:
                # Update visualization with bindings
                self.viz_widget.update_bindings(joystick_bindings)
                self.statusBar().showMessage(f"Loaded {num_bindings} joystick binding(s) from {instance}")
            else:
                self.statusBar().showMessage(f"No joystick bindings found in {instance} profile")
        else:
            self.statusBar().showMessage(f"No binding files found for {instance}")
