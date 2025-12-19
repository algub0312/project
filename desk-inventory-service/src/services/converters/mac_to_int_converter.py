def convert_mac_to_int(mac_address: str) -> int:
    """Convert a MAC address string to its integer representation.

    Args:
        mac_address (str): The MAC address in the format 'XX:XX:XX:XX:XX:XX'.

    Returns:
        int: The integer representation of the MAC address.

    """
    # Remove colons and convert to integer
    mac_address_cleaned = mac_address.replace(":", "")
    return int(mac_address_cleaned, 16)
