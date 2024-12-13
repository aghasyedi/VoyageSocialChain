def right_rotate(value, amount):
    """Performs a right rotation on a 32-bit integer.
    
    Parameters:
    - value (int): The integer to rotate.
    - amount (int): The number of positions to rotate.
    
    Returns:
    - int: The rotated integer.
    """
    return ((value >> amount) | (value << (32 - amount))) & 0xFFFFFFFF

def pad_message(message):
    """Pads the message according to SHA-1 specifications.
    
    Parameters:
    - message (bytes): The original message to be padded.
    
    Returns:
    - bytes: The padded message.
    """
    original_byte_len = len(message)
    original_bit_len = original_byte_len * 8
    message += b'\x80'  # Append the bit '1' to the message

    # Padding with zeros until the message length is congruent to 448 mod 512
    while (len(message) * 8) % 512 != 448:
        message += b'\x00'

    # Append the original length as a 64-bit big-endian integer
    for i in range(8):
        message += (original_bit_len >> (56 - 8 * i) & 0xFF).to_bytes(1, 'big')
    return message

def process_chunk(chunk, h):
    """Processes a 512-bit chunk of the message with a fixed number of rounds.
    
    Parameters:
    - chunk (bytes): The 512-bit chunk to process.
    - h (list): The current hash values.
    
    Returns:
    - list: The updated hash values.
    """
    # Prepare the message schedule (80 words)
    w = list(int.from_bytes(chunk[i:i + 4], 'big') for i in range(0, 64, 4)) + [0] * 80

    for i in range(16, 80):
        w[i] = right_rotate(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1)

    a, b, c, d, e = h

    for i in range(80):  # Fixed number of rounds
        if i < 20:
            f = (b & c) | (~b & d)
            k = 0x5A827999
        elif i < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif i < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        temp = (right_rotate(a, 5) + f + e + k + w[i]) & 0xFFFFFFFF
        e = d
        d = c
        c = right_rotate(b, 30)
        b = a
        a = temp

    # Update the hash state
    return [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e])]

def sha1(message):
    """Generates a SHA-1 hash of the input message as a hexadecimal string.
    
    Parameters:
    - message (str): The data to hash.
    
    Returns:
    - str: The SHA-1 hash of the input message as a hexadecimal string.
    """
    # Initial hash values
    h = [   0x67452301,
            0xEFCDAB89,
            0x98BADCFE,
            0x10325476,
            0xC3D2E1F0
    ]

    # Convert the input string to bytes
    message_bytes = message.encode('utf-8')

    # Pad the message
    padded_message = pad_message(message_bytes)
    
    # Process each 512-bit chunk
    for i in range(0, len(padded_message), 64):
        h = process_chunk(padded_message[i:i + 64], h)

    # Produce the final hash value
    return ''.join(hv.to_bytes(4, 'big').hex() for hv in h)


def get_hash(data):
    """Generates a SHA-1 hash of the input message as a hexadecimal string.
    
    Parameters:
    - message (str): The data to hash.
    
    Returns:
    - str: The SHA-1 hash of the input message as a hexadecimal string.
    """
    
    return sha1(data)

# word = r"""UUIDv8: 032ccab6064f-837088aa540a91e2ab66-88aa-540a-91e2ab66

# (base) D:\AGHA\SHUATS\Notes\Sem-7\Project\Social MEdia>C:/Users/aghas/anaconda3/python.exe "d:/AGHA/SHUATS/Notes/Sem-7/Project/Social MEdia/temp.py"
# Generated UUIDv8: 48abb20b-28b6-7a08-80f2-3bdbc74309b9

# (base) D:\AGHA\SHUATS\Notes\Sem-7\Project\Social MEdia>C:/Users/aghas/anaconda3/python.exe "d:/AGHA/SHUATS/Notes/Sem-7/Project/Social MEdia/temp.py"
# Generated UUIDv8: bb8530d1-62dc-48a8-80c1-0e3bb9cd692e

# (base) D:\AGHA\SHUATS\Notes\Sem-7\Project\Social MEdia>C:/Users/aghas/anaconda3/python.exe "d:/AGHA/SHUATS/Notes/Sem-7/Project/Social MEdia/temp.py"
# Generated UUIDv8: 02f40c07-f39d-b018-80f8-0df3384e570c"""

# print(get_hash(word))
# print(sha1(word))



"""
This script provides functionality for hashing and message padding using the SHA-1 algorithm.

It includes a SHA-1 implementation that adheres to the SHA-1 specifications, allowing for message
padding, chunk processing, and hash computation. It also includes a utility to compute SHA-256 hashes
and an optional UUID generator.

Modules:
- hashlib: Used for generating SHA-256 hashes.
- uuid: Provides functionality for generating UUIDs, specifically UUIDv4 (not used directly in the program).

Functions:
1. get_hash(data):
    Description:
        Computes and returns a SHA-1 hash of the given input data.
    Parameters:
        - data (str): Input string to be hashed.
    Returns:
        - str: Hexadecimal string representation of the SHA-1 hash.

2. right_rotate(value, amount):
    Description:
        Performs a right rotation (circular shift) on a 32-bit integer by the specified amount.
    Parameters:
        - value (int): Integer to rotate.
        - amount (int): Number of positions to rotate.
    Returns:
        - int: The rotated integer.

3. pad_message(message):
    Description:
        Pads the message according to SHA-1 specifications. Adds a single '1' bit,
        followed by '0' bits, then appends the original message length as a 64-bit big-endian integer.
    Parameters:
        - message (bytes): Original message in bytes.
    Returns:
        - bytes: Padded message.

4. process_chunk(chunk, h):
    Description:
        Processes a 512-bit message chunk with SHA-1 specific rounds, updating the hash values.
    Parameters:
        - chunk (bytes): The 512-bit chunk to be processed.
        - h (list): List of five 32-bit initial hash values.
    Returns:
        - list: Updated hash values after processing the chunk.

5. sha1(message):
    Description:
        Generates a SHA-1 hash of the input message by encoding the message to bytes, padding it,
        processing each 512-bit chunk, and computing the final hash value.
    Parameters:
        - message (str): Input message to be hashed.
    Returns:
        - str: SHA-1 hash as a hexadecimal string.
"""


"""
Another way to get Hash
This function uses the SHA-256 using python built-in library 'hashlib'. 
"""

# import hashlib

# def get_hash(data):
#     """
#     Generate a SHA-256 hash of the input data.

#     Args:
#         data (str): The input string to hash.

#     Returns:
#         str: The hexadecimal digest of the SHA-256 hash.
#     """
#     # Generate the SHA-256 hash
#     hash_object = hashlib.sha256(data.encode())
#     print(type(hash_object.hexdigest()))
    
#     # Get the hexadecimal digest
#     return hash_object.hexdigest()
#     # return hashlib.sha256(data.encode()).hexdigest()
    

# This function generates and returns a random UUID (Universally Unique Identifier) using uuid4, version 4.
"""
import uuid
def get_hash():
    return uuid.uuid4()
"""
# Not using in our program because we may need to verify some of the hashes.