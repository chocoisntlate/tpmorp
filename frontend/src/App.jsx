import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const PROMPTER_WORD = "prompter";
const RETPMORP_WORD = "retpmorp";
const RETPMORP_LETTERS = RETPMORP_WORD.split("").map((letter, index) => ({
  from: PROMPTER_WORD[index] ?? "",
  to: letter,
}));

function RetpmorpWord({
  as: Element = "span",
  className = "",
  label = RETPMORP_WORD,
  ...restProps
}) {
  const classNames = ["retpmorp-word", className].filter(Boolean).join(" ");

  return (
    <Element className={classNames} {...restProps}>
      <span className="sr-only">{label}</span>
      {RETPMORP_LETTERS.map(({ from, to }, index) => (
        <span
          aria-hidden="true"
          key={`${to}-${index}`}
          className="retpmorp-letter"
          data-from={from}
          data-to={to}
          style={{ "--retpmorp-delay": `${index * 80}ms` }}
        >
          {to}
        </span>
      ))}
    </Element>
  );
}

export default function App() {
  const buildIntroMessage = () => ({
    role: "assistant",
    content: (
      <>
        Hi, I’m <RetpmorpWord />. Feed me a thought and I’ll flip it on its head.
      </>
    ),
  });

  const [messages, setMessages] = useState(() => [buildIntroMessage()]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
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
          <p className="app-name">
            <RetpmorpWord className="retpmorp-word--title" />
          </p>
          <span className="app-subtitle">
            Serious answers only · Professional Ragebaiter
          </span>
        </div>
        <button className="reset-btn" onClick={() => setMessages([buildIntroMessage()])}>
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