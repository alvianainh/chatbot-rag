import { useEffect } from "react";

function Login() {
  useEffect(() => {
    const form = document.getElementById("login-form");
    if (form) {
      form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
          const response = await fetch("http://localhost:8000/token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          });

          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.detail || "Login gagal");
          }

          localStorage.setItem("token", data.access_token);
          alert("Login berhasil!");
          window.location.href = "/query";
        } catch (error) {
          alert(error.message);
        }
      });
    }
  }, []);

  return (
    <div>
      <h1>Halaman Login</h1>
      <form id="login-form">
        <input type="email" id="email" placeholder="Email" required />
        <input type="password" id="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
