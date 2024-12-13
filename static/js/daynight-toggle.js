document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("night-button");
  const commonStylesheet = document.getElementById("common-stylesheet");
  const themeStylesheet = document.getElementById("theme-stylesheet");

  // Get the current path
  const currentPath = window.location.pathname;

  // Check for saved mode in localStorage and set theme
  const savedMode = localStorage.getItem("mode");

  // Function to set theme styles
  function setTheme(mode) {
    if (mode === "night") {
      commonStylesheet.href = "/static/css/night-mode-common.css"; // Load night mode common styles
      if (
        currentPath.includes("/feed") ||
        currentPath.match(/^\/edit-post\/[^\/]+$/) ||
        currentPath === "/edit-profile"
      ) {
        themeStylesheet.href = "/static/css/feed.css"; // Night mode for feed
      } else if (
        currentPath.includes("/profile") ||
        currentPath.match(/^\/user\/[^\/]+$/) ||
        currentPath.match(/^\/post\/[^\/]+$/)
      ) {
        themeStylesheet.href = "/static/css/profile.css"; // Night mode for profile/user
      } else {
        themeStylesheet.href = "/static/css/login.css"; // Fallback for other pages
      }
      toggleButton.checked = true; // Check the checkbox for night mode
    } else {
      commonStylesheet.href = "/static/css/day-mode-common.css"; // Load day mode common styles
      if (
        currentPath.includes("/feed") ||
        currentPath.match(/^\/edit-post\/[^\/]+$/) ||
        currentPath === "/edit-profile"
      ) {
        themeStylesheet.href = "/static/css/nfeed.css"; // Day mode for feed
      } else if (
        currentPath.includes("/profile") ||
        currentPath.match(/^\/user\/[^\/]+$/) ||
        currentPath.match(/^\/post\/[^\/]+$/)
      ) {
        themeStylesheet.href = "/static/css/nprofile.css"; // Day mode for profile/user
      } else {
        themeStylesheet.href = "/static/css/nlogin.css"; // Fallback for other pages
      }
      toggleButton.checked = false; // Uncheck the checkbox for day mode
    }
  }

  // Set theme based on saved mode or default to day mode
  setTheme(savedMode || "day");

  // Add event listener for button click
  toggleButton.addEventListener("click", function () {
    const newMode = toggleButton.checked ? "night" : "day";
    localStorage.setItem("mode", newMode); // Save mode in localStorage
    setTheme(newMode); // Update the theme
  });
});
