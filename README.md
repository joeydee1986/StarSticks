# StarSticks

A visualization tool for Star Citizen joystick bindings - detect connected joysticks and view your current bindings.

## Features

- **Joystick Detection**: Automatically detects connected joystick devices (HOTAS, HOSAS, etc.)
- **Visual Representation**: Display visual representations of your joysticks with button layouts
- **Binding Visualization**: Maps your Star Citizen bindings to the corresponding buttons on your joystick visuals
- **Multi-Instance Support**: Select between LIVE, PTU, and HOTFIX Star Citizen installations
- **Virpil Alpha Prime Support**: Initial focus on dual Virpil Alpha Prime HOSAS setups

## Requirements

- Windows 10/11
- Python 3.11+ (for development)
- Star Citizen installation

## Installation

### Portable Executable (Recommended)
1. Download the latest `StarSticks.exe` from [Releases](https://github.com/joeydee1986/StarSticks/releases)
2. Double-click `StarSticks.exe` to run
3. No installation required! It's completely portable.

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/joeydee1986/StarSticks.git
   cd StarSticks
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Building from Source

To create your own portable .exe:

### Windows:
```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the build script
python build.py
# OR simply double-click build.bat

# The portable .exe will be created in dist/StarSticks.exe
```

### Build Details:
- Creates a single portable .exe file (~80-120MB)
- No installation or dependencies required for end users
- All libraries bundled into the executable
- Just run the .exe directly!

## Development Status

🚧 **Early Development** - This project is in active initial development.

### Roadmap
- [x] Project setup
- [x] Joystick detection implementation (pygame)
- [x] Star Citizen binding file parser (XML)
- [x] Basic GUI framework (PyQt6)
- [x] Multi-instance SC installation support (LIVE/PTU/HOTFIX)
- [x] Portable .exe build system (PyInstaller)
- [ ] Virpil Alpha Prime visual representation
- [ ] Binding-to-button mapping visualization
- [ ] Advanced joystick visualization with SVG/graphics
- [ ] Support for additional joystick models (VKB, Thrustmaster, etc.)
- [ ] Export/import binding configurations
- [ ] Binding conflict detection

## Contributing

This is a personal project but contributions, suggestions, and bug reports are welcome! Please open an issue to discuss any changes.

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built for the Star Citizen community. Not affiliated with Cloud Imperium Games.
