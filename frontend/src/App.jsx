// frontend/src/App.jsx
import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Feel free to ask questions! :)",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userText }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/invert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userText }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.result ?? "…" },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I couldn’t reach the inversion backend. Please check the FastAPI server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-shell">
      <header>
        <div>
          <p className="app-name">OppositeGPT</p>
          <span className="app-subtitle">Serious answers only</span>
        </div>
        <button
          className="reset-btn"
          onClick={() =>
            setMessages([
              {
                role: "assistant",
                content:
                  "Hi, I’m OppositeGPT. Feed me a thought and I’ll flip it on its head.",
              },
            ])
          }
        >
          Clear chat
        </button>
      </header>

      <section className="chat-thread" ref={chatRef}>
        {messages.map((msg, idx) => (
          <article key={idx} className={`bubble ${msg.role}`}>
            <div className="avatar">{msg.role === "user" ? "You" : "OG"}</div>
            <p>{msg.content}</p>
          </article>
        ))}
        {loading && (
          <article className="bubble assistant typing">
            <div className="avatar">OG</div>
            <div className="dots">
              <span />
              <span />
              <span />
            </div>
          </article>
        )}
      </section>

      <form className="composer" onSubmit={sendMessage}>
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Send a message..."
        />
        <button type="submit" disabled={!input.trim() || loading}>
          Send
        </button>
      </form>
    </div>
  );
}