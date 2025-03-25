import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Register from "./Register";
import Login from "./Login";
import Chatbot from "./Chatbot";

function App() {
  console.log("App.js dirender!");
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Register />} />
        <Route path="/token" element={<Login />} />
        <Route path="/query" element={<Chatbot />} />
      </Routes>
    </Router>
  );
}

export default App;
