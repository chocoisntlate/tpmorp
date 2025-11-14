import { useEffect, useRef, useState } from "react";
import "./App.css";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws/chat";
const SESSION_ID = "session-" + Math.random().toString(36).substr(2, 9);
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
        Hi, I'm <RetpmorpWord />. Feed me a thought and I'll flip it on its head.
      </>
    ),
  });

  const [messages, setMessages] = useState(() => [buildIntroMessage()]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const chatRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    chatRef.current?.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message:", data);

      if (data.type === "ai_response") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.message },
        ]);
        setLoading(false);
      } else if (data.type === "error") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Error: ${data.error}` },
        ]);
        setLoading(false);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "WebSocket connection error. Please check the server.",
        },
      ]);
      setConnected(false);
      setLoading(false);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || !connected) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userText }]);
    setLoading(true);

    try {
      wsRef.current.send(
        JSON.stringify({
          message: userText,
          session_id: SESSION_ID,
          model: "llama2",
        })
      );
    } catch (err) {
      console.error("Send error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Failed to send message. Please check the connection.",
        },
      ]);
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
            FastAPI · React · WebSocket {connected ? "✓" : "✗"}
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
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage(e);
            }
          }}
          placeholder="Send a message..."
        />
        <button type="submit" disabled={!input.trim() || loading || !connected}>
          Send
        </button>
      </form>
    </div>
  );
}