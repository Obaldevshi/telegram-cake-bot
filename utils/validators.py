def is_valid_address(address: str) -> bool:
    return address is not None and len(address.strip()) >= 10

def is_positive_integer(value: str) -> bool:
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False
