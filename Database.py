import json
import sqlite3
from rsa_enc import AesRsa


# Step 1: conn_contentect to the SQLite database with a timeout to avoid "database is locked" errors
conn_content = sqlite3.connect("static/database/content.db", timeout=10, check_same_thread=False)  # Set timeout to wait for 10 seconds if database is locked
cursor_content = conn_content.cursor()

conn_udata = sqlite3.connect("static/database/userdata.db", timeout=10, check_same_thread=False)  # Set timeout to wait for 10 seconds if database is locked
cursor_udata = conn_udata.cursor()

conn_flist = sqlite3.connect("static/database/friends.db", timeout=10, check_same_thread=False)  # Set timeout to wait for 10 seconds if database is locked
cursor_flist = conn_flist.cursor()

conn_ffollowing = sqlite3.connect("static/database/friendfollowing.db", timeout=10, check_same_thread=False)  # Set timeout to wait for 10 seconds if database is locked
cursor_ffollowing = conn_ffollowing.cursor()


#pid     ->      post_id

# Step 2: Create a table (if it doesn't exist)
try:
    cursor_content.execute("""
        CREATE TABLE "content" (
    	"pid"	TEXT NOT NULL UNIQUE,
    	"data"	TEXT NOT NULL,
    	PRIMARY KEY("pid")
    );
    """)
except:
    pass

try:
    # cursor_udata.execute("""
    #     CREATE TABLE "userdata" (
    #     "uid"   TEXT NOT NULL UNIQUE,
    #     "data"  TEXT NOT NULL,
    #     PRIMARY KEY("uid")
    # );
    # """)
    cursor_udata.execute("""
        CREATE TABLE "userdata" (
        "uid"   TEXT NOT NULL,
        "data"  TEXT NOT NULL
    );
    """)
except:
    pass

try:
    cursor_flist.execute("""
        CREATE TABLE "friends" (
        "uid"   TEXT NOT NULL UNIQUE,
        "friendlist"  TEXT NOT NULL,
        PRIMARY KEY("uid")
    );
    """)
except:
    pass

try:
    cursor_flist.execute("""
        CREATE TABLE "friendfollowing" (
        "uid"   TEXT NOT NULL UNIQUE,
        "friendlist"  TEXT NOT NULL,
        PRIMARY KEY("uid")
    );
    """)
except:
    pass

try:
    cursor_flist.execute("""
        CREATE TABLE "friendRequests" (
        uid TEXT NOT NULL,
        friendUID TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'cancelled')),
        PRIMARY KEY (uid, friendUID)
    );
    """)
except:
    pass

def insert_user_data(uid, data):
    """
    Insert user data into the userdata table.

    Args:
        uid (str): Unique user ID.
        data (dict): User data to insert.
    """
    # Convert data dictionary to JSON format for cleaner storage
    data_json = json.dumps(data)
    
    # Encrypt the JSON string
    encrypted_data = AesRsa.encrypt(data_json)  # This should return a dict

    # Store the encrypted data as JSON encoded string
    cursor_udata.execute("""
        INSERT INTO userdata (uid, data) 
        VALUES (?, ?)
    """, (uid, json.dumps(encrypted_data)))

    conn_udata.commit()  # Save the changes

def retrieve_user_data(uid):
    """
    Retrieve user data from the userdata table.

    Args:
        uid (str): Unique user ID.

    Returns:
        dict: Decrypted user data or None if an error occurs.
    """
    cursor_udata.execute('SELECT * FROM userdata WHERE uid = ?', (uid,))
    try:
        # Last saved user data in database
        encrypted_data = cursor_udata.fetchall()[-1][1]  # Get the encrypted data
        # encrypted_data = cursor_udata.fetchone()[1] 
        # print(encrypted_data)
        # print(cursor_udata.fetchall()[-1][1])
        encrypted_data = json.loads(encrypted_data)  # Decode back from JSON

        decrypted_data = AesRsa.decrypt(encrypted_data)
        return json.loads(decrypted_data)  # Return as dictionary
    except Exception as e:
        print("Error retrieving data:", e)
        return None

# print(retrieve_user_data('679ba730c20faf0'))
def insert_content_text(pid, data):
    """
    Insert content text into the content table.

    Args:
        pid (str): Unique post ID.
        data (str): Content text to insert.
    """
    # Convert data to bytes if it's a string
    if isinstance(data, str):
        data = data.encode('utf-8')  # Encode to bytes

    # Encrypt the data
    encrypted_data = AesRsa.encrypt(data)  # Ensure this returns a dictionary

    # Insert the encrypted data into the database
    try:
        cursor_content.execute("""
            INSERT INTO content (pid, data) 
            VALUES (?, ?)
        """, (pid, json.dumps(encrypted_data)))
    except:
        delete_content(pid)
        cursor_content.execute("""
            INSERT INTO content (pid, data) 
            VALUES (?, ?)
        """, (pid, json.dumps(encrypted_data)))
        
    conn_content.commit()  # Save the changes

