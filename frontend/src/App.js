import React, { useState } from "react";
import ReactMarkdown from "react-markdown";

const API_BASE = "https://fuzzy-invention-x6qvq5qqg6pfvrgv-8000.app.github.dev";

const spinnerStyle = {
  display: "inline-block",
  width: 24,
  height: 24,
  border: "3px solid #ccc",
  borderTop: "3px solid #333",
  borderRadius: "50%",
  animation: "spin 1s linear infinite",
};

// スピナー用CSS
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}
`;
document.head.appendChild(styleSheet);

// トグルボタン用スタイル
const toggleContainer = {
  display: "flex",
  margin: "12px 0",
  borderRadius: 8,
  overflow: "hidden",
  border: "1px solid #aaa",
  width: 220,
};

const toggleBtn = (active) => ({
  flex: 1,
  padding: "2px 0",
  background: active ? "#333" : "#f5f5f5",
  color: active ? "#fff" : "#333",
  border: "none",
  cursor: "pointer",
  fontWeight: active ? "bold" : "normal",
  fontSize: 14,
  transition: "background 0.2s, color 0.2s",
});

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("answer"); // "answer" or "hint"

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse("");
    try {
      const endpoint = mode === "answer" ? "create_answer" : "create_hint";
      const res = await fetch(`${API_BASE}/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (err) {
      setResponse("エラーが発生しました");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 32 }}>
      <h1>Copilot Chatbot</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="質問を入力"
          style={{
            width: 300 * 1.5,      // 横幅1.5倍
            height: 20,        // 縦幅2倍（デフォルト約32px）
            fontSize: 14,          // 文字も少し大きく
            padding: "12px 16px",  // パディングも調整
            boxSizing: "border-box"
          }}
        />
        <div style={toggleContainer}>
          <button
            type="button"
            style={toggleBtn(mode === "answer")}
            onClick={() => setMode("answer")}
          >
            回答生成
          </button>
          <button
            type="button"
            style={toggleBtn(mode === "hint")}
            onClick={() => setMode("hint")}
          >
            ヒント生成
          </button>
        </div>
        <button type="submit" disabled={loading}>送信</button>
      </form>
      <div style={{ marginTop: 24 }}>
        <strong>応答:</strong>
        <div>
          {loading ? (
            <span style={spinnerStyle}></span>
          ) : (
            <ReactMarkdown>{response}</ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
