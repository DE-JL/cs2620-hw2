from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

public_key_path = "keys/public_key.pem"
private_key_path = "keys/private_key.pem"

def encrypt_password(password):
    # Load public key
    """
    Encrypts a given password using the public key stored in keys/public_key.pem
    and returns the result as a base64-encoded string.

    :param password: The password to be encrypted
    :type password: str
    :return: The encrypted password as a base64-encoded string
    :rtype: str
    """
    with open("keys/public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # Encrypt password
    encrypted_password = public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    encrypted_password_b64 = base64.b64encode(encrypted_password).decode()

    return encrypted_password_b64

def decrypt_password(encrypted_password_b64):
    """
    Decrypts a given base64-encoded string using the private key stored in keys/private_key.pem
    and returns the result as a string.

    :param encrypted_password_b64: The base64-encoded string to be decrypted
    :type encrypted_password_b64: str
    :return: The decrypted password as a string
    :rtype: str
    """
    encrypted_password_bytes = base64.b64decode(encrypted_password_b64)

    # Load private key
    with open("keys/private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Decrypt password
    decrypted_password = private_key.decrypt(
        encrypted_password_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_password.decode()

# Simple unit test for password encryption strategy
if __name__ == "__main__":
    password = "my_secure_password"
    encrypted_password_b64 = encrypt_password(password)
    decrypted_password = decrypt_password(encrypted_password_b64)
    print(f"Original password: {password}")
    print(f"Encrypted password: {encrypted_password_b64}")
    print(f"Decrypted password: {decrypted_password}")
    print(f"Original password == Decrypted password: {password == decrypted_password}")
