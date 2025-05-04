const apiUrl = "http://127.0.0.1:5000";

async function registerUser(username, password) {
    window.location.href = "/register";
}

async function loginUser(username, password) {
    window.location.href = "/login";
}

async function logoutUser() {
    const response = await fetch(`${apiUrl}/logout`, {method: "POST"});
        sessionStorage.removeItem("user");
        window.location.href = "/login";
}

async function loadData() {
    const response = await fetch(`${apiUrl}/get_data`, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    });

    if (!response.ok) {
        alert("Please log in to view data");
        return;
    }

}

async function applyFilters() {
    const amountQuery = document.getElementById("Fprice").value;
    const nameQuery = document.getElementById("Fname").value;
    const date = document.getElementById("Fdate").value;
    const reportType = document.getElementById("Ftype").value;

    let url = "/?";
    if (amountQuery) {
        url += `Fprice=${amountQuery}&`;
    }
    if (nameQuery) {
        url += `Fname=${nameQuery}&`;
    }
    if (date) {
        url += `Fdate=${date}&`;
    }
    if (reportType && reportType !== "All") {
        url += `Ftype=${reportType}&`;
    }

    if (url.endsWith("&")) {
        url = url.slice(0, -1);
    }

    window.location.href = url;
}


document.addEventListener("DOMContentLoaded", () => {

    if (sessionStorage.getItem("user")) {
        loadData();
    }

    // Add event listeners to close buttons in alerts
    document.querySelectorAll(".alert .close").forEach((button) => {
        button.addEventListener("click", (event) => {
            const alert = event.target.closest(".alert");
            if (alert) {
                alert.style.display = "none"; // Hide the alert
            }
        });
    });

    // Navigation links
    const registerLink = document.getElementById("toggle-linkr");
    if (registerLink) {
        registerLink.addEventListener("click", (event) => {
            event.preventDefault();
            window.location.href = "register";
        });
    }

    const loginLink = document.getElementById("toggle-linkl");
    if (loginLink) {
        loginLink.addEventListener("click", (event) => {
            event.preventDefault();
            window.location.href = "login";
        });
    }

    // Handle registration form submission
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            
            registerForm.submit();
        });
    }

    // Handle login form submission
    const loginForm = document.getElementById("auth-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            loginForm.submit();
        });
    }

});