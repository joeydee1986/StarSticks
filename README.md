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

### From Release (Coming Soon)
1. Download the latest installer from [Releases](https://github.com/joeydee1986/StarSticks/releases)
2. Run the installer
3. Launch StarSticks

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

## Development Status

🚧 **Early Development** - This project is in active initial development.

### Roadmap
- [x] Project setup
- [ ] Joystick detection implementation
- [ ] Star Citizen binding file parser
- [ ] Basic GUI framework
- [ ] Virpil Alpha Prime visual representation
- [ ] Binding-to-button mapping visualization
- [ ] Multi-instance SC installation support
- [ ] Installer creation
- [ ] Support for additional joystick models

## Contributing

This is a personal project but contributions, suggestions, and bug reports are welcome! Please open an issue to discuss any changes.

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built for the Star Citizen community. Not affiliated with Cloud Imperium Games.
