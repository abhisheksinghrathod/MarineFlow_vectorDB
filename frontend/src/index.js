// frontend/src/index.js
import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./chatbot.css";

function Chatbot() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [docId, setDocId] = useState(null);

  const handleSubmit = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setMatches([]);

    try {
      const response = await fetch("/api/ask/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      setAnswer(data.answer);
      setMatches(data.matches || []);
      setDocId(data.doc_id || null);
    } catch (error) {
      setAnswer("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <h1>MarineFlow Chatbot</h1>

      <div className="input-container">
        <textarea
          className="question-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask your question here..."
          rows={4}
        />
        <button
          onClick={handleSubmit}
          className={`submit-button ${loading ? "disabled" : ""}`}
          disabled={question.trim().length === 0 || loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {answer && (
        <div className="answer-box">
          <h2>Answer</h2>
          <p>{answer}</p>
          {docId && (
            <p className="doc-id">
              <strong>Source Document:</strong>{" "}
              <span className="doc-id-tag">{docId}</span>
            </p>
          )}
        </div>
      )}

      {matches.length > 0 && (
        <details className="matches-box">
          <summary>Top Matches</summary>
          <ul>
            {matches.map((match, idx) => (
              <li key={idx}>
                <pre>{match.clause}</pre>
                <em>Score: {match.score}</em>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<Chatbot />);