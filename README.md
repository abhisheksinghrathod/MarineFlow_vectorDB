# 🚢 MarineFlow AI Chatbot

MarineFlow AI Chatbot is a smart assistant designed to help users query Recap and Statement of Facts (SOF) shipping documents using natural language. Powered by OpenAI’s GPT-4-turbo and vector search using pgvector, it provides accurate clause-level answers from embedded shipping documents — **no need to select the document manually!**

---

## ✨ Features

- 🤖 Ask natural language questions about shipping Recap/SOF documents
- 📄 Automatically selects the most relevant document and clauses
- 💬 Clean and responsive React-based UI with collapsible clause matches
- 📚 Clause vector search using pgvector + cosine similarity
- 📌 Source document (`doc_id`) displayed with each answer
- ⛔ Ask button is disabled until a valid question is typed
- 🎯 Efficient token-budget-aware chunk selection (max 3000 tokens)
- ⚡ Powered by OpenAI GPT-4-turbo and `text-embedding-3-small` model

---

## 🛠️ Tech Stack

- **Backend**: Django + Django REST Framework (DRF)
- **Vector DB**: PostgreSQL with `pgvector`
- **LLM**: OpenAI GPT-4-turbo
- **Frontend**: React (with Webpack, Babel, and CSS modules)

---

## 📦 Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- Node.js & npm
- OpenAI API key

---

## 🧩 Project Structure

```bash
vectorDB/
├── flowAI/
│   ├── models.py           # ClauseEmbedding model
│   ├── views.py            # Core chatbot logic
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── index.js        # React UI code
│   │   └── chatbot.css     # Styling
│   ├── templates/
│   │   └── frontend/index.html
│   ├── urls.py             # Frontend URL route
│   ├── views.py            # Renders index.html
│   ├── webpack.config.js
│   └── ...
├── vectorDB/
│   └── settings.py         # WebpackLoader, static files config
├── manage.py
└── requirements.txt
```

## 🚀 Setup Instructions

### 1. Clone and Install Dependencies

```
git clone https://github.com/yourusername/marineflow-chatbot.git
cd marineflow-chatbotpython3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup PostgreSQL with pgvector

```
-- inside psql shell
CREATE EXTENSION IF NOT EXISTS vector;
```

</span></span></code></div></div></pre>

Then update your `settings.py` for DB configuration.

---

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Setup Frontend (React + Webpack)

```
cd frontend
npm install
npm run build
```

</span></span></code></div></div></pre>

This builds the React UI into `static/bundle.js`.

---

### 5. Run Django Server

```
cd ..
python manage.py migrate
python manage.py runserver
```

</span></span></code></div></div></pre>

Visit [http://localhost:8000/chatbot/]()

---

## 💬 Usage

1. Ask a question like:
   > What is the LAYCAN window?
   >
2. The chatbot will:
   * Embed the question
   * Search all documents for closest matches
   * Identify the best document
   * Return an accurate answer using GPT-4-turbo
   * Display top matching clauses

---

## 🧠 How It Works

* **Embedding**: Questions are embedded via `text-embedding-3-small`
* **Vector Search**: Uses cosine similarity via `pgvector` to find closest clauses
* **Context Assembly**: Best clauses (within 3000 token limit) are assembled
* **LLM Answer**: GPT-4-turbo is prompted with the context and question
* **Doc Selection**: Most common `doc_id` among top matches is auto-selected

---

## 🎨 UI Highlights

* Styled question box + smaller "Ask" button
* `Ask` changes to `Thinking...` when loading
* Clause matches in collapsible section
* Texts auto-wrapped and styled for readability
* Source document highlighted under the answer

---

## 📈 Future Enhancements

* ✅ Upload documents from UI
* ✅ Admin dashboard for managing clause embeddings
* ⏳ Support multi-page PDFs and scanned images
* ⏳ Improve clause chunking accuracy with fuzzy matching
* ⏳ Chat history and feedback scoring

---

## 🤝 Contributing

PRs welcome! Please raise an issue first to discuss what you’d like to change.

---

## 📝 License

MIT © 2025 MarineFlow

---

## 🧪 Sample Questions to Try

* Where and how should NOR be submitted?
* What is the LAYCAN window?
* What are the load rates at the port?
* When does laytime start counting?
* Who is responsible for discharging costs?
