| Link                        | Description                                                                                                 |
|-----------------------------|-------------------------------------------------------------------------------------------------------------|
| `/`                          | Redirects to the user feed if logged in; otherwise, redirects to the login page.                            |
| `/contact`                   | Renders the "Contact" page.                                                                                 |
| `/admin`                     | Renders the admin dashboard if the user is an admin. Otherwise, redirects to login or user feed.            |
| `/view_users`                | Admin-only page. Displays all users if logged in as admin. Redirects to login if not authenticated.          |
| `/view_posts`                | Admin-only page. Displays all posts if logged in as admin. Redirects to login if not authenticated.          |
| `/about`                     | Renders the "About" page.                                                                                   |
| `/search`                    | Searches and filters users (excluding admins) based on the query and returns results as JSON.               |
| `/login`                     | Handles login page rendering and POST requests for user authentication.                                     |
| `/signup`                    | Handles user registration, including validation and account creation.                                       |
| `/user/<username>`           | Displays the profile page of the specified user. Redirects to login if not authenticated.                   |
| `/edit-profile`              | Renders the profile editing page for the current user.                                                      |
| `/editprofile`               | Handles profile updates for the current user and validates the input.                                        |
| `/feed/upload`               | Handles file uploads and encryption for the user feed. Only available for authenticated users.              |
| `/feed`                      | Displays the main feed, allowing users to create new posts and see other posts if logged in.                |
