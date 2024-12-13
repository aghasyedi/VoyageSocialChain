// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voyage {
    
    struct User {
        string username;
        string passwordHash; // Store password hash
        bool isAdmin;
    }

    struct Post {
        string username;
        string content;
        uint timestamp;
    }

    mapping(address => User) public users;
    Post[] public posts;

    event UserAdded(string username, bool isAdmin);
    event PostCreated(string username, string content, uint timestamp);

    modifier onlyExistingUser() {
        require(bytes(users[msg.sender].username).length != 0, "User does not exist");
        _;
    }

    modifier onlyAdmin() {
        require(users[msg.sender].isAdmin, "Only admin can perform this action");
        _;
    }

    function addUser(string memory username, string memory password) public {
        require(bytes(users[msg.sender].username).length == 0, "User already exists");
        string memory hashedPassword = password;
        users[msg.sender] = User(username, hashedPassword, false); // Default to non-admin
        
        emit UserAdded(username, false);
    }

    function addPost(string memory content) public onlyExistingUser {
        Post memory newPost = Post(users[msg.sender].username, content, block.timestamp);
        posts.push(newPost);
        emit PostCreated(users[msg.sender].username, content, block.timestamp);
    }

    function getPosts() public view returns (Post[] memory) {
        return posts;
    }

    function getUserData() public view returns (User memory) {
        return users[msg.sender];
    }
    

    // Admin function example
    function grantAdmin(address user) public onlyAdmin {
        users[user].isAdmin = true;
    }
}
