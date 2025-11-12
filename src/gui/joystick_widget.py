"""
Joystick visualization widget
Displays joystick buttons and their bindings in a visual layout
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from typing import Dict, List, Optional
import pygame
from src.models.joystick_models import identify_joystick, JoystickModel


class JoystickButton(QPushButton):
    """Individual button widget representing a joystick button"""

    def __init__(self, button_number: int, parent=None):
        super().__init__(parent)
        self.button_number = button_number
        self.binding_action = None
        self.is_pressed = False
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

    def set_pressed(self, pressed: bool):
        """Set the pressed state of this button"""
        if self.is_pressed != pressed:
            self.is_pressed = pressed
            self.update_display()

    def update_display(self):
        """Update the button display with current binding info"""
        # Pressed state overrides everything with bright color
        if self.is_pressed:
            if self.binding_action:
                text = f"BTN {self.button_number}\n\n{self.binding_action}"
            else:
                text = f"BTN {self.button_number}\n\nUnbound"
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: 3px solid #F57C00;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                }
            """)
        elif self.binding_action:
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

    def __init__(self, joystick_name: str, joystick_id: int, num_buttons: int, num_axes: int = 0, parent=None):
        super().__init__(parent)
        self.joystick_name = joystick_name
        self.joystick_id = joystick_id
        self.num_buttons = num_buttons
        self.num_axes = num_axes
        self.button_widgets = {}
        self.axis_widgets = {}
        self.joystick = None

        # Identify the joystick model
        self.model = identify_joystick(joystick_name, num_buttons, num_axes)

        self.init_ui()
        self.init_joystick_polling()

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

        # Detected model label
        if self.model:
            model_text = f"✓ Detected: {self.model.name}"
            model_color = "#4CAF50"
        else:
            model_text = "⚠ Unknown Model - Manual configuration may be needed"
            model_color = "#FF9800"

        model_label = QLabel(model_text)
        model_label.setStyleSheet(f"color: {model_color}; padding: 5px; font-weight: bold;")
        model_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(model_label)

        # Info label
        info = QLabel(f"Device ID: {self.joystick_id} | {self.num_buttons} Buttons | {self.num_axes} Axes")
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

        # Axes section
        if self.num_axes > 0:
            axes_label = QLabel("Axes")
            axes_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #ffffff;")
            layout.addWidget(axes_label)

            # Create axis displays
            axes_container = QWidget()
            axes_layout = QVBoxLayout(axes_container)
            axes_layout.setSpacing(5)

            axis_names = ["X", "Y", "Z", "RX", "RY", "RZ", "Throttle", "Rudder"]
            for i in range(self.num_axes):
                axis_widget = QWidget()
                axis_h_layout = QHBoxLayout(axis_widget)
                axis_h_layout.setContentsMargins(0, 0, 0, 0)

                # Axis label
                axis_name = axis_names[i] if i < len(axis_names) else f"Axis {i}"
                axis_label = QLabel(f"{axis_name}:")
                axis_label.setMinimumWidth(80)
                axis_label.setStyleSheet("color: #cccccc;")
                axis_h_layout.addWidget(axis_label)

                # Progress bar to show axis value (-1 to 1)
                axis_bar = QProgressBar()
                axis_bar.setMinimum(-100)
                axis_bar.setMaximum(100)
                axis_bar.setValue(0)
                axis_bar.setTextVisible(True)
                axis_bar.setFormat("%v%")
                axis_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #555555;
                        border-radius: 3px;
                        text-align: center;
                        background-color: #2a2a2a;
                    }
                    QProgressBar::chunk {
                        background-color: #2196F3;
                    }
                """)
                axis_h_layout.addWidget(axis_bar)

                # Value label
                value_label = QLabel("0.00")
                value_label.setMinimumWidth(60)
                value_label.setStyleSheet("color: #cccccc; font-family: monospace;")
                axis_h_layout.addWidget(value_label)

                # Binding label
                binding_label = QLabel("")
                binding_label.setStyleSheet("color: #4CAF50; font-style: italic;")
                binding_label.setMinimumWidth(150)
                axis_h_layout.addWidget(binding_label)

                self.axis_widgets[i] = {'bar': axis_bar, 'label': value_label, 'binding': binding_label}
                axes_layout.addWidget(axis_widget)

            layout.addWidget(axes_container)

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

    def set_axis_binding(self, axis_number: int, action: str):
        """
        Set the binding for a specific axis

        Args:
            axis_number: The axis number (0-based)
            action: The action name from Star Citizen
        """
        if axis_number in self.axis_widgets:
            # Clean up action name for display
            display_action = self.format_action_name(action)
            self.axis_widgets[axis_number]['binding'].setText(display_action)
            self.axis_widgets[axis_number]['binding'].setStyleSheet("color: #4CAF50; font-style: italic; font-weight: bold;")

    def clear_all_bindings(self):
        """Clear all button and axis bindings"""
        for btn in self.button_widgets.values():
            btn.clear_binding()
        for axis in self.axis_widgets.values():
            axis['binding'].setText("")

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

    def init_joystick_polling(self):
        """Initialize joystick polling for real-time button press detection"""
        try:
            # Make sure pygame joystick is initialized
            if not pygame.joystick.get_init():
                pygame.joystick.init()

            # Get the joystick by ID (don't re-init pygame, just get the joystick)
            if self.joystick_id < pygame.joystick.get_count():
                self.joystick = pygame.joystick.Joystick(self.joystick_id)
                if not self.joystick.get_init():
                    self.joystick.init()

                print(f"Polling initialized for joystick {self.joystick_id}: {self.joystick.get_name()}")

                # Create timer to poll joystick state (30Hz)
                self.poll_timer = QTimer(self)
                self.poll_timer.timeout.connect(self.poll_joystick)
                self.poll_timer.start(33)  # ~30 FPS
            else:
                print(f"Warning: Joystick ID {self.joystick_id} not found (count: {pygame.joystick.get_count()})")

        except Exception as e:
            print(f"Error initializing joystick polling for ID {self.joystick_id}: {e}")

    def poll_joystick(self):
        """Poll the joystick and update button and axis states"""
        if not self.joystick:
            return

        try:
            # Process pygame events (required for joystick state updates)
            pygame.event.pump()

            # Check each button state
            for button_num in self.button_widgets.keys():
                # pygame buttons are 0-indexed, our display is 1-indexed
                pygame_button_index = button_num - 1

                if pygame_button_index < self.joystick.get_numbuttons():
                    is_pressed = self.joystick.get_button(pygame_button_index)
                    self.button_widgets[button_num].set_pressed(bool(is_pressed))

            # Check each axis value
            for axis_index in self.axis_widgets.keys():
                if axis_index < self.joystick.get_numaxes():
                    # Get axis value (range: -1.0 to 1.0)
                    axis_value = self.joystick.get_axis(axis_index)

                    # Update progress bar (convert to -100 to 100)
                    bar_value = int(axis_value * 100)
                    self.axis_widgets[axis_index]['bar'].setValue(bar_value)

                    # Update value label
                    self.axis_widgets[axis_index]['label'].setText(f"{axis_value:+.2f}")

        except Exception as e:
            print(f"Error polling joystick: {e}")

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
        self.stick_visualizations = {}  # Map pygame ID to visualization widget
        self.mapping_swapped = False  # Track if user has swapped the mapping
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

        # Clear previous mappings
        self.stick_visualizations = {}
        self.left_stick = None
        self.right_stick = None

        # Create visualization for each joystick
        for joy in joysticks:
            viz = JoystickVisualization(
                joystick_name=joy['name'],
                joystick_id=joy['id'],
                num_buttons=joy['buttons'],
                num_axes=joy.get('axes', 0)
            )

            # Store by pygame joystick ID
            self.stick_visualizations[joy['id']] = viz

            # Also store reference based on left/right in name (for display order)
            name_lower = joy['name'].lower()
            if 'left' in name_lower:
                self.left_stick = viz
            elif 'right' in name_lower:
                self.right_stick = viz

            self.layout.addWidget(viz)

        print(f"\n=== JOYSTICK DETECTION ===")
        for joy_id, viz in self.stick_visualizations.items():
            print(f"Pygame ID {joy_id} = {viz.joystick_name}")
        print("="*50 + "\n")

    def swap_joystick_mapping(self):
        """Toggle the joystick mapping (swap left/right)"""
        self.mapping_swapped = not self.mapping_swapped
        print(f"\n🔄 Joystick mapping {'SWAPPED' if self.mapping_swapped else 'NORMAL'}\n")

    def update_bindings(self, bindings: List[Dict]):
        """
        Update all button bindings from parsed SC bindings

        Args:
            bindings: List of binding dictionaries from binding parser
        """
        # Clear all existing bindings first
        for viz in self.stick_visualizations.values():
            viz.clear_all_bindings()

        print(f"\n=== LOADING {len(bindings)} BINDINGS ===")

        # Build mapping from SC js numbers to available pygame IDs
        # Pygame IDs may not be sequential (e.g., 0, 2 if 1 is blacklisted)
        available_pygame_ids = sorted(self.stick_visualizations.keys())

        print(f"Available pygame IDs: {available_pygame_ids}")

        # Apply swap if user has toggled it
        if self.mapping_swapped and len(available_pygame_ids) >= 2:
            available_pygame_ids = list(reversed(available_pygame_ids))
            print("🔄 Mapping is SWAPPED")

        # Create mapping: SC js1 → first available ID, js2 → second available ID, etc.
        sc_to_pygame_map = {}
        for i, pygame_id in enumerate(available_pygame_ids):
            sc_js_number = i + 1  # SC uses 1-based numbering
            sc_to_pygame_map[sc_js_number] = pygame_id
            viz_name = self.stick_visualizations[pygame_id].joystick_name
            print(f"Mapping: SC js{sc_js_number} → Pygame ID {pygame_id} ({viz_name})")

        print()

        # Track bindings per device for summary
        bindings_per_device = {}

        # Apply new bindings
        for binding in bindings:
            input_str = binding.get('input', '')
            action = binding.get('action', '')

            # Parse the input string to get device and button/axis
            parsed = self.parse_input_string(input_str)
            sc_js_number = parsed.get('sc_js_number')  # SC js number (1-based)
            button_num = parsed.get('button')
            axis_name = parsed.get('axis')

            if sc_js_number is None:
                continue

            # Map SC js number to pygame ID using our mapping
            pygame_id = sc_to_pygame_map.get(sc_js_number)

            # Get the visualization for this pygame ID
            viz = self.stick_visualizations.get(pygame_id)
            if not viz:
                print(f"⚠ Warning: SC js{sc_js_number} not mapped (no pygame device available)")
                continue

            # Track this binding
            if sc_js_number not in bindings_per_device:
                bindings_per_device[sc_js_number] = 0
            bindings_per_device[sc_js_number] += 1

            # Handle button bindings
            if button_num is not None:
                viz.set_button_binding(button_num, action)
                print(f"  SC js{sc_js_number} button{button_num} → Pygame ID {pygame_id} ({viz.joystick_name[:30]}) = {action[:30]}")

            # Handle axis bindings
            elif axis_name is not None:
                # Map axis names to indices
                axis_map = {'x': 0, 'y': 1, 'z': 2, 'rotx': 3, 'roty': 4, 'rotz': 5}
                axis_index = axis_map.get(axis_name)

                if axis_index is not None:
                    viz.set_axis_binding(axis_index, action)
                    print(f"  SC js{sc_js_number} {axis_name} → Pygame ID {pygame_id} ({viz.joystick_name[:30]}) = {action[:30]}")

        # Print summary
        print(f"\n=== BINDING SUMMARY ===")
        for sc_js, count in sorted(bindings_per_device.items()):
            pygame_id = sc_js - 1
            viz = self.stick_visualizations.get(pygame_id)
            viz_name = viz.joystick_name if viz else "Unknown"
            print(f"  SC js{sc_js} → Pygame ID {pygame_id} ({viz_name}): {count} bindings")
        print("="*50 + "\n")

    def parse_input_string(self, input_str: str) -> Dict:
        """
        Parse joystick input string from SC bindings

        Args:
            input_str: Input string like "js1_button10" or "js1_x"

        Returns:
            Dictionary with sc_js_number (1-based), button, and/or axis info
        """
        result = {'sc_js_number': None, 'button': None, 'axis': None}

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
                # Keep SC's 1-based numbering (js1 = 1, js2 = 2)
                result['sc_js_number'] = int(input_lower[device_start:device_end])
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

        # Extract axis name (e.g., js1_x, js1_y, js1_rotx)
        # Common axis names in SC: x, y, z, rotx, roty, rotz
        axis_names = ['rotx', 'roty', 'rotz', 'x', 'y', 'z']  # Check longer names first
        for axis in axis_names:
            if f'_{axis}' in input_lower or input_lower.endswith(axis):
                result['axis'] = axis
                break

        return result
