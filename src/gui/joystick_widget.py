"""
Joystick visualization widget
Displays joystick buttons and their bindings in a visual layout
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, List, Optional


class JoystickButton(QPushButton):
    """Individual button widget representing a joystick button"""

    def __init__(self, button_number: int, parent=None):
        super().__init__(parent)
        self.button_number = button_number
        self.binding_action = None
        self.setMinimumSize(100, 80)
        self.setMaximumSize(120, 100)
        self.update_display()

    def set_binding(self, action: str):
        """Set the binding action for this button"""
        self.binding_action = action
        self.update_display()

    def clear_binding(self):
        """Clear the binding for this button"""
        self.binding_action = None
        self.update_display()

    def update_display(self):
        """Update the button display with current binding info"""
        if self.binding_action:
            # Show button number and binding
            text = f"BTN {self.button_number}\n\n{self.binding_action}"
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: 2px solid #45a049;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
        else:
            # Show just button number (no binding)
            text = f"BTN {self.button_number}\n\nUnbound"
            self.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #cccccc;
                    border: 2px solid #555555;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
            """)

        self.setText(text)
        font = self.font()
        font.setPointSize(8)
        self.setFont(font)


class JoystickVisualization(QWidget):
    """Widget that displays a visual representation of a joystick with bindings"""

    def __init__(self, joystick_name: str, joystick_id: int, num_buttons: int, parent=None):
        super().__init__(parent)
        self.joystick_name = joystick_name
        self.joystick_id = joystick_id
        self.num_buttons = num_buttons
        self.button_widgets = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Joystick name header
        header = QLabel(f"{self.joystick_name}")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2a2a2a;
                color: #ffffff;
                border-radius: 5px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Info label
        info = QLabel(f"Device ID: {self.joystick_id} | {self.num_buttons} Buttons")
        info.setStyleSheet("color: #888888; padding: 5px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # Scroll area for buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Button grid container
        button_container = QWidget()
        grid = QGridLayout(button_container)
        grid.setSpacing(10)

        # Create button widgets in a grid (6 columns)
        columns = 6
        for i in range(self.num_buttons):
            row = i // columns
            col = i % columns

            btn_widget = JoystickButton(i + 1)  # Button numbers start at 1
            btn_widget.clicked.connect(lambda checked, b=i+1: self.on_button_clicked(b))
            self.button_widgets[i + 1] = btn_widget

            grid.addWidget(btn_widget, row, col)

        scroll.setWidget(button_container)
        layout.addWidget(scroll)

    def set_button_binding(self, button_number: int, action: str):
        """
        Set the binding for a specific button

        Args:
            button_number: The button number (1-based)
            action: The action name from Star Citizen
        """
        if button_number in self.button_widgets:
            # Clean up action name for display
            display_action = self.format_action_name(action)
            self.button_widgets[button_number].set_binding(display_action)

    def clear_all_bindings(self):
        """Clear all button bindings"""
        for btn in self.button_widgets.values():
            btn.clear_binding()

    def format_action_name(self, action: str) -> str:
        """
        Format Star Citizen action names to be more readable

        Args:
            action: Raw action name from XML

        Returns:
            Formatted action name
        """
        # Remove common prefixes
        action = action.replace('v_', '').replace('spaceship_', '')

        # Replace underscores with spaces
        action = action.replace('_', ' ')

        # Capitalize words
        action = action.title()

        # Limit length for display
        if len(action) > 30:
            action = action[:27] + "..."

        return action

    def on_button_clicked(self, button_number: int):
        """Handle button click event"""
        btn = self.button_widgets.get(button_number)
        if btn and btn.binding_action:
            print(f"Button {button_number} clicked: {btn.binding_action}")


class DualJoystickView(QWidget):
    """Widget that displays two joysticks side by side (HOSAS setup)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.left_stick = None
        self.right_stick = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(20)

        # Placeholder
        self.placeholder = QLabel("No joysticks to display.\n\nClick 'Detect Joysticks' to scan for devices.")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #888888; font-size: 14px;")
        self.layout.addWidget(self.placeholder)

    def set_joysticks(self, joysticks: List[Dict]):
        """
        Set the joysticks to display

        Args:
            joysticks: List of joystick info dictionaries
        """
        # Clear existing layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not joysticks:
            self.placeholder = QLabel("No joysticks detected.")
            self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.placeholder)
            return

        # Create visualization for each joystick
        for joy in joysticks:
            viz = JoystickVisualization(
                joystick_name=joy['name'],
                joystick_id=joy['id'],
                num_buttons=joy['buttons']
            )

            # Store reference based on left/right in name
            name_lower = joy['name'].lower()
            if 'left' in name_lower:
                self.left_stick = viz
            elif 'right' in name_lower:
                self.right_stick = viz

            self.layout.addWidget(viz)

    def update_bindings(self, bindings: List[Dict]):
        """
        Update all button bindings from parsed SC bindings

        Args:
            bindings: List of binding dictionaries from binding parser
        """
        # Clear all existing bindings first
        if self.left_stick:
            self.left_stick.clear_all_bindings()
        if self.right_stick:
            self.right_stick.clear_all_bindings()

        # Apply new bindings
        for binding in bindings:
            input_str = binding.get('input', '')
            action = binding.get('action', '')

            # Parse the input string to get device and button
            parsed = self.parse_input_string(input_str)
            device_id = parsed.get('device')
            button_num = parsed.get('button')

            if device_id is not None and button_num is not None:
                # Map device ID to stick
                # Device 0 is usually first detected (could be left or right)
                # We'll need to improve this mapping logic
                if device_id == 0 and self.left_stick:
                    self.left_stick.set_button_binding(button_num, action)
                elif device_id == 1 and self.right_stick:
                    self.right_stick.set_button_binding(button_num, action)

    def parse_input_string(self, input_str: str) -> Dict:
        """
        Parse joystick input string from SC bindings

        Args:
            input_str: Input string like "js1_button10"

        Returns:
            Dictionary with device and button info
        """
        result = {'device': None, 'button': None}

        if not input_str:
            return result

        input_lower = input_str.lower()

        # Extract device number (js1, js2, etc.)
        if 'js' in input_lower:
            try:
                device_start = input_lower.find('js') + 2
                device_end = device_start
                while device_end < len(input_lower) and input_lower[device_end].isdigit():
                    device_end += 1
                # SC uses 1-based, convert to 0-based
                result['device'] = int(input_lower[device_start:device_end]) - 1
            except (ValueError, IndexError):
                pass

        # Extract button number
        if 'button' in input_lower:
            try:
                button_start = input_lower.find('button') + 6
                button_num = ''
                for char in input_lower[button_start:]:
                    if char.isdigit():
                        button_num += char
                    else:
                        break
                if button_num:
                    result['button'] = int(button_num)
            except ValueError:
                pass

        return result
