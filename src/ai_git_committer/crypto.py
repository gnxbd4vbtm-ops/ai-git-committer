"""Fernet symmetric encryption for securely storing API keys."""

import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from .exceptions import CryptoError
from .utils import get_logger

logger = get_logger()


def get_or_create_fernet_key(key_path: Path) -> bytes:
    """Retrieve existing Fernet key or generate a new key file securely.

    Args:
        key_path: Path to the api.key file.

    Returns:
        Fernet key bytes.

    Raises:
        CryptoError: If key file read/write fails.
    """
    if key_path.exists():
        try:
            key_data = key_path.read_bytes().strip()
            if key_data:
                return key_data
        except Exception as err:
            raise CryptoError(f"Failed to read encryption key file at {key_path}: {err}") from err

    logger.debug("Generating new Fernet encryption key at %s", key_path)
    try:
        key_path.parent.mkdir(parents=True, exist_ok=True)
        new_key = Fernet.generate_key()
        key_path.write_bytes(new_key)
        os.chmod(key_path, 0o600)
        return new_key
    except Exception as err:
        raise CryptoError(f"Failed to create encryption key at {key_path}: {err}") from err


def store_encrypted_api_key(api_key: str, key_path: Path, secret_path: Path) -> None:
    """Encrypt and store the provided Groq API key securely on disk.

    Args:
        api_key: Plaintext API key string.
        key_path: Path to api.key file.
        secret_path: Path to secrets.enc file.

    Raises:
        CryptoError: If encryption or file saving fails.
    """
    if not api_key or not api_key.strip():
        raise CryptoError("API key cannot be empty.")

    fernet_key = get_or_create_fernet_key(key_path)
    try:
        fernet = Fernet(fernet_key)
        encrypted_bytes = fernet.encrypt(api_key.strip().encode("utf-8"))
        secret_path.parent.mkdir(parents=True, exist_ok=True)
        secret_path.write_bytes(encrypted_bytes)
        os.chmod(secret_path, 0o600)
        logger.debug("Successfully encrypted API key to %s", secret_path)
    except Exception as err:
        raise CryptoError(f"Failed to encrypt API key: {err}") from err


def load_decrypted_api_key(key_path: Path, secret_path: Path) -> Optional[str]:
    """Load and decrypt the stored Groq API key.

    Args:
        key_path: Path to api.key file.
        secret_path: Path to secrets.enc file.

    Returns:
        Decrypted API key string, or None if secret file does not exist.

    Raises:
        CryptoError: If key is corrupt or decryption fails.
    """
    if not secret_path.exists():
        return None

    if not key_path.exists():
        raise CryptoError(
            f"Encrypted secrets file exists at {secret_path}, but decryption key is missing at {key_path}."
        )

    try:
        fernet_key = get_or_create_fernet_key(key_path)
        fernet = Fernet(fernet_key)
        encrypted_data = secret_path.read_bytes()
        decrypted_bytes = fernet.decrypt(encrypted_data)
        return decrypted_bytes.decode("utf-8")
    except InvalidToken as err:
        raise CryptoError(
            "Failed to decrypt API key: Invalid or corrupted token. Please re-enter your key with --api-key."
        ) from err
    except Exception as err:
        raise CryptoError(f"Error reading encrypted API key: {err}") from err
