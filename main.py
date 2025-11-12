"""
StarSticks - Star Citizen Joystick Binding Visualizer
Main entry point for the application
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    """Initialize and run the StarSticks application"""
    app = QApplication(sys.argv)
    app.setApplicationName("StarSticks")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("StarSticks")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
