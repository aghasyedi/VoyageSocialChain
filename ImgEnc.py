from cryptography.fernet import Fernet,os

# Step 1: Generate encryption key (do this only once and store it securely)
# key = Fernet.generate_key()
# with open('secret.key', 'wb') as key_file:
#     key_file.write(key)

# Step 2: Load the key
def load_key():
    """
    Load the encryption key from a file.

    Returns:
        bytes: The encryption key.
    """
    return open('secret.key', 'rb').read()

# Step 3: Encrypt the image file
def encrypt_image(image_path):
    """
    Encrypt an image file.

    Args:
        image_path (str): Path to the image file to encrypt.

    Returns:
        str: Path to the encrypted image file.
    """
    key = load_key()
    cipher = Fernet(key)
    print(image_path)
    image_path= f"static/uploaded_files/"+image_path

    # Open and read the image file
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Encrypt the image data
    encrypted_data = cipher.encrypt(image_data)
    # os.remove
    # Save the encrypted image
    encrypted_image_path = image_path + '.enc'
    with open(encrypted_image_path, 'wb') as enc_file:
        enc_file.write(encrypted_data)
    print((encrypted_image_path))
    
# Delete the original image after encryption
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"Original image deleted: {image_path}")
    return encrypted_image_path

def decrypt_image(encrypted_image_path):
    """
    Decrypt an encrypted image file.

    Args:
        encrypted_image_path (str): Path to the encrypted image file.

    Returns:
        str: Path to the decrypted image file.
    """
    key = load_key()
    cipher = Fernet(key)

    # Open and read the encrypted image file
    with open(encrypted_image_path, 'rb') as enc_file:
        encrypted_data = enc_file.read()

    # Decrypt the image data
    decrypted_data = cipher.decrypt(encrypted_data)

    # Save the decrypted image
    decrypted_image_path = encrypted_image_path.replace('.enc', '_decrypted.jpg')
    with open(decrypted_image_path, 'wb') as dec_file:
        dec_file.write(decrypted_data)
    

    return decrypted_image_path

# print(type(encrypt_image('static/uploaded_files/3.png')))
# print(type(decrypt_image('static/uploaded_files/3.png.enc')))
