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
from src.gui.visual_joystick_widget import DualVisualJoystickView
from src.core.action_categories import ActionMode, get_mode_icon


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.joystick_detector = JoystickDetector()
        self.binding_parser = BindingParser()
        self.detected_joysticks = []  # Store detected joysticks
        self.current_bindings = []  # Store current bindings for filtering
        self.current_mode = ActionMode.ALL  # Current filter mode
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

        # Mode Filter Section
        mode_group = QGroupBox("Display Mode")
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Filter by Mode:")
        self.mode_combo = QComboBox()

        # Add all modes to combo box
        for mode in ActionMode:
            icon = get_mode_icon(mode)
            self.mode_combo.addItem(f"{icon} {mode.value}", mode)

        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Joystick Detection Section
        joystick_group = QGroupBox("Detected Joysticks")
        joystick_layout = QVBoxLayout()
        self.joystick_list = QTextEdit()
        self.joystick_list.setReadOnly(True)
        self.joystick_list.setMaximumHeight(150)

        joystick_layout.addWidget(self.joystick_list)

        # Detect button
        self.detect_btn = QPushButton("Detect Joysticks")
        self.detect_btn.clicked.connect(self.detect_joysticks)
        joystick_layout.addWidget(self.detect_btn)

        # Mapping swap section
        swap_group = QWidget()
        swap_layout = QVBoxLayout(swap_group)
        swap_layout.setContentsMargins(0, 10, 0, 0)

        swap_info = QLabel("⚠ Bindings on wrong stick?")
        swap_info.setStyleSheet("font-weight: bold; color: #FF9800;")
        swap_layout.addWidget(swap_info)

        swap_help = QLabel("Click below if SC js1 bindings appear on LEFT stick instead of RIGHT\n(or vice versa)")
        swap_help.setStyleSheet("font-size: 10px; color: #888888;")
        swap_layout.addWidget(swap_help)

        self.swap_btn = QPushButton("🔄 Swap SC js1 ↔ js2 Mapping")
        self.swap_btn.clicked.connect(self.swap_joysticks)
        self.swap_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        swap_layout.addWidget(self.swap_btn)

        self.mapping_status = QLabel()
        self.mapping_status.setStyleSheet("font-size: 10px; color: #4CAF50; font-style: italic;")
        swap_layout.addWidget(self.mapping_status)

        joystick_layout.addWidget(swap_group)
        joystick_group.setLayout(joystick_layout)
        main_layout.addWidget(joystick_group)

        # Visualization Area - Button Grid
        viz_group = QGroupBox("Button Grid View")
        viz_layout = QVBoxLayout()
        self.viz_widget = DualJoystickView()
        viz_layout.addWidget(self.viz_widget)
        viz_group.setLayout(viz_layout)
        main_layout.addWidget(viz_group)

        # Visual Diagram Area
        visual_group = QGroupBox("Visual Diagram View")
        visual_layout = QVBoxLayout()
        self.visual_widget = DualVisualJoystickView()
        visual_layout.addWidget(self.visual_widget)
        visual_group.setLayout(visual_layout)
        main_layout.addWidget(visual_group)

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

            # Update visualizations
            self.viz_widget.set_joysticks(joysticks)
            self.visual_widget.set_joysticks(joysticks)
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
                # Store bindings for filtering
                self.current_bindings = joystick_bindings

                # Apply current mode filter
                self.apply_mode_filter()

                self.statusBar().showMessage(f"Loaded {num_bindings} joystick binding(s) from {instance}")
            else:
                self.current_bindings = []
                self.statusBar().showMessage(f"No joystick bindings found in {instance} profile")
        else:
            self.current_bindings = []
            self.statusBar().showMessage(f"No binding files found for {instance}")

    def on_mode_changed(self, index):
        """Handle mode selection change"""
        self.current_mode = self.mode_combo.itemData(index)
        self.apply_mode_filter()

    def swap_joysticks(self):
        """Swap the left and right joystick mapping"""
        self.viz_widget.swap_joystick_mapping()

        # Update status label
        if self.viz_widget.mapping_swapped:
            self.mapping_status.setText("✓ Mapping SWAPPED: SC js1→RIGHT, js2→LEFT")
            self.statusBar().showMessage("Joystick mapping swapped - SC js1 and js2 reversed")
        else:
            self.mapping_status.setText("✓ Mapping NORMAL: SC js1→LEFT, js2→RIGHT")
            self.statusBar().showMessage("Joystick mapping reset to normal")

        # Reload bindings with new mapping
        if self.current_bindings:
            self.apply_mode_filter()

    def apply_mode_filter(self):
        """Filter and display bindings based on selected mode"""
        from src.core.action_categories import categorize_action

        if not self.current_bindings:
            return

        # Filter bindings by mode
        if self.current_mode == ActionMode.ALL:
            filtered_bindings = self.current_bindings
        else:
            filtered_bindings = [
                binding for binding in self.current_bindings
                if categorize_action(binding.get('action', '')) == self.current_mode
            ]

        # Update button grid visualization
        self.viz_widget.update_bindings(filtered_bindings)

        # Update visual diagram with the same bindings and mapping
        if hasattr(self.viz_widget, 'sc_to_pygame_map') and self.viz_widget.sc_to_pygame_map:
            self.visual_widget.update_bindings(filtered_bindings, self.viz_widget.sc_to_pygame_map)

        # Update status bar
        total = len(self.current_bindings)
        shown = len(filtered_bindings)
        if self.current_mode == ActionMode.ALL:
            self.statusBar().showMessage(f"Showing all {total} binding(s)")
        else:
            self.statusBar().showMessage(f"Showing {shown} of {total} binding(s) for {self.current_mode.value}")
