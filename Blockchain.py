class Blockchain:
    """
    Main module to interact with a local Ganache blockchain.

    This script establishes a connection to the Ganache blockchain and handles transactions,
    including creating and sending encrypted transactions to the blockchain.

    Dependencies:
        - get_hash: Custom module for hash-related functions.
        - rsa_enc.voyage_rsa: Custom module for RSA encryption.
        - web3: Web3.py library for interacting with Ethereum blockchain.
        - json: Standard library for JSON manipulation.
        - base64: Standard library for base64 encoding and decoding.
        - os: Standard library for operating system interactions.
        - datetime: Standard library for date and time manipulations.
        - img_encdec: Custom module for image encryption and decryption.
        - post_db: Custom module for handling post-related database operations.
        - time_ago: Custom module for displaying time in a relative format.
    """

# import hashlib
import Hash as hash
import rsa_enc.AesRsa as AesRsa
from web3 import Web3
import json,base64,os
from datetime import datetime
import ImgEnc as ied
import Database as db
import timeformatter
# Connection to Ganache
"""
Set up a connection to the Ganache local blockchain.

The script checks if the connection to the blockchain is successful and waits 
until it is established.

Example usage:
    This block runs when the script is executed directly.

Returns:
    None: Prints connection status to the console.
"""
# Set up a connection to the Ganache local blockchain
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
print("Connecting to Ganache...")
if web3.is_connected():
    print("Connected to Ganache")
else:
    print("Waiting the connection to Ganache to be established.", end="")


while (not web3.is_connected()):
    if web3.is_connected():
        print("Connected to Ganache")


print()
# Reading keys.json
"""
Load encryption keys and account details from the keys.json file.

This section reads the private key and account addresses required for signing
and sending transactions on the blockchain.

Returns:
    None: Initializes the private key and account addresses for further use.
"""
# Open and read the keys.json file
with open('keys.json', 'r') as file:
    data = json.load(file)

private_key = data["private_key"]
account_address = web3.to_checksum_address(data["account_address"])
recieve_account = web3.to_checksum_address(data["recieve_account"])

