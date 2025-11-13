"""
Visual joystick diagram widget
Displays joystick images with binding overlays
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QPen
from typing import Dict, List
import pygame
import sys
import os


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class VisualJoystickDiagram(QWidget):
    """Widget that displays a joystick diagram image with binding overlays"""

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.bindings = {}  # button_num -> action text
        self.original_pixmap = QPixmap(image_path)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create label to display the image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set initial pixmap
        self.update_display()

        layout.addWidget(self.image_label)

    def set_bindings(self, bindings: Dict[int, str]):
        """
        Set the button bindings to display

        Args:
            bindings: Dict mapping button number -> action name
        """
        self.bindings = bindings
        self.update_display()

    def update_display(self):
        """Redraw the image with binding overlays"""
        if self.original_pixmap.isNull():
            return

        # Create a copy to draw on
        pixmap = self.original_pixmap.copy()

        # Create painter to draw overlays
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set font for binding text
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)

        # TODO: Draw binding text at button positions
        # For now, this is a placeholder - we'll add coordinate mapping next

        painter.end()

        # Update the label
        self.image_label.setPixmap(pixmap)


class DualVisualJoystickView(QWidget):
    """Widget that displays dual joystick visual diagram"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.left_bindings = {}
        self.right_bindings = {}
        self.stick_ids = {}  # pygame ID -> 'left' or 'right'
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Scroll area for the large image
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create visual diagram
        image_path = get_resource_path("assets/images/Yogidragon Dual Alpha Template.png")
        self.diagram = VisualJoystickDiagram(image_path)

        scroll.setWidget(self.diagram)
        layout.addWidget(scroll)

    def set_joysticks(self, joysticks: List[Dict]):
        """
        Set the detected joysticks

        Args:
            joysticks: List of joystick info dictionaries
        """
        # Map pygame IDs to left/right based on names
        self.stick_ids = {}
        for joy in joysticks:
            joy_id = joy['id']
            name_lower = joy['name'].lower()

            if 'left' in name_lower:
                self.stick_ids[joy_id] = 'left'
            elif 'right' in name_lower:
                self.stick_ids[joy_id] = 'right'
            else:
                # Default: first one is left, second is right
                if not any(side == 'left' for side in self.stick_ids.values()):
                    self.stick_ids[joy_id] = 'left'
                else:
                    self.stick_ids[joy_id] = 'right'

        print(f"\n📊 Visual diagram stick mapping:")
        for joy_id, side in self.stick_ids.items():
            joy_name = next((j['name'] for j in joysticks if j['id'] == joy_id), 'Unknown')
            print(f"   Pygame ID {joy_id} ({joy_name}) → {side.upper()} side of diagram")
        print()

    def update_bindings(self, bindings: List[Dict], sc_to_pygame_map: Dict[int, int]):
        """
        Update bindings on the visual diagram

        Args:
            bindings: List of binding dictionaries
            sc_to_pygame_map: Mapping from SC js number to pygame ID
        """
        # Clear previous bindings
        self.left_bindings = {}
        self.right_bindings = {}

        # Sort bindings by stick (left/right)
        for binding in bindings:
            input_str = binding.get('input', '')
            action = binding.get('action', '')

            # Parse input
            from src.gui.joystick_widget import DualJoystickView
            temp_view = DualJoystickView()
            parsed = temp_view.parse_input_string(input_str)

            sc_js_number = parsed.get('sc_js_number')
            button_num = parsed.get('button')

            if sc_js_number and button_num:
                # Map to pygame ID
                pygame_id = sc_to_pygame_map.get(sc_js_number)

                # Determine which side (left/right)
                side = self.stick_ids.get(pygame_id)

                if side == 'left':
                    self.left_bindings[button_num] = action
                elif side == 'right':
                    self.right_bindings[button_num] = action

        # Combine bindings for display (TODO: separate left/right on diagram)
        all_bindings = {}
        all_bindings.update(self.left_bindings)
        all_bindings.update(self.right_bindings)

        # Update diagram
        self.diagram.set_bindings(all_bindings)

        print(f"📊 Visual diagram updated: {len(self.left_bindings)} left bindings, {len(self.right_bindings)} right bindings")
