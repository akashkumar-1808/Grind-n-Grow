// test connection with Flask backend
async function checkBackend() {
  try {
    const response = await fetch("http://127.0.0.1:5000/");
    const data = await response.text();
    console.log("Backend says:", data);
  } catch (err) {
    console.error("Backend not reachable:", err);
  }
}

checkBackend();
// Handle login
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      try {
        const response = await fetch("http://127.0.0.1:5000/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
          alert("Login successful!");
          window.location.href = "dashboard.html";
        } else {
          alert(data.error || "Invalid credentials!");
        }
      } catch (err) {
        alert("Server not reachable. Check backend!");
      }
    });
  }
});