def create_transaction(data):
    """
    Create a new transaction and add it to the blockchain.

    This function encrypts the provided data and creates a transaction to store it on the blockchain.
    The data typically includes essential identifiers like "post_id" and "user_id".

    Args:
        data (dict): The information to be stored on the blockchain, such as post details or user data.
    
    Example usage:
        create_transaction({"post_id": 1, "user_id": 123})

    Returns:
        None: Prints the transaction hash and block number upon successful transaction.
    """
    # data = base64.b64encode(voyage_rsa.encrypt((data))).decode('utf-8')
    encrypted_data = AesRsa.encrypt(json.dumps(data))
    # print(encrypted_data)
    # Convert the encrypted data dictionary to a JSON string and then to bytes
    # encrypted_data_json = json.dumps(encrypted_data)
    # print(encrypted_data_json)
    # Base64 encode the encrypted data
    # data = base64.b64encode(encrypted_data_json)
    # print(data)
    if isinstance(encrypted_data, str):
        encrypted_data = encrypted_data.encode('utf-8')  # Convert string to bytes
    
    data = base64.b64encode(encrypted_data)
    txn = {
        'from': account_address,
        'to': recieve_account,
        'value': web3.to_wei(0, 'ether'),
        'gas': 2100000,
        'gasPrice': web3.to_wei('100', 'gwei'),
        'data': Web3.to_hex(data),
        # 'data':data,
        'nonce': web3.eth.get_transaction_count(account_address),
    }

    # signed_txn = web3.eth.account.sign_transaction(txn, private_key)
    signed_txn = web3.eth.account.sign_transaction(txn, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    print(f"Transaction hash: {txn_hash.hex()}")
    print("Transaction mined in block:", txn_receipt.blockNumber)
    print("Success")



def get_chain():
    """
    Retrieve all data from the blockchain.

    This function iterates through all blocks in the blockchain, decrypts the 
    encrypted transaction data, and returns the data as a list of dictionaries.
    
    Returns:
        list: A list of dictionaries containing the decrypted data from the blockchain.

    Note:
        Each transaction's input data is expected to be encrypted in base64 format.
        The function handles potential decoding and JSON parsing errors gracefully.
    """
    block_number = web3.eth.block_number
    blockchains = []

    for i in range(1, block_number + 1):
        block = web3.eth.get_block(i, full_transactions=True)
        transactions = block['transactions']

        for tx in transactions:
            raw_data_hex = tx['input']  # Hex string
            raw_data_bytes = Web3.to_bytes(raw_data_hex)  # Convert Hex string to bytes

            try:
                # Base64 decode the encrypted data
                encoded_data = base64.b64decode(raw_data_bytes)
                # Decrypt the data using RSA
                decrypted_data = AesRsa.decrypt(encoded_data)
                # print(decrypted_data)
                decrypted_data_str = decrypted_data.replace("'", '"')
                decrypted_data_str = decrypted_data_str.replace('True', 'true').replace('False', 'false')
                decrypted_data_str = decrypted_data
                # Convert to dictionary
                if decrypted_data_str.endswith(','):
                    decrypted_data_str = decrypted_data_str[:-1]  # Remove trailing comma
                blockchains.append(json.loads(decrypted_data_str))

            except (base64.binascii.Error, json.JSONDecodeError, ValueError) as e:
                # print(f"Error processing transaction {tx['hash'].hex()}: {e}")
                continue  # Skip to the next transaction

            except UnicodeDecodeError as e:
                # print(f"Unicode decoding error for transaction {tx['hash'].hex()}: {e}")
                continue  # Skip if there's a decoding error
    return blockchains

# for i in get_chain():
#     print(i)
#     print()

def get_posts():
    """
    Retrieve all posts from the blockchain.

    This function filters the blockchain data obtained from get_chain() to 
    return only those entries that contain a "post_id". It enriches each post 
    with additional content and metadata, such as the post date and user information.

    Returns:
        list: A list of enriched post dictionaries containing information 
              about each post.

    Note:
        The function retrieves the content text for each post and decrypts the image 
        if it exists in the encrypted format.
    """
    posts =  [block for block in get_chain() if "post_id" in block]
    for post in posts:
        content_post = db.retrieve_content_text(post['post_id'])
        post['content'] = content_post
        post['date'] = timeformatter.time_ago(post['date'])
        if 'postimg' in post and post['postimg'].endswith('.enc'):
            # Decrypt the image and update the post with the decrypted image path
            encrypted_image_path = post['postimg']
            if os.path.exists(encrypted_image_path):
                decrypted_image_path = ied.decrypt_image(encrypted_image_path)
                post['postimg'] = decrypted_image_path  # Replace with decrypted image path
        user_info = get_user_info(post['username'])
        if user_info:  # Check if user_info is not None
            post['name'] = user_info['name'].split(' ')[0]  # Get the first name
        else:
            post['name'] = "Unknown"
    return posts

def get_user_number_of_post(username):
    """
    Count the total number of posts made by a specific user.

    This function iterates through the list of posts and counts how many 
    posts belong to the user identified by the provided username.

    Args:
        username (str): The username of the user whose post count is to be retrieved.

    Returns:
        int: The total number of posts made by the user.

    Note:
        The function relies on the get_posts() function to obtain the list of posts.
    """
    user_posts = []
    for post in get_posts():
        # print(user)
        if username == str(post['username']):
            user_posts.append(post)
    return len(user_posts)

def get_user_posts(username):
    """
    Retrieve all posts made by a specific user.

    This function takes a username as input and returns a list of 
    all posts associated with that user by utilizing the get_posts() 
    function to fetch the complete list of posts.

    Args:
        username (str): The username of the user whose posts are to be retrieved.

    Returns:
        list: A list of dictionaries representing the posts made by the user.
    """
    user_posts = []
    for post in get_posts():
        # print(user)
        if username == str(post['username']):
            user_posts.append(post)
    return user_posts

"""
    # if 'decrypted_images' not in session:
    #     session['decrypted_images'] = []
    # session['decrypted_images'].append(decrypted_image_path)
"""

def get_user_data():
    """
    Retrieve all user data stored in the blockchain.

    This function searches for entries containing the "uhash" key in 
    the blockchain data and returns a list of user data dictionaries. 
    Each user entry is enriched with additional details such as the 
    user's name, the time since registration, and the number of posts.

    Returns:
        list: A list of dictionaries containing enriched user data.
    """
    user_data = [block for block in get_chain() if 'uhash' in block]
    # print(user_data)
    for user in user_data:
        # user = {**user, **db.retrieve_user_data(user['user_id'])}
        user_details = db.retrieve_user_data(user['user_id'])
        user.update(user_details) # merges both dictionary
        user['name'] = str(user['name'])
        user['time_ago'] = timeformatter.time_ago(user['date'])
        user['no_of_posts'] = get_user_number_of_post(user['username']) #temp
    return user_data
    # time_ago.time_ago(post['date'])
    # return [{**block, 'name': str(block['name']).capitalize()} for block in get_chain() if 'password' in block]

def get_user_info(username):
    """
    Retrieve detailed information about a specific user.

    This function takes a username as input and searches through the 
    blockchain data to return the complete user object as a dictionary.

    Args:
        username (str): The username of the user whose information is to be retrieved.

    Returns:
        dict: A dictionary containing the user's information, or None if the user is not found.
    """
    user_data = [block for block in get_chain() if 'uhash' in block]
    # print(user_data)
    for user in user_data:
        # user = {**user, **db.retrieve_user_data(user['user_id'])}
        user_details = db.retrieve_user_data(user['user_id'])
        user.update(user_details) # merges both dictionary

    for user in reversed(user_data):
        if username ==user['username']:
            return user
    return None


def get_userId(username):
    """
    Retrieve the user ID associated with a given username.

    This function takes a username as input and searches for it 
    within the user data retrieved from the blockchain to return 
    the corresponding user ID.

    Args:
        username (str): The username for which the user ID is to be retrieved.

    Returns:
        str: The user ID associated with the username, or "NULL" if not found.
    """
    for user in reversed(get_user_data()):
        if username == user['username']:
            return user['user_id']
    return "NULL"

def get_userName(uid):
    """
    Retrieve the username associated with a given user ID.

    This function takes a user ID as input and searches for it 
    within the user data retrieved from the blockchain to return 
    the corresponding username.

    Args:
        uid (str): The user ID for which the username is to be retrieved.

    Returns:
        str: The username associated with the user ID, or "NULL" if not found.
    """
    for user in reversed(get_user_data()):
        if uid == user['user_id']:
            return user['username']
    return "NULL"

# print(get_user_info('agha')['name'])
"""
def get_posts():
    #Get all posts from the blockchain.
    posts =  [block for block in get_chain() if "post_id" in block]
    for post in posts:
        content_post = db.retrieve_content_text(post['post_id'])
        post['content'] = content_post
        post['date'] = time_ago.time_ago(post['date'])

        if 'postimg' in post and post['postimg'].endswith('.enc'):
            # Decrypt the image and update the post with the decrypted image path
            encrypted_image_path = post['postimg']
            if os.path.exists(encrypted_image_path):
                decrypted_image_path = ied.decrypt_image(encrypted_image_path)
                post['postimg'] = decrypted_image_path  # Replace with decrypted image path

        user_info = get_user_info(post['username'])
        
        if user_info:  # Check if user_info is not None
            post['name'] = user_info['name'].split(' ')[0]  # Get the first name
        else:
            post['name'] = "Unknown"

    return posts"""

def get_post_info(post_id):
    """
    Retrieve full information of a specific post based on post_id.

    This function searches for the post in the blockchain using the 
    get_posts() function and returns the corresponding post's details 
    along with a flag indicating whether the post exists.

    Args:
        post_id (str): The unique identifier for the post.

    Returns:
        list: A list containing the post dictionary and a boolean flag 
              indicating the existence of the post.
    """
    postFlag = False
    try:
        post = [block for block in get_posts() if block["post_id"]==post_id][0]
    except:
        post = []
    if post:
        postFlag = True
    postReturn = [post,postFlag]
    return postReturn



def add_new_user(username, password, email, phone, name, datenow=None, ):
    """
    Add a new user to the blockchain and database.

    This function creates a new user block in the blockchain, 
    generating a unique user hash (uhash) and user ID (user_id). 
    It stores relevant user details both in the database and the blockchain.

    Args:
        username (str): The username for the new user.
        password (str): The password for the new user.
        email (str): The email address of the new user.
        phone (str): The phone number of the new user.
        name (str): The full name of the new user.
        datenow (datetime, optional): The timestamp for user creation. 
                                       Defaults to current time if not provided.
    """
    
    isAdmin = username in ['admin', 'agha']
    if not datenow:
        datenow = datetime.now()

    # uid = get_hash.get_hash(data=username)[:10]

    # data = {"block": "User Block", "username": username, "password": password,
    #         "email": email, "phone": phone, "name": name, "Admin": isAdmin, "date": datenow}
    if type(datenow) is str:
        datenow = datetime.strptime(datenow, "%Y-%m-%d %H:%M:%S.%f")
    
    uid_hash = str(datenow.strftime("%d%m%y%H%M%S")+username+name+email+phone) ## makemthisMAX more can be added, but they would be uselsss, this max would be enough
    uid = hash.get_hash(uid_hash)[:15]
    
    user_data_hash = str(username+name+phone)
    uhash =hash.get_hash(user_data_hash)[:15]
    # hash_hex = get_hash.get_hash(data=uniq)

    data = {"user_id": uid, "uhash":uhash, "Admin": isAdmin, "date": str(datenow)}
    data_dict = {
        "username": username,
        "password": password,
        "email": email,
        "phone": phone,
        "name": name,
        "isAdmin": isAdmin,
        "user_id": uid
    }
    # print(data_dict,data)
    db.insert_user_data(data_dict['user_id'], data_dict)
    # merged_data = {**data, **data_dict}
    create_transaction(data)


def add_old_user(old_user, password, phone, name):
    """
    Update user information for an existing user.

    This function takes the old user details and updates the 
    necessary fields (password, phone, name) by creating a new user block.
    It retains the original username and email to ensure continuity.

    Args:
        old_user (dict): The existing user's data.
        password (str): The new password for the user.
        phone (str): The new phone number for the user.
        name (str): The new name for the user.

    Returns:
        dict: The updated user information after modification.
    """
    add_new_user(old_user['username'], password, old_user['email'], phone, name, old_user['date'])
    # Function to return the present user with the changed profile.
    for user in  reversed(get_user_data()):
        if str(old_user['username']) == str(user['username']):
            return user
    return old_user

def add_new_post(username, content:str, filename):
    """
    Add a new post to the blockchain.

    This function creates a new post block in the blockchain 
    with details such as post ID, username, content, and any 
    associated multimedia file. The post content is also stored 
    in the database.

    Args:
        username (str): The username of the post creator.
        content (str): The text content of the post.
        filename (str): The filename of the multimedia associated with the post.
    """
    datenow = datetime.now()
    # post_date = datenow.strftime("%Y-%m-%d %H:%M:%S")
    post_date = str(datenow)
    uniq = str(datenow.strftime("%d%m%y%H%M%S")+username+filename+content) ## more can be added, but they would be uselsss, this max would be enough
    hash_hex = hash.get_hash(data=uniq)
    #  Generate the SHA-256 hash
    # hash_object = hashlib.sha256(uniq.encode())
    #  Get the hexadecimal digest
    # hash_hex = hash_object.hexdigest()
    post_id = hash_hex[:10] #16^10  =   1,099,511,627,776 total possible user ids
    # print("10-digit Hex Hash:", post_id)
    user_id = get_userId(username)
    """ HERE content is saved to database """
    content = content.replace('"', '``').replace("'", '`') #later change this to hex to get all codes
    db.insert_content_text(post_id,content)
    # data = {"post_id":post_id, "username": username, "content": content, "date": post_date, "postimg":filename}
    data = {"post_id":post_id, "username": username, "date": post_date, "postimg":filename, "user_id":user_id}
    create_transaction(data)

import random

def get_user_list_for_username(username):
    current_user_id = get_userId(username)
    user_data = get_user_data()
    friend_list = getFriendList(current_user_id)

    user_list = []

    for user in user_data:
        if user['user_id'] == current_user_id:
            continue
        
        user_info = {
            'name': user['name'],
            'isFollowing': 'true' if user['user_id'] in friend_list else 'false',
            'user_id':user['user_id'],
            'username': user['username'],
        }
        user_list.append(user_info)
    
    random.shuffle(user_list)
    return user_list

"""
Function to interact and serves as gateway to Database "db".
"""
def update_post(pid,data):
    """
    Update the content of an existing post.

    This function takes the post ID and the new content to 
    update the specified post in the database.

    Args:
        pid (str): The unique identifier of the post to be updated.
        data (str): The new content for the post.
    """
    db.insert_content_text(pid,data)

def getFriendList(uid):
    """
    Retrieve the list of friends for a given user.

    Args:
        uid (str): The user ID of the user.

    Returns:
        list: A list of friends for the user.
    """
    return db.retrieve_user_friend(uid)


def getFollowingList(uid):
    """
    Retrieve the list of users that a given user is following.

    Args:
        uid (str): The user ID of the user.

    Returns:
        list: A list of users that the user is following.
    """
    return db.retrieve_user_follower(uid)



def send_friend_request(uid, friendUID):
    return db.send_friend_request(uid, friendUID)

def cancel_friend_request(uid, friendUID):
    return db.cancel_friend_request(uid, friendUID)

def approve_friend_request(uid, friendUID):
    return db.approve_friend_request(friendUID, uid)

def remove_friend(uid, friendUID):
    return db.remove_friend(uid, friendUID)

def get_pending_requests(uid):
    return db.get_pending_requests(uid)

def sent_pending_requests(uid):
    return db.sent_pending_requests(uid)



"""
# This line of code is to add some new users to the blockchain.
users = [
    {"username": "aisha_life", "password": "Aisha123!", "email": "aisha.life@example.com", "phone": "555-8765", "name": "Aisha Malik"},
    {"username": "fatimah87", "password": "Fatimah!87", "email": "fatimah_87@example.com", "phone": "555-9345", "name": "Fatimah Ali"},
    {"username": "khadi_jay", "password": "KhadiJay88", "email": "khadi.jay@example.com", "phone": "555-1023", "name": "Khadija Jamil"},
    {"username": "maryamXoxo", "password": "MaryaM*2024", "email": "maryamxo@example.com", "phone": "555-3345", "name": "Maryam Khan"},
    {"username": "amina_smile", "password": "Aminasmile21", "email": "amina.smile@example.com", "phone": "555-4456", "name": "Amina Hassan"},
    {"username": "zainab_qwerty", "password": "ZainabQ!99", "email": "zainabq@example.com", "phone": "555-9287", "name": "Zainab Qureshi"},
    {"username": "safiyah_girl", "password": "SafiYA95", "email": "safiyah95@example.com", "phone": "555-7624", "name": "Safiya Karim"},
    {"username": "hafsa_22", "password": "HafsA@22", "email": "hafsa_22@example.com", "phone": "555-3648", "name": "Hafsa Siddiqi"},
    {"username": "asma_clouds", "password": "AsmAclouds", "email": "asmaclouds@example.com", "phone": "555-8265", "name": "Asma Sheikh"},
    {"username": "sara_rays", "password": "SaraSunshine!1", "email": "sararays@example.com", "phone": "555-4739", "name": "Sara Ahmed"},
    {"username": "noor_light", "password": "Noor1234!", "email": "noorlight@example.com", "phone": "555-5172", "name": "Noor Farooq"},
    {"username": "leila_dreamer", "password": "LeilaD!ream", "email": "leiladreamer@example.com", "phone": "555-3812", "name": "Leila Mahmoud"},
    {"username": "sumayyah_star", "password": "Sumayyah!123", "email": "sumayyah.star@example.com", "phone": "555-7326", "name": "Sumayyah Zafar"},
    {"username": "ran_ran12", "password": "Rani12Ran!", "email": "ran.ran12@example.com", "phone": "555-9832", "name": "Raniya Patel"},
]

for user in users:
    add_new_user(user['username'],user['password'],user['email'],user['phone'],user['name'])
    
"""



"""TEST CODE"""
# print(get_chain())
# print(get_post_info('267c257799'))
# print(get_posts())

# print(get_user_info('agha'))
# print(get_user_data())
# print(get_user_info('2c4f46f313c85a7'))
# print(get_user_data())
# print(get_chain())
# add_new_user('agha','agha','agha','agha','agha')
# for i in get_user_data():
#     # print('aaaa')
#     print(i)
    # print(i['uhash'])


# print(get_posts())
# Example usage:
# add_new_user('agha', 'agha_password')
# add_new_post('agha', 'Working on my final year project','static/uploaded_files/300924212127aghajpeg.enc')
# print(get_posts())
# print(get_user_data())
# add_new_user('agha','agha')
# j=0
# for i in get_posts()+get_user_data():
#     j+=1s
#     print(j,end="> ")
#     print(i)

# add_new_post('agha','b','c')
# x=0

# for i in get_chain():
#     print(i)
#     print()

# for i in get_posts():
#     print(i)

# for i in get_user_data():
    # print(i)

# for i in get_user_number_of_post():
    # print(i)

# for i in get_user_posts('agha'):
#     print(i)


# post = {'post_id': 'c82bf5ae97', 'username': 'agha', 'date': '23m ago', 'postimg': 'static/uploaded_files/111024125847aghawebp_decrypted.jpg', 'content': 'aa'}
# post['name'] = get_user_info(post['username'])['name'].split(' ')[0]
# print(post)



# userList = [{'name':'Agha', 'isFollowing':'false'},{'name':'Admin', 'isFollowing':'true'}]
