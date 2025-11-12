"""
Star Citizen binding file parser
Parses XML binding files from Star Citizen installations
"""
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional


class BindingParser:
    """Parse Star Citizen joystick binding XML files"""

    def __init__(self):
        """Initialize the binding parser"""
        self.sc_base_paths = [
            r"C:\Program Files\Roberts Space Industries\StarCitizen",
            r"D:\Program Files\Roberts Space Industries\StarCitizen",
            r"E:\Program Files\Roberts Space Industries\StarCitizen",
        ]
        self.bindings = {}

    def find_sc_installation(self) -> Optional[Path]:
        """
        Find the Star Citizen installation directory

        Returns:
            Path to SC installation, or None if not found
        """
        for base_path in self.sc_base_paths:
            if os.path.exists(base_path):
                return Path(base_path)
        return None

    def get_bindings_path(self, instance: str = "LIVE") -> Optional[Path]:
        """
        Get the path to the bindings directory for a specific instance

        Args:
            instance: The SC instance (LIVE, PTU, HOTFIX)

        Returns:
            Path to the bindings directory, or None if not found
        """
        sc_path = self.find_sc_installation()
        if not sc_path:
            return None

        bindings_path = sc_path / instance / "USER" / "Client" / "0" / "Controls" / "Mappings"

        if bindings_path.exists():
            return bindings_path
        return None

    def list_binding_files(self, instance: str = "LIVE") -> List[str]:
        """
        List all binding XML files for a specific instance

        Args:
            instance: The SC instance (LIVE, PTU, HOTFIX)

        Returns:
            List of binding file names
        """
        bindings_path = self.get_bindings_path(instance)
        if not bindings_path:
            return []

        xml_files = list(bindings_path.glob("*.xml"))
        return [f.name for f in xml_files]

    def parse_binding_file(self, file_path: Path) -> Dict:
        """
        Parse a single binding XML file

        Args:
            file_path: Path to the XML binding file

        Returns:
            Dictionary containing parsed bindings
        """
        bindings = {
            'joystick_bindings': [],
            'keyboard_bindings': [],
            'mouse_bindings': []
        }

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Parse joystick bindings
            for action in root.findall('.//action'):
                action_name = action.get('name', 'Unknown')

                # Look for joystick rebinds
                for rebind in action.findall('.//rebind'):
                    input_type = rebind.get('input', '')

                    if 'js' in input_type.lower():  # Joystick binding
                        binding_info = {
                            'action': action_name,
                            'input': rebind.get('input', ''),
                            'multiTap': rebind.get('multiTap', ''),
                        }
                        bindings['joystick_bindings'].append(binding_info)

                    elif 'kb' in input_type.lower():  # Keyboard binding
                        binding_info = {
                            'action': action_name,
                            'input': rebind.get('input', ''),
                        }
                        bindings['keyboard_bindings'].append(binding_info)

                    elif 'mouse' in input_type.lower():  # Mouse binding
                        binding_info = {
                            'action': action_name,
                            'input': rebind.get('input', ''),
                        }
                        bindings['mouse_bindings'].append(binding_info)

        except ET.ParseError as e:
            print(f"Error parsing XML file {file_path}: {e}")
        except Exception as e:
            print(f"Unexpected error parsing {file_path}: {e}")

        return bindings

    def load_bindings(self, instance: str = "LIVE") -> Dict:
        """
        Load all bindings for a specific Star Citizen instance

        Args:
            instance: The SC instance (LIVE, PTU, HOTFIX)

        Returns:
            Dictionary containing all bindings
        """
        bindings_path = self.get_bindings_path(instance)
        if not bindings_path:
            print(f"Could not find bindings path for {instance}")
            return {}

        binding_files = self.list_binding_files(instance)
        if not binding_files:
            print(f"No binding files found for {instance}")
            return {}

        # Parse the first binding file found (can be extended to support multiple)
        first_file = bindings_path / binding_files[0]
        self.bindings = self.parse_binding_file(first_file)

        return self.bindings

    def get_joystick_bindings(self) -> List[Dict]:
        """
        Get all joystick bindings

        Returns:
            List of joystick binding dictionaries
        """
        return self.bindings.get('joystick_bindings', [])

    def parse_joystick_input(self, input_string: str) -> Dict:
        """
        Parse a joystick input string to extract device and button info

        Example: "js1_button10" -> {'device': 1, 'button': 10}

        Args:
            input_string: The input string from the binding

        Returns:
            Dictionary with device and button/axis information
        """
        result = {
            'device': None,
            'button': None,
            'axis': None,
            'hat': None
        }

        if not input_string:
            return result

        input_lower = input_string.lower()

        # Extract device number
        if 'js' in input_lower:
            try:
                device_start = input_lower.find('js') + 2
                device_end = device_start
                while device_end < len(input_lower) and input_lower[device_end].isdigit():
                    device_end += 1
                result['device'] = int(input_lower[device_start:device_end])
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

        # Extract axis information
        if 'axis' in input_lower or 'x' in input_lower or 'y' in input_lower or 'z' in input_lower:
            result['axis'] = input_string  # Store raw for now

        # Extract hat information
        if 'hat' in input_lower or 'pov' in input_lower:
            result['hat'] = input_string  # Store raw for now

        return result
