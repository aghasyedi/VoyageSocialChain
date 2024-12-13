from datetime import datetime
import re, Blockchain
from flask import Flask, render_template, redirect,  url_for, jsonify, send_from_directory, session, request
import ImgEnc as ied
from werkzeug.utils import secure_filename
print("_________RELOADING app.py________")

# Set the SECRET_KEY for the Flask application.
# This key is used for securely signing session cookies and
# protecting against CSRF attacks. Ensure that this key is 
# kept secret and use a strong, randomly generated value 
# for production environments. Consider loading it from an 
# environment variable for enhanced security.
app = Flask(__name__)
app.config["SECRET_KEY"] = "xtft7jAc84DRBJXoirnqzSQ5voB8DIL6"


# this code not working
# @app.route('/static/<path:filename>')
# def static_files(filename):
#     print(filename,'ahha')
#     current_user = session.get('current_user')
#     if not current_user:
#         return redirect(url_for('login'))
    
#     # Path to the static folder (including subdirectories)
#     static_folder = os.path.join(app.root_path, 'static')
#     print(send_from_directory(static_folder,filename))
#     # Serve the requested file
#     return send_from_directory(static_folder, filename)



@app.route('/')
def home():
    """
    Function to redirect the user to the feed page by default.
    
    This function handles requests made to the base URL and redirects them to the feed page.
    
    Example usage:
    https://127.0.0.1:8080/
    
    Returns:
        Redirect: A redirect to the feed page.
    """
    return redirect(url_for("feed"))

@app.errorhandler(404)
def page_not_found(e):
    """
     Custom 404 error handler for non-existent pages.
    
    This function catches requests for URLs that don't exist on the server. 
    Depending on whether the user is logged in or not, it redirects them to the 
    appropriate page (feed for logged-in users or login page otherwise).
    
    Example usage:
    https://127.0.0.1:8080/{invalid_path}
    
    Args:
        e (Exception): The exception raised for a 404 error.
    
    Returns:
        Redirect: A redirect to either the feed or login page.
    """
    current_user = session.get('current_user')
    if current_user:
        return redirect(url_for("feed"))
    return redirect(url_for("login"))

@app.route('/contact')
def contact():
    """
    Function to render the contact page.
    
    This page provides information for users to contact the server administrator.
    
    Example usage:
    https://127.0.0.1:8080/contact
    
    Returns:
        HTML: The contact page template.
    """
    return render_template("contact.html")

@app.route('/admin')
def admin():
    """
    Admin access function for the dashboard.
    
    This function ensures that only users with admin privileges can access the 
    admin dashboard. Non-admin users are redirected to the feed page with an error message.
    
    Example usage:
    https://127.0.0.1:8080/admin
    
    Returns:
        HTML: The dashboard page if the user is admin, or an error message otherwise.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error="Login with admin account to get access")
    if current_user['Admin'] is True:
        return render_template("dashboard.html")
    return render_template('feed.html',currentuser=current_user, feed_data=Blockchain.get_posts(), error="Your account is not an ADMIN.") 
    
@app.route('/view_users')
def view_users():
    """
    Function for admin users to view all users.
    
    This function allows admin users to retrieve and view all registered users in the 
    Social app. The data includes all user information except None values.
    
    Example usage:
    https://127.0.0.1:8080/view_users
    
    Returns:
        HTML: The view users page with a list of all users.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error="Login with admin account to get access")
        # return redirect(url_for('login', error='Login with admin account to get access'))

    if current_user['Admin'] is True:
        try:
            users = Blockchain.get_user_data()
        except:
            return "Please Refresh the Page"
        latest_users = {}
        for user in reversed(users):
            user_id = user['username']
            user_date = datetime.strptime(user['date'], '%Y-%m-%d %H:%M:%S.%f')
            
            # If the user_id is not in latest_users or the date is more recent, update the entry
            if user_id not in latest_users or user_date > datetime.strptime(latest_users[user_id]['date'], '%Y-%m-%d %H:%M:%S.%f'):
                latest_users[user_id] = user

        # Convert the dictionary back to a list
        unique_users = list(latest_users.values())
        # print(users, unique_users)
        users = unique_users
        return render_template("view_users.html", users=users)
    return render_template('feed.html',currentuser=current_user, feed_data=Blockchain.get_posts(), error="Your account is not an ADMIN.") 


