"""
Visual joystick diagram widget
Displays joystick images with binding overlays
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QImageReader
from typing import Dict, List
import pygame
import sys
import os

# Increase Qt's image allocation limit to 512MB (default is 256MB)
QImageReader.setAllocationLimit(512)


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Button coordinate mappings for Yogidragon Dual Alpha Template (11000x6160 pixels)
# Format: button_number -> (x, y, alignment)
# Alignment: 'left', 'center', 'right' for text positioning

LEFT_BUTTON_COORDS = {
    # Thumb buttons (top of stick)
    1: (2750, 2200, 'center'),
    2: (2950, 2200, 'center'),
    3: (2550, 2200, 'center'),
    4: (2750, 2000, 'center'),

    # Side buttons
    5: (1800, 2800, 'right'),
    6: (1800, 3000, 'right'),
    7: (1800, 3200, 'right'),
    8: (1800, 3400, 'right'),

    # Trigger stages
    9: (2750, 4500, 'center'),
    10: (2750, 4700, 'center'),

    # Hat switches (approximate positions)
    11: (2400, 2600, 'center'),  # Hat 1
    12: (3100, 2600, 'center'),  # Hat 2

    # Additional buttons
    13: (1600, 2400, 'right'),
    14: (1600, 2600, 'right'),
    15: (3900, 2400, 'left'),
    16: (3900, 2600, 'left'),
}

RIGHT_BUTTON_COORDS = {
    # Thumb buttons (top of stick) - mirrored from left
    1: (8250, 2200, 'center'),
    2: (8050, 2200, 'center'),
    3: (8450, 2200, 'center'),
    4: (8250, 2000, 'center'),

    # Side buttons - mirrored
    5: (9200, 2800, 'left'),
    6: (9200, 3000, 'left'),
    7: (9200, 3200, 'left'),
    8: (9200, 3400, 'left'),

    # Trigger stages
    9: (8250, 4500, 'center'),
    10: (8250, 4700, 'center'),

    # Hat switches - mirrored
    11: (8600, 2600, 'center'),  # Hat 1
    12: (7900, 2600, 'center'),  # Hat 2

    # Additional buttons - mirrored
    13: (9400, 2400, 'left'),
    14: (9400, 2600, 'left'),
    15: (7100, 2400, 'right'),
    16: (7100, 2600, 'right'),
}


class VisualJoystickDiagram(QWidget):
    """Widget that displays a joystick diagram image with binding overlays"""

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.left_bindings = {}  # button_num -> action text
        self.right_bindings = {}  # button_num -> action text
        self.original_pixmap = QPixmap(image_path)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create label to display the image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)  # We'll handle scaling manually

        # Set initial pixmap
        self.update_display()

        layout.addWidget(self.image_label)

    def resizeEvent(self, event):
        """Handle resize events to scale the image"""
        super().resizeEvent(event)
        self.update_display()

    def set_bindings(self, left_bindings: Dict[int, str], right_bindings: Dict[int, str]):
        """
        Set the button bindings to display

        Args:
            left_bindings: Dict mapping button number -> action name for left stick
            right_bindings: Dict mapping button number -> action name for right stick
        """
        self.left_bindings = left_bindings
        self.right_bindings = right_bindings
        self.update_display()

    def draw_binding_text(self, painter: QPainter, x: int, y: int, text: str, alignment: str):
        """
        Draw binding text at specified position with alignment

        Args:
            painter: QPainter instance
            x, y: Position coordinates
            text: Binding action text
            alignment: 'left', 'center', or 'right'
        """
        # Truncate long text
        max_length = 25
        if len(text) > max_length:
            text = text[:max_length - 3] + "..."

        # Calculate text width for alignment
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()

        # Adjust x position based on alignment
        if alignment == 'center':
            draw_x = x - text_width // 2
        elif alignment == 'right':
            draw_x = x - text_width - 20  # Add padding for right-aligned
        else:  # left
            draw_x = x + 20  # Add padding for left-aligned

        # Draw white background box with border (like fillable PDF style)
        padding = 12
        bg_rect = (
            draw_x - padding,
            y - text_height - padding // 2,
            text_width + padding * 2,
            text_height + padding
        )

        # White background
        painter.fillRect(*bg_rect, QColor(255, 255, 255, 255))

        # Black border
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawRect(*bg_rect)

        # Draw black text on white background
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(draw_x, y, text)

    def update_display(self):
        """Redraw the image with binding overlays"""
        if self.original_pixmap.isNull():
            return

        # Create a copy to draw on
        pixmap = self.original_pixmap.copy()

        # Create painter to draw overlays
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Set font for binding text (scaled for high-res image)
        # Smaller font for better readability
        font = QFont("Arial", 50, QFont.Weight.Normal)
        painter.setFont(font)

        # Draw left stick bindings
        for button_num, action in self.left_bindings.items():
            if button_num in LEFT_BUTTON_COORDS:
                x, y, alignment = LEFT_BUTTON_COORDS[button_num]
                self.draw_binding_text(painter, x, y, action, alignment)

        # Draw right stick bindings
        for button_num, action in self.right_bindings.items():
            if button_num in RIGHT_BUTTON_COORDS:
                x, y, alignment = RIGHT_BUTTON_COORDS[button_num]
                self.draw_binding_text(painter, x, y, action, alignment)

        painter.end()

        # Scale to fit the available widget size while maintaining aspect ratio
        label_size = self.image_label.size()
        if label_size.width() > 0 and label_size.height() > 0:
            scaled_pixmap = pixmap.scaled(
                label_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            # Fallback for initial sizing
            scaled_pixmap = pixmap.scaledToWidth(
                1200,
                Qt.TransformationMode.SmoothTransformation
            )

        # Update the label with scaled pixmap
        self.image_label.setPixmap(scaled_pixmap)


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

        # Update diagram with separate left/right bindings
        self.diagram.set_bindings(self.left_bindings, self.right_bindings)

        print(f"📊 Visual diagram updated: {len(self.left_bindings)} left bindings, {len(self.right_bindings)} right bindings")