def retrieve_content_text(pid):
    """
    Retrieve content text from the content table.

    Args:
        pid (str): Unique post ID.

    Returns:
        str: Decrypted content text or None if an error occurs.
    """
    cursor_content.execute('SELECT * FROM content WHERE pid = ?', (pid,))
    try:
        encrypted_data = cursor_content.fetchall()[0][1]  # Fetch encrypted data
        encrypted_data = json.loads(encrypted_data)  # Decode back from JSON
        decrypted_data = AesRsa.decrypt(encrypted_data)
        return decrypted_data  # Return as strings
    except Exception as e:
        # print("Error retrieving content:", e)
        return None

def delete_content(pid):
    """
    Delete content from the content table.

    Args:
        pid (str): Unique post ID.
    """
    try:
        cursor_content.execute('DELETE FROM content WHERE pid = ?', (pid,))
        conn_content.commit()  # Commit the transaction to apply changes
        # print(f"Content with pid {pid} has been deleted successfully.")
    except Exception as e:
        print("Error deleting content:", e)


def insert_user_friend(uid, friendlist):
    """
    Insert user friend data into the friends table.

    Args:
        uid (str): Unique user ID.
        friendlist (list): List of friends to insert.
    """
    # Convert data dictionary to JSON format for cleaner storage
    data_json = json.dumps(friendlist)
    
    # Encrypt the JSON string
    encrypted_data = AesRsa.encrypt(data_json)  # This should return a dict

    # Store the encrypted data as JSON encoded string
    cursor_flist.execute("""
        INSERT INTO friends (uid, friendlist) 
        VALUES (?, ?)
    """, (uid, json.dumps(encrypted_data)))

    conn_flist.commit()  # Save the changes

def retrieve_user_friend(uid): #return list of friends, if not then empty list
    """
    Retrieve user friend data from the friends table.

    Args:
        uid (str): Unique user ID.

    Returns:
        list: List of friends or an empty list if an error occurs.
    """
    cursor_flist.execute('SELECT * FROM friends WHERE uid = ?', (uid,))
    try:
        encrypted_data = cursor_flist.fetchall()[0][1]  # Get the encrypted data
        encrypted_data = json.loads(encrypted_data)  # Decode back from JSON

        decrypted_data = AesRsa.decrypt(encrypted_data)
        return json.loads(decrypted_data)['friends']  # Return as dictionary
    except Exception as e:
        # print("Error retrieving data:", e)
        return []

def delete_friend(uid):
    """
    Delete a user from the friends table.

    Args:
        uid (str): Unique user ID.
    """
    try:
        cursor_flist.execute('DELETE FROM friends WHERE uid = ?', (uid,))
        conn_flist.commit()  # Commit the transaction to apply changes
        # print(f"Content with pid {pid} has been deleted successfully.")
    except Exception as e:
        print("Error deleting friend:", e)

def insert_user_follower(uid, friendlist):
    """
    Insert user follower data into the friendfollowing table.

    Args:
        uid (str): Unique user ID.
        friendlist (list): List of followers to insert.
    """
    # Convert data dictionary to JSON format for cleaner storage
    data_json = json.dumps(friendlist)
    
    # Encrypt the JSON string
    encrypted_data = AesRsa.encrypt(data_json)  # This should return a dict

    # Store the encrypted data as JSON encoded string
    cursor_flist.execute("""
        INSERT INTO friendfollowing (uid, friendlist) 
        VALUES (?, ?)
    """, (uid, json.dumps(encrypted_data)))

    conn_flist.commit()  # Save the changes

def retrieve_user_follower(uid): #return list of friends, if not then empty list
    """
    Retrieve user follower data from the friendfollowing table.

    Args:
        uid (str): Unique user ID.

    Returns:
        list: List of followers or an empty list if an error occurs.
    """
    cursor_flist.execute('SELECT * FROM friendfollowing WHERE uid = ?', (uid,))
    try:
        encrypted_data = cursor_flist.fetchall()[0][1]  # Get the encrypted data
        encrypted_data = json.loads(encrypted_data)  # Decode back from JSON

        decrypted_data = AesRsa.decrypt(encrypted_data)
        return json.loads(decrypted_data)['friendfollowing']  # Return as dictionary
    except Exception as e:
        # print("Error retrieving data:", e)
        return []

