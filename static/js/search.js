document.getElementById("search-input").addEventListener("input", function () {
  const query = this.value.trim(); // Trim whitespace
  console.log(`Search Query: "${query}" (Length: ${query.length})`); // Debugging line

  // Get the elements for dropdown and results container
  const resultsContainer = document.getElementById("search-results");
  const dropdown = document.getElementById("search-dropdown");

  // Clear previous results
  resultsContainer.innerHTML = "";

  // Check if the query is empty
  if (query === "") {
    dropdown.style.display = "none"; // Hide dropdown if input is empty
    return; // Exit the function
  }

  // Fetch search results from the server
  fetch(`/search?q=${encodeURIComponent(query)}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((users) => {
      let seenUsernames = new Set();
      let uniqueUsers = [];

      // Iterate over users and filter out duplicates
      for (let i = users.length - 1; i >= 0; i--) {
        let user = users[i];
        if (!seenUsernames.has(user.username)) {
          seenUsernames.add(user.username);
          uniqueUsers.push(user);
        }
      } // Debugging line to see the fetched results
      // uniqueUsers.reverse();
      uniqueUsers.sort((a, b) => {
        if (a.name < b.name) return -1; // a comes before b
        if (a.name > b.name) return 1; // a comes after b
        return 0; // a and b are equal
      });
      console.log(encodeURIComponent(query));
      // for (let user of uniqueUsers.reverse()) {
      //     console.log(`Name: ${user.username}, Name: ${user.name}`);
      // }
      users = uniqueUsers;
      users.forEach((user) => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `
                  <font style='font-size:12px;'>@${user.username}</font>
                  <a href="/user/${user.username}" style="display: flex; align-items: center;">
                      <img src="https://gdm-catalog-fmapi-prod.imgix.net/ProductScreenshot/74919c82-78e5-4f1e-8164-9937cbe5deb6.png"
                          style="width: 30px; height: 30px; border: 2px solid yellow; border-radius: 50%; margin-right: 5px;">
                      ${user.name}
                  </a>
                  `;
        resultsContainer.appendChild(listItem);
      });

      // Show or hide dropdown based on results
      dropdown.style.display = users.length > 0 ? "block" : "none";
    })
    .catch((error) => console.error("Error fetching search results:", error));
});

// Handle keyboard navigation
let selectedIndex = -1; // To track the currently selected item

document
  .getElementById("search-input")
  .addEventListener("keydown", function (event) {
    const results = document.querySelectorAll("#search-results li");

    if (event.key === "ArrowDown") {
      selectedIndex = Math.min(selectedIndex + 1, results.length - 1); // Move down
    } else if (event.key === "ArrowUp") {
      selectedIndex = Math.max(selectedIndex - 1, -1); // Move up
    } else if (event.key === "Enter") {
      if (selectedIndex >= 0) {
        // Click the selected item
        results[selectedIndex].querySelector("a").click();
      } else if (results.length > 0) {
        // Click the first item if no item is selected
        results[0].querySelector("a").click();
      }
    }

    // Update the highlighted state
    results.forEach((item, index) => {
      item.style.backgroundColor = index === selectedIndex ? "#c8e6c9" : ""; // Highlight selected item
    });
  });

// Hide dropdown when clicking outside
document.addEventListener("click", function (event) {
  const dropdown = document.getElementById("search-dropdown");
  if (!document.getElementById("search-input").contains(event.target)) {
    dropdown.style.display = "none";
  }
});
