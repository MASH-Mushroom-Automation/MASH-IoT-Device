"""
Device ID Generator with Luhn Modulo N Algorithm
Generates unique device IDs in the format: MASH-A1-CAL25-D5A91F
"""

import secrets
import string
from typing import Dict, Tuple


class DeviceIDGenerator:
    """Generate unique device IDs using Luhn Modulo N algorithm"""
    
    # Character set for Luhn algorithm (0-9, A-F for hexadecimal)
    CHARSET = "0123456789ABCDEF"
    
    # Model types
    MODELS = {
        'A': 'Alpha Prototype Build',
        'B': 'Beta Prototype Build',
        'R': 'Release Build'
    }
    
    @staticmethod
    def luhn_checksum(data: str, charset: str = CHARSET) -> str:
        """
        Calculate Luhn checksum for given data
        
        Args:
            data: Input string to calculate checksum for
            charset: Character set to use for calculation
            
        Returns:
            Checksum character
        """
        n = len(charset)
        number = tuple(charset.index(char) for char in reversed(data))
        
        # Calculate checksum
        checksum = sum(number[::2]) + sum(
            sum(divmod(num * 2, n)) for num in number[1::2]
        )
        
        return charset[(n - checksum % n) % n]
    
    @staticmethod
    def validate_luhn(data: str, charset: str = CHARSET) -> bool:
        """
        Validate a string with Luhn algorithm
        
        Args:
            data: String to validate (including checksum)
            charset: Character set used for calculation
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # The last character should be the checksum
            expected_checksum = DeviceIDGenerator.luhn_checksum(data[:-1], charset)
            return data[-1] == expected_checksum
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def generate_hex_code(length: int = 5) -> str:
        """
        Generate a random hexadecimal code
        
        Args:
            length: Length of the hex code (default 5, will add 1 checksum digit)
            
        Returns:
            Hex code with Luhn checksum
        """
        # Generate random hex string
        random_hex = ''.join(secrets.choice(DeviceIDGenerator.CHARSET) for _ in range(length))
        
        # Add Luhn checksum
        checksum = DeviceIDGenerator.luhn_checksum(random_hex)
        return random_hex + checksum
    
    @staticmethod
    def generate_device_id(brand: str = "MASH",
                          model: str = "A",
                          version: int = 1,
                          location: str = "CAL",
                          year: int = 25) -> Tuple[str, Dict[str, str]]:
        """
        Generate a complete device ID
        
        Args:
            brand: Brand name (default: MASH)
            model: Model type - A (Alpha), B (Beta), or R (Release)
            version: Version number
            location: Location code (3 letters)
            year: Year (2 digits)
            
        Returns:
            Tuple of (device_id, components_dict)
        """
        # Validate inputs
        brand = brand.upper().strip()
        model = model.upper().strip()
        location = location.upper().strip()[:3]  # Max 3 characters
        
        if model not in DeviceIDGenerator.MODELS:
            model = 'A'  # Default to Alpha
        
        # Generate unique hex code with Luhn checksum
        hex_code = DeviceIDGenerator.generate_hex_code()
        
        # Format device ID
        device_id = f"{brand}-{model}{version}-{location}{year:02d}-{hex_code}"
        
        # Return ID and components
        components = {
            'device_id': device_id,
            'brand': brand,
            'model': model,
            'model_name': DeviceIDGenerator.MODELS[model],
            'version': str(version),
            'location': location,
            'year': f"{year:02d}",
            'hex_code': hex_code
        }
        
        return device_id, components
    
    @staticmethod
    def parse_device_id(device_id: str) -> Dict[str, str]:
        """
        Parse a device ID into its components
        
        Args:
            device_id: Device ID string (e.g., MASH-A1-CAL25-D5A91F)
            
        Returns:
            Dictionary with device ID components
        """
        try:
            parts = device_id.split('-')
            if len(parts) != 4:
                raise ValueError("Invalid device ID format")
            
            brand = parts[0]
            model = parts[1][0]
            version = parts[1][1:]
            location = parts[2][:3]
            year = parts[2][3:]
            hex_code = parts[3]
            
            return {
                'device_id': device_id,
                'brand': brand,
                'model': model,
                'model_name': DeviceIDGenerator.MODELS.get(model, 'Unknown'),
                'version': version,
                'location': location,
                'year': year,
                'hex_code': hex_code,
                'valid_checksum': DeviceIDGenerator.validate_luhn(hex_code)
            }
        except (ValueError, IndexError, KeyError) as e:
            return {
                'device_id': device_id,
                'error': f"Invalid device ID: {str(e)}",
                'valid_checksum': False
            }
    
    @staticmethod
    def validate_device_id(device_id: str) -> bool:
        """
        Validate a device ID format and checksum
        
        Args:
            device_id: Device ID string
            
        Returns:
            True if valid, False otherwise
        """
        parsed = DeviceIDGenerator.parse_device_id(device_id)
        return 'error' not in parsed and parsed.get('valid_checksum', False)


# Example usage
if __name__ == "__main__":
    # Generate a new device ID
    device_id, components = DeviceIDGenerator.generate_device_id(
        brand="MASH",
        model="A",
        version=1,
        location="CAL",
        year=25
    )
    
    print(f"Generated Device ID: {device_id}")
    print(f"Components: {components}")
    
    # Validate the device ID
    is_valid = DeviceIDGenerator.validate_device_id(device_id)
    print(f"Valid: {is_valid}")
    
    # Parse the device ID
    parsed = DeviceIDGenerator.parse_device_id(device_id)
    print(f"Parsed: {parsed}")