def delete_follower(uid):
    """
    Delete a user from the friendfollowing table.

    Args:
        uid (str): Unique user ID.
    """
    try:
        cursor_flist.execute('DELETE FROM friendfollowing WHERE uid = ?', (uid,))
        conn_flist.commit()  # Commit the transaction to apply changes
        # print(f"Content with pid {pid} has been deleted successfully.")
    except Exception as e:
        print("Error deleting friend:", e)



# def addFollower(uid, followerUID):
#     friendList = list(retrieve_user_follower(uid))
#     delete_follower(uid)
#     friendList.append(followerUID)
#     friendList = list(set(friendList))
#     insert_user_follower(uid,{'friends':friendList})

# def removeFollower(uid, followerUID):
#     friendList = list(retrieve_user_follower(uid))
#     delete_follower(uid)
#     friendList.remove(followerUID)
#     friendList = list(set(friendList))
#     insert_user_follower(uid,{'friends':friendList})



def addFriend(uid, friendUID):
    """
    Add a friend to the user's friend list and update the follower list.

    Args:
        uid (str): Unique user ID.
        friendUID (str): Unique friend ID to add.
    """
    # Add Following(friend)
    friendList = list(retrieve_user_friend(uid))
    delete_friend(uid)
    friendList.append(friendUID)
    friendList = list(set(friendList))
    insert_user_friend(uid,{'friends':friendList})
    # Add Follower
    followerListOfFriend = list(retrieve_user_follower(friendUID))
    delete_follower(friendUID)
    followerListOfFriend.append(uid)
    followerListOfFriend = list(set(followerListOfFriend))
    insert_user_follower(friendUID, {'friendfollowing':followerListOfFriend})

def removeFriend(uid, friendUID):
    """
    Remove a friend from the user's friend list and update the follower list.

    Args:
        uid (str): Unique user ID.
        friendUID (str): Unique friend ID to remove.
    """
    # Add Following(friend)
    friendList = list(retrieve_user_friend(uid))
    delete_friend(uid)
    friendList.remove(friendUID)
    friendList = list(set(friendList))
    insert_user_friend(uid,{'friends':friendList})
    # Add Follower
    followerListOfFriend = list(retrieve_user_follower(friendUID))
    delete_follower(friendUID)
    followerListOfFriend.remove(uid)
    followerListOfFriend = list(set(followerListOfFriend))
    insert_user_follower(friendUID, {'friendfollowing':followerListOfFriend})



def send_friend_request(uid, friendUID):
    """
    Send a friend request from one user to another.

    Args:
        uid (str): User ID sending the friend request.
        friendUID (str): User ID receiving the friend request.
    """
    try:
        cursor_flist.execute("""
            INSERT INTO friendRequests (uid, friendUID, status)
            VALUES (?, ?, 'pending')
        """, (uid, friendUID))
        conn_flist.commit()
    except sqlite3.IntegrityError:
        # return f"A friend request already exists between {uid} and {friendUID}."
        pass
    # return f"Friend request sent from {uid} to {friendUID}."


def cancel_friend_request(uid, friendUID):
    """
    Cancel a pending friend request.

    Args:
        uid (str): User ID who sent the friend request.
        friendUID (str): User ID to whom the request was sent.
    """
    cursor_flist.execute("""
        DELETE FROM friendRequests
        WHERE uid = ? AND friendUID = ? AND status = 'pending'
    """, (uid, friendUID))
    conn_flist.commit()
    # return f"Friend request from {uid} to {friendUID} has been cancelled."


def approve_friend_request(uid, friendUID):
    """
    Approve a pending friend request and update both friend and follower lists.

    Args:
        uid (str): User ID approving the friend request.
        friendUID (str): User ID who sent the friend request.
    """
    cursor_flist.execute("""
        UPDATE friendRequests
        SET status = 'approved'
        WHERE uid = ? AND friendUID = ? AND status = 'pending'
    """, (uid, friendUID ))
    conn_flist.commit()

    # Add to friends list of both users
    addFriend(uid, friendUID)
    # return f"Friend request from {friendUID} to {uid} has been approved."


def remove_friend(uid, friendUID):
    """
    Remove an existing friendship between two users.

    Args:
        uid (str): User ID initiating the removal.
        friendUID (str): Friend ID to remove.
    """
    # Remove from friendRequests table
    cursor_flist.execute("""
        DELETE FROM friendRequests
        WHERE (uid = ? AND friendUID = ?) OR (uid = ? AND friendUID = ?)
    """, (uid, friendUID, friendUID, uid))
    conn_flist.commit()

    # Remove from friends and followers
    removeFriend(uid, friendUID)
    # return f"Friendship between {uid} and {friendUID} has been removed."


