import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./chatbot.css";

function Chatbot() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [docId, setDocId] = useState("AGIOS_20230501");
  const [matches, setMatches] = useState([]);
  const [showMatches, setShowMatches] = useState(false);

  const handleSubmit = async () => {
    const res = await fetch("/api/ask/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, doc_id: docId }),
    });

    const data = await res.json();
    setAnswer(data.answer);
    setMatches(data.matches || []);
    setShowMatches(true);
  };

  return (
    <div className="chat-container">
      <h2>💬 MarineFlow AI Chatbot</h2>

      <div className="dropdown-area">
        <label htmlFor="doc">Document:</label>
        <select
          id="doc"
          value={docId}
          onChange={(e) => setDocId(e.target.value)}
        >
          <option value="AGIOS_20230501">AGIOS_20230501</option>
          {/* Add more doc IDs here */}
        </select>
      </div>

      <div className="input-area">
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={handleSubmit}>Ask</button>
      </div>

      {answer && <div className="chat-response">{answer}</div>}

      {matches.length > 0 && (
        <div className="match-section">
          <button
            className="toggle-matches"
            onClick={() => setShowMatches(!showMatches)}
          >
            {showMatches ? "🔽 Hide Top Matches" : "▶️ Show Top Matches"}
          </button>
          {showMatches && (
            <ul className="match-list">
              {matches.map((m, idx) => (
                <li key={idx}>
                  <pre className="clause-wrap">{m.clause}</pre>
                  <div className="match-score">Score: {m.score}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<Chatbot />);