@app.route('/view_posts')
def view_posts():
    """
    Function for admin users to view all posts.
    
    This function allows admin users to retrieve and view all posts made in the Social app.
    
    Example usage:
    https://127.0.0.1:8080/view_posts
    
    Returns:
        HTML: The view posts page with a list of all posts.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error="Login with admin account to get access")
    if current_user['Admin'] is True:
        posts = Blockchain.get_posts()
        return render_template("view_posts.html", posts=posts)
    return render_template('feed.html',currentuser=current_user, feed_data=Blockchain.get_posts(), error="Your account is not an ADMIN.") 

@app.route('/about')
def about():
    """
    Function to render the about page.
    
    This function loads and displays the about page for the Social app.
    
    Example usage:
    https://127.0.0.1:8080/about
    
    Returns:
        HTML: The about page template.
    """
    return render_template("about.html")

user_data_cache = Blockchain.get_user_data()


@app.route('/search', methods=['GET'])
def search():
    """
    Function to search for users in the Social app.

    The function handles GET requests at the /search endpoint, 
    processes the search query, and returns matching users from the user data cache. 
    It filters out the 'admin' user and current user and includes only those users
    whose usernames match the search query.

    The search results return a simplified JSON response containing 
    only the 'username' and 'name' fields of the matching users.

    Example usage:
    https://127.0.0.1:8080/search?q=<query>

    Args:
        q (str): The search query provided as a URL parameter.
    
    Returns:
        JSON: A list of filtered users, each containing 'username' and 'name'.
    """
    current_user = session.get('current_user')
    query = request.args.get('q', '').lower()

    filtered_users = [
        {'username': user['username'], 'name': user['name']} 
        for user in user_data_cache 
        if user['username'] != 'admin' and user['username'] != current_user['username'] and query in user['username'].lower()
    ]

    return jsonify(filtered_users)  # Return filtered users as JSON


@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Function to verify the user login request comparing
    it to the latest block of user login.
    If user is already logged in the forward the request to "feed()"
    function.
    Otherwise, first check for username in blocks, then password,
    then mark that the user is logged in, and a session is
    created.
    The rest of the application uses this session to track
    the user logged in. The "logout()" function will clear this
    session.

    Example usage:
    https://127.0.0.1:8080/login

    Returns:
        Rendered HTML page: Redirects to feed if logged in, otherwise shows the login page.
    """
    global user_data_cache
    user_data_cache= Blockchain.get_user_data()
    current_user = session.get('current_user')
    if current_user:
        return redirect(url_for("feed"))
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        print("'",username,"' tried to login - ")
        if not username or not password:
            return render_template('login.html', error="Please fill out all fields!")

        users = Blockchain.get_user_data()
        
        #reversed make this like, the latest block with the user data and username will be selected
        #the unchanged old block would be ignore but it will be in the block
        for user in reversed(users):
            if user["username"] == username:
                if user["password"] == password:
                    session['current_user'] = user  #assigning user to session #this is ony section for this
                    return redirect(url_for('feed'))
                return render_template('login.html', error="Invalid username or password!")
        return render_template('login.html', error="Invalid username or password!")

    return render_template("login.html")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Function to add a new user to the blockchain.

    The function verifies the following inputs:
        - Username: must be alphanumeric, at least 3 characters long.
        - Password: must be at least 6 characters long.
        - Phone: must be a numeric string of fixed length 10.
        - Email and Name: added to the block without verification.

    Example usage:
    https://127.0.0.1:8080/signup

    Returns:
        Rendered HTML page: Redirects to login with a success message upon registration.
    """
    if request.method == 'POST':
        username = request.form.get("susername")
        password = request.form.get("spassword")
        email = request.form.get("semail")
        phone = request.form.get("sphone")
        name = request.form.get("sname")

        if not username or not password or not email or not phone or not name:
            return render_template('login.html', error="Please fill out all fields!")

        if not re.match(r"^[a-zA-Z0-9]{3,}$", username):
            """
            Username must be alphanumeric, no dots(.) or underscore(_)
            are supported. Username must be atleast 3 character, no
            upper limit.
            """
            return render_template('login.html', error="Username must be alphanumeric and at least 3 characters long.")

        users = Blockchain.get_user_data()
        if any(user['username'] == username for user in users):
            return render_template('login.html', error=f"'{username}' is already taken. Please choose another one.")

        if len(password) < 6:
            return render_template('login.html', error="Password must be at least 6 characters long.")

        if not phone.isdigit() or len(phone) != 10:
            return render_template('login.html', error="Phone number must be a 10-digit number.")
        
        # Adds the user, and as a friend as well as the followers
        Blockchain.add_new_user(username, password, email, phone, name)
        # Blockchain.addFriend(Blockchain.get_userId(username),Blockchain.get_userId(username))
        return render_template('login.html', signupped=f"Registered for {username}!")

    return render_template("login.html")

@app.route('/user/<username>')
def user_profile(username):
    """
    Function to display the user profile.

    This function verifies the user's request to access their profile
    and returns a webpage containing user information and posts.

    Example usage:
    https://127.0.0.1:8080/user/{username}

    Args:
        username (str): The username of the profile to be displayed.
    
    Returns:
        Rendered HTML page: Displays the user profile or an error message if not found.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error=f"Please login to see User Profile.")
    
    """ Implement here for a friend"""
    user_data = Blockchain.get_user_data()

    friendList = Blockchain.getFriendList(Blockchain.get_userId(username))
    followingList = Blockchain.getFollowingList(Blockchain.get_userId(username))

    recievedRequests = Blockchain.get_pending_requests(current_user['user_id'])
    sentRequests = Blockchain.sent_pending_requests(current_user['user_id'])


    toRemove = Blockchain.get_userId(username)

    friendList = [i for i in friendList if i != toRemove]
    followingList = [i for i in followingList if i != toRemove]

    # print(friendList.remove(list(toRemove)))

    #add user profile here
    friendListName = [[Blockchain.get_userName(uid),Blockchain.get_user_info(Blockchain.get_userName(uid))['name'],uid] for uid in friendList] 
    #add user profile here
    followingListName = [[Blockchain.get_userName(fid),Blockchain.get_user_info(Blockchain.get_userName(fid))['name'],fid] for fid in followingList]

    # print(friendListName,([username,Blockchain.get_user_info(Blockchain.get_userName(Blockchain.get_userId(username)))['name']]))
    flag = False
    # print(friendList)
    if Blockchain.get_userId(username) in  Blockchain.getFriendList(Blockchain.get_userId(current_user['username'])):
        flag = True
    # print(flag)
    
    # print(flag)
    if username == current_user['username']:
        flag = True
    for user in reversed(user_data):
        if username == str(user['username']):
            current_user['no_of_posts'] = Blockchain.get_user_number_of_post(current_user['username'])
            return render_template('profile.html', currentuser = current_user, user = user, user_data = Blockchain.get_user_posts(user['username']),
                                                friend = flag,friendListName=friendListName, followingListName=followingListName,recievedRequests=recievedRequests,sentRequests=sentRequests,
                                                userList = Blockchain.get_user_list_for_username(current_user['username']))
    return render_template('profile-dont-exist.html', currentuser = current_user, username = username)
    # return render_template("feed.html", currentuser=current_user, feed_data=Blockchain.get_posts(), error=f"[{username}] doesn't exist.")


