import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Load the private key from a PEM file
def load_private_key(filename):
    """
    Load the private key from a PEM file.

    Args:
        filename (str): The path to the PEM file containing the private key.

    Returns:
        PrivateKey: The loaded private key.
    """
    
    with open(filename, 'rb') as f:
        pem_data = f.read()
    
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,  # Add your password if the key is encrypted
        backend=default_backend()
    )
    
    return private_key

# Load the public key from a PEM file
def load_public_key(filename):
    """
    Load the public key from a PEM file.

    Args:
        filename (str): The path to the PEM file containing the public key.

    Returns:
        PublicKey: The loaded public key.
    """
    with open(filename, 'rb') as f:
        pem_data = f.read()

    public_key = serialization.load_pem_public_key(
        pem_data,
        backend=default_backend()
    )
    
    return public_key

def load_from_pem(filename):
    """
    Load and decode the content from a PEM file.

    Args:
        filename (str): The path to the PEM file.

    Returns:
        bytes: The base64-decoded content of the PEM file.
    """
    with open(filename, 'r') as f:
        pem_data = f.read()
    b64_data = '\n'.join(pem_data.splitlines()[1:-1])  # no head and footer
    return base64.b64decode(b64_data)

# Load keys and parameters
FIXED_SYMMETRIC_KEY = load_from_pem('rsa_enc/symmetric_key.pem')
FIXED_IV = load_from_pem('rsa_enc/iv.pem')
private_key = load_private_key('rsa_enc/private_key.pem')
public_key = load_public_key('rsa_enc/public_key.pem')

# Encrypt the symmetric key with the RSA public key
encrypted_symmetric_key = public_key.encrypt(
    FIXED_SYMMETRIC_KEY,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Decrypt the symmetric key with the RSA private key
symmetric_key = private_key.decrypt(
    encrypted_symmetric_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Encrypt a message using hybrid encryption
def encrypt(message):
    """
    Encrypt a message using a fixed symmetric key.

    Args:
        message (str or bytes): The message to encrypt.

    Returns:
        str: The base64-encoded ciphertext.
    """
    if isinstance(message, str):
        message = message.encode('utf-8')

    # Encrypt the message using the fixed symmetric key
    cipher = Cipher(algorithms.AES(FIXED_SYMMETRIC_KEY), modes.CFB(FIXED_IV), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message) + encryptor.finalize()

    # Return only the base64 encoded ciphertext
    return base64.b64encode(ciphertext).decode('utf-8')

# Decrypt a message using hybrid encryption
def decrypt(ciphertext_b64):
    """
    Decrypt a base64-encoded ciphertext.

    Args:
        ciphertext_b64 (str): The base64-encoded ciphertext to decrypt.

    Returns:
        str: The decrypted plaintext message.
    """
    try:
        # Decode the ciphertext from base64
        ciphertext = base64.b64decode(ciphertext_b64)
    except (ValueError, TypeError) as e:
        print("Error decoding ciphertext:", e)
        return None

    # Decrypt the message using the symmetric key
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(FIXED_IV), backend=default_backend())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Return the decoded plaintext as a string
    return plaintext.decode('utf-8', errors='ignore')

# Example usage
# if __name__ == "__main__":
#     # Create a large message for testing
#     message = '2' * 1000  # Example large message
#     print("Original message (length):", len(message))  # Display the length of the message

#     # Encrypt the message
#     ciphertext = encrypt(message)
#     print("Encrypted message:", ciphertext)  # This will print the base64 encoded ciphertext
    
#     # Decrypt the message
#     decrypted_message = decrypt(ciphertext)
#     print("Decrypted message:", decrypted_message)


# print(decrypt("IlBnVHFmV0NiRzlMTW1DN004T1YwVU5XcGhObi96TnU4MEtvbmFTUEZGKzQ3Ykl1eHZqMkp3Qmdlc25OR045MS9Kd2hwMUJwbjJkSGk3a2UvMTVqYkVYWitlaHkzb1o1dnNGd2Z3SmtwbE1MdXcvRk4rOXpKamk1S1dTMi92TlRXazRzbEFaSWtRaDM0dzFjVGxYSU0i".encode('utf-8')))

# a = encrypt('Agha Tasheer Syedi')
# print(a)
# print(decrypt("BEH3byW9JcjA33Ge8o4+V2Dw"))