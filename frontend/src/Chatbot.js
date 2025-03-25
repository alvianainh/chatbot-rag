import { useState } from "react";
import "./Chatbot.css"; 

function Chatbot() {
  const [message, setMessage] = useState("");
  const [chats, setChats] = useState([]); 
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    const newChat = { sender: "user", text: message };
    setChats((prevChats) => [...prevChats, newChat]);
    setMessage(""); 

    try {
      const token = localStorage.getItem("token");
      if (!token) throw new Error("Token not found. Please login.");

      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: newChat.text }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to get response.");

      const botReply = { sender: "bot", text: data.answer };
      setChats((prevChats) => [...prevChats, botReply]);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <h1>Chatbot</h1>
      <div className="chatbox">
        {chats.map((chat, index) => (
          <div key={index} className={`chat-message ${chat.sender}`}>
            {chat.text}
          </div>
        ))}
      </div>
      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default Chatbot;