@app.route('/post/<post_id>')
def post_info(post_id):
    """
    Function to get detailed information about a specific post.

    This function validates the post ID and returns the post details
    in a webpage.

    Example usage:
    https://127.0.0.1:8080/post/{post_id}

    Args:
        post_id (str): The ID of the post to be displayed.

    Returns:
        Rendered HTML page: Displays the post details or an error message if not found.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error=f"Please login to see User Profile.")
    postInfo = Blockchain.get_post_info(post_id)
    if postInfo[1] is True:
        return render_template('post.html', currentuser = current_user, post= postInfo[0])
    else:
        return render_template('post-dont-exist.html', currentuser = current_user, post_id = post_id)


@app.route('/edit-post/<post_id>')
def edit_post(post_id):
    """
    Function to edit a user's post.

    This function verifies if the post belongs to the user requesting the edit,
    allowing only the "content" to be changed.

    Example usage:
    https://127.0.0.1:8080/edit-post/{post_id}

    Args:
        post_id (str): The ID of the post to be edited.

    Returns:
        Rendered HTML page: Displays the edit post form or an error message if unauthorized.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error=f"Please login to see Edit Post.")
    postInfo = Blockchain.get_post_info(post_id)
    if current_user['username'] != postInfo[0]['username']:
        return render_template('edit-post.html', currentuser =current_user,
                               error=f"Please LogIN with '{Blockchain.get_post_info(post_id)[0]['username']}'.")
    if postInfo[1]:
        post =  postInfo[0]
        return render_template('edit-post.html', currentuser =current_user, post=post)
    else:
        return render_template('edit-post.html', currentuser =current_user, error="Post ID not Found.")

    
