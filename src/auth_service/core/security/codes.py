import secrets
import string


def generate_numeric_code(length: int = 6) -> str:
    alphabet = string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
