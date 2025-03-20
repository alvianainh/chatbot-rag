import { useEffect } from "react";

function Chatbot() {
  useEffect(() => {
    const form = document.getElementById("chatbot-form");
    if (form) {
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = document.getElementById("message").value;

        try {
          const response = await fetch("http://localhost:8000/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.detail || "Gagal mendapatkan respons chatbot");
          }

          alert(`Chatbot: ${data.response}`);
        } catch (error) {
          alert(error.message);
        }
      });
    }
  }, []);

  return (
    <div>
      <h1>Chatbot</h1>
      <form id="chatbot-form">
        <input type="text" id="message" placeholder="Ketik pesan..." required />
        <button type="submit">Kirim</button>
      </form>
    </div>
  );
}

export default Chatbot;