@app.route('/editpost', methods = ["POST"])
def editpost():
    """
    Function to handle the post edit submission.

    This function verifies if the request belongs to the user who
    posted the content, and updates the post if authorized.

    Example usage:
    https://127.0.0.1:8080/editpost

    Returns:
        Rendered HTML page: Displays the updated post or an error message if unauthorized.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error=f"Please login to see Edit Post.")
    if request.method == "POST" and request.form.get("username")==current_user['username']:

        # username =  str(request.form.get("username"))
        """post_id, username, date,content"""
        post_id_html =  str(request.form.get("postid"))
        postInfo = Blockchain.get_post_info(post_id_html)
        if postInfo[1]:
            # post =  postInfo[0]
            # post_user_name = post['username']
            # date =  str(request.form.get("date"))
            content =  str(request.form.get("content"))
            Blockchain.update_post(post_id_html, content)
            # pbio =  str(request.form.get("pbio"))
            # session['current_user'] = Blockchain.add_old_user(current_user,password, phone, name)
            current_user = session.get('current_user')

            # print(Blockchain.get_post_info('post_id'))
            return render_template('edit-post.html', currentuser =current_user, post=Blockchain.get_post_info(post_id_html)[0],
                                   feedback = "Your data have been changed.")
        else:
            return render_template('edit-post.html', currentuser =current_user, error="Post ID not Found.")
    return render_template('edit-post.html', currentuser =current_user,
                           error=f"Please LogIN with '{Blockchain.get_post_info(request.form.get('postid'))[0]['username']}'.")
    # post_info = Blockchain.get_post_info(request.form.get("postid"))[0]['username']
    # usernamex = post_info
    # error_message = f"Please LogIN with '{usernamex}'."
    # return render_template('edit-post.html', currentuser=current_user, error=error_message)



@app.route('/edit-profile')
def edit_profile():
    """
    Function to render the edit profile page.

    This function checks for the user session; if the user is logged in, 
    it forwards the request to _edit-profile.html_. If the user is not logged in, 
    it redirects to _login.html_.

    Example usage:
    https://127.0.0.1:8080/edit-profile

    Returns:
        Rendered HTML page: Displays the edit profile page if logged in, 
        otherwise redirects to the login page.
    """
    current_user = session.get('current_user')
    if not current_user:
        return render_template('login.html', error=f"Please login to see Edit User Profile.")
    return render_template('edit-profile.html', currentuser =current_user)
    

@app.route('/editprofile',methods = ["POST"])
def editprofile():
    """
    Function to handle the editing of the user's profile.

    This function allows the user to update their phone, name, and password 
    if logged in. Any changes will result in a new block being added to the blockchain.

    Example usage:
    https://127.0.0.1:8080/editprofile

    Returns:
        Rendered HTML page: Displays the edit profile page with feedback if changes are made, 
        or redirects to the login page if not logged in.
    """
    if request.method == "POST" and request.form.get("username")==session.get('current_user')['username']:
        current_user = session.get('current_user')
        # username =  str(request.form.get("username"))
        if str(request.form.get("password")):
            password =  str(request.form.get("password"))
        else:
            password = current_user['password']

        # email =  str(request.form.get("email"))
        phone =  str(request.form.get("phone"))
        name =  str(request.form.get("name"))
        # pbio =  str(request.form.get("pbio"))
        session['current_user'] = Blockchain.add_old_user(current_user,password, phone, name)
        current_user = session.get('current_user')
        return render_template("edit-profile.html", feedback='Your data have been changed.', currentuser=current_user )
    return render_template('login.html', error="Please login to make any changes.")


@app.route('/send-friend-request', methods=["POST"])
def sendFriend():
    """
    Function to add a friend to the user's following list.

    This function handles the addition of a follower and following relationship
    for the user and the specified friend.

    Example usage:
    https://127.0.0.1:8080/send-friend-request

    Returns:
        Redirects to the user profile page of the friend.
    """
    current_user = session.get('current_user')
    if not current_user:
        return redirect(url_for('login'))
    
    friendUID = request.form.get("friendUID")
    username = request.form.get("username")
    # print(current_user['user_id'], friendUID,'aaaaaaa')
    Blockchain.send_friend_request(current_user['user_id'], friendUID)

    if request.form.get("area") == 'feed':
        return redirect(url_for('feed'))
    return redirect(url_for('user_profile', username=username))

@app.route('/cancel-friend-request', methods=["POST"])
def cancelFriend():
    """
    Function to add a friend to the user's following list.

    This function handles the addition of a follower and following relationship
    for the user and the specified friend.

    Example usage:
    https://127.0.0.1:8080/cancel-friend-request

    Returns:
        Redirects to the user profile page of the friend.
    """
    current_user = session.get('current_user')
    if not current_user:
        return redirect(url_for('login'))
    
    friendUID = request.form.get("friendUID")
    username = request.form.get("username")
    # print(current_user['user_id'], friendUID,'aaaaaaa')
    Blockchain.cancel_friend_request(friendUID,current_user['user_id'])

    if request.form.get("area") == 'feed':
        return redirect(url_for('feed'))
    return redirect(url_for('user_profile', username=username))

@app.route('/approve-friend-request', methods=["POST"])
def approveFriend():
    """
    Function to remove a friend from the user's following list.

    This function handles the removal of a follower and following relationship
    for the user and the specified friend.

    Example usage:
    https://127.0.0.1:8080/approve-friend-request

    Returns:
        Redirects to the user profile page of the friend.
    """
    current_user = session.get('current_user')
    if not current_user:
        return redirect(url_for('login'))
    friendUID = request.form.get("friendUID")
    username = request.form.get("username")
    Blockchain.approve_friend_request(current_user['user_id'], friendUID)
    if request.form.get("area") == 'feed':
        return redirect(url_for('feed'))
    return redirect(url_for('user_profile', username=username))


@app.route('/remove-friend-request', methods=["POST"])
def removeFriend():
    """
    Function to remove a friend from the user's following list.

    This function handles the removal of a follower and following relationship
    for the user and the specified friend.

    Example usage:
    https://127.0.0.1:8080/remove-friend-request

    Returns:
        Redirects to the user profile page of the friend.
    """
    current_user = session.get('current_user')
    if not current_user:
        return redirect(url_for('login'))
    friendUID = request.form.get("friendUID")
    username = request.form.get("username")
    Blockchain.remove_friend(current_user['user_id'], friendUID)
    if request.form.get("area") == 'feed':
        return redirect(url_for('feed'))
    return redirect(url_for('user_profile', username=username))


@app.route('/feed/upload', methods=["POST"])
def upload_files(time):
    """
    Function to upload a file (usually an image) to the database.

    This function is called when uploading a post with an image. It stores
    the file in the database and returns the stored filename.

    Example usage:
    https://127.0.0.1:8080/feed/upload

    Args:
        time (str): The timestamp of the upload.

    Returns:
        str: The filename of the uploaded file.
    """
    current_user = session.get('current_user')
    files = request.files.getlist("file")
    if not current_user:
        return redirect(url_for('login'))
    if files:
        for file in files:
            if file.filename != '':
                fileend = secure_filename(file.filename)
                filename = str(time)+current_user['username']+fileend[-4:]
                file.save(f'static/uploaded_files/{filename}')
                filename = ied.encrypt_image(filename)
                return filename
        feed_data = Blockchain.get_posts()
        return render_template("feed.html", currentuser=current_user, feed_data=feed_data)
    return render_template("feed.html", currentuser=current_user, feed_data=Blockchain.get_posts(),
                           error='Length of the content should be less than 100 letters.')

@app.route('/feed', methods=["GET", "POST"])
def feed():
    """
    Function to display the user feed page.

    This function shows the first page after login, including the navigation bar, 
    side profile panel, and post feed. Only posts from followed accounts are displayed.

    Example usage:
    https://127.0.0.1:8080/feed

    Returns:
        Rendered HTML page: Displays the user feed with posts from followed accounts.
    """
    current_user = session.get('current_user')
    if not current_user:
        return redirect(url_for('login'))
    global user_data_cache
    
    users = Blockchain.get_user_data()
    user_data_cache= users
    user_found = False

    friendList = Blockchain.getFriendList(current_user['user_id'])
    recievedRequests = Blockchain.get_pending_requests(current_user['user_id'])
    sentRequests = Blockchain.sent_pending_requests(current_user['user_id'])

    for user in users:
        if user["username"] == current_user['username']:
            user_found = True
            break

    if not user_found:
        logout()
        return render_template('login.html', error=f"The username '{current_user['username']}' doesn't exist, create an account.")

    if request.method == "POST" and request.form.get("post_content"):
        content = request.form.get("post_content")

        if len(content) > 100:
            return render_template("feed.html", currentuser=current_user, feed_data=Blockchain.get_posts(),
                                   error='Length of the content should be less than 100 letters.')
        
        time = datetime.now().strftime("%d%m%y%H%M%S")
        filename = upload_files(time)
        
        Blockchain.add_new_post(current_user['username'], content, filename)
        return redirect(url_for('feed'))

    feed_data = Blockchain.get_posts()
    postList = []

    friendList.append(Blockchain.get_userId(current_user['username'])) # to add self user to participate in feed content
    for post in feed_data:
        userID = Blockchain.get_userId(post['username'])
        if userID in friendList:
            postList.append(post)
    feed_data = postList
    current_user['no_of_posts'] = Blockchain.get_user_number_of_post(current_user['username'])
    userList = Blockchain.get_user_list_for_username(current_user['username'])
    print(postList)
    return render_template("feed.html", currentuser=current_user, feed_data=feed_data, userList = userList,recievedRequests=recievedRequests, sentRequests=sentRequests)



@app.route('/static/database/<db_name>.db')
def protected_db(db_name):
    """
    Function to protect the database from unauthorized access.

    This function prevents direct access to the database files, redirecting
    to the login page instead.

    Example usage:
    https://127.0.0.1:8080/static/database/{any db name}.db

    Returns:
        Redirect: Redirects to the login page.
    """
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """
    Function to clear the user session and redirect to the login page.

    Example usage:
    https://127.0.0.1:8080/logout

    Returns:
        Redirect: Redirects to the login page after logging out.
    """
    print(session.get('current_user')['username'],"  LOGOFF")
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    """
    Main section to run the application.

    This section starts the Flask application on the specified host and port.
    """

    app.run(host='0.0.0.0', port=2910, debug=True)
    # app.run(host='127.0.0.1', port=8080, debug=True)