def get_pending_requests(uid):
    """
    Retrieve all pending friend requests for a user(who have the requests).

    Args:
        uid (str): User ID for whom to fetch pending requests.

    Returns:
        list: List of user IDs who sent the pending friend requests.
    """
    cursor_flist.execute("""
        SELECT uid FROM friendRequests WHERE friendUID = ? AND status = 'pending'
    """, (uid,))
    return [row[0] for row in cursor_flist.fetchall()]

def sent_pending_requests(uid):
    """
    Retrieve all pending friend requests for a user(whom sent the requests).

    Args:
        uid (str): User ID for whom to fetch pending requests.

    Returns:
        list: List of user IDs who sent the pending friend requests.
    """
    cursor_flist.execute("""
        SELECT friendUID FROM friendRequests WHERE uid = ? AND status = 'pending'
    """, (uid,))
    return [row[0] for row in cursor_flist.fetchall()]


# Test Data
def add_test_users():
    """
    Add some test users and initial data for testing.
    """
    # Clear any existing data
    cursor_flist.execute("DELETE FROM friendRequests")
    conn_flist.commit()

    print("Existing data cleared.")

    # Add test friend requests
    send_friend_request('user1', 'user2')  # Pending request
    send_friend_request('user2', 'user3')  # Pending request
    send_friend_request('user3', 'user1')  # Pending request
    approve_friend_request('user2', 'user1')  # Approve user1's request to user2

    print("Test users added.")

# Test Functions
def test_get_pending_requests():
    """
    Test fetching pending friend requests for a user.
    """
    print("Pending friend requests for user2:", get_pending_requests('user2'))
    print("Pending friend requests for user3:", get_pending_requests('user3'))

def test_sent_pending_requests():
    """
    Test fetching pending friend requests sent by a user.
    """
    print("Pending requests sent by user1:", sent_pending_requests('user1'))
    print("Pending requests sent by user2:", sent_pending_requests('user2'))

def test_approve_friend_request():
    """
    Test approving a friend request.
    """
    print("Pending friend requests for user1 after approval:", get_pending_requests('user1'))
    print("Approving user3's request to user1.")
    approve_friend_request('user1', 'user3')
    print("Pending friend requests for user1 after approval:", get_pending_requests('user1'))

    print("Pending friend requests for user3 after approval:", get_pending_requests('user3'))
    print("Friends of user1:", retrieve_user_friend('user1'))
    print("Followers of user3:", retrieve_user_follower('user3'))

def test_cancel_friend_request():
    """
    Test canceling a friend request.
    """
    print("Canceling user2's request to user3.")
    cancel_friend_request('user2', 'user3')
    print("Pending friend requests for user3 after cancellation:", get_pending_requests('user3'))

def test_remove_friend():
    """
    Test removing a friendship.
    """
    print("Removing friendship between user1 and user2.")
    remove_friend('user2', 'user1')
    print("Friends of user1 after removal:", retrieve_user_friend('user1'))
    print("Followers of user2 after removal:", retrieve_user_follower('user2'))


# addFriend('agha','qual')
# print(retrieve_user_friend('agha'))
# print(retrieve_user_follower('qual'))

# # insert_user_friend('tash',{'friends':["a","b"]})
# addFriend('tash','c2')
# print((retrieve_user_friend('74d1927467dfb5d')))
# addFriend('tash','c')
# addFriend('tash','cc')
# addFriend('tash','ca')
# addFriend('tash','c1')
# removeFriend('tash','c2')
# print(len(retrieve_user_friend('tashs')))


# print(type(retrieve_user_friend('aghaa')))


# print(str(['a','b']))
# delete_content('ca81171ad2')
# insert_content_text('ca81171ad2','agssha')
# Step 5: Close the conn_contentection
# def close_conn_content():
#     conn_content.close()

# insert_content_text('87b98b9n8','agha')
# print(retrieve_content_text('87b98b9n8'))

# insert_profile_bio('agha','what a good day')
# print(retrieve_profile_bio('agha'))



# # Example usage:
# data_dict = {
#     "username": "agha",
#     "password": "secret_password",
#     "email": "agha@example.com",
#     "phone": "1234567890",
#     "name": "Agha",
#     "isAdmin": False,
#     "uid": "f7446c6e421d1a01"  # UID generated from username
# }

# # Insert user data
# insert_user_data("1", data_dict)
# print(retrieve_user_data('1'))
# # Retrieve user data
# retrieved_data = retrieve_user_data("87b98b9ns8a")
# print(retrieved_data)
# insert_content_text('a', 'aaaa')
# print(retrieve_content_text('a'))


