# 🎬 YouTube AI Chatbot

A RAG-powered chatbot that lets you have a full conversation with any YouTube video. Paste a URL, and ask anything — it finds exact answers from any part of the video. Supports Hindi and multilingual videos, with all responses delivered in English.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=flat-square&logo=react)
![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-1C3C3C?style=flat-square)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai)

---

## 📸 Demo

> Paste a YouTube URL → Ask questions → Get precise answers instantly

---

## ✨ Features

- 🔗 **Paste any YouTube URL** — works with long-form videos, lectures, interviews, and more
- 🔍 **Finds exact answers** from any part of the video using semantic search
- 🌐 **Multilingual support** — handles Hindi and other languages, always answers in English
- 💬 **Conversational chat UI** — clean, modern interface built with React + Tailwind CSS
- 🧠 **RAG pipeline** — retrieves only the most relevant chunks before generating an answer
- ⚡ **Fast responses** — powered by OpenAI embeddings + ChromaDB vector store

---

## 🏗️ Architecture

```
User Input (YouTube URL)
        │
        ▼
YouTube Transcript API
        │
        ▼
Text Splitting (RecursiveCharacterTextSplitter)
        │
        ▼
OpenAI Embeddings (text-embedding-3-large)
        │
        ▼
ChromaDB Vector Store
        │
  ┌─────┴─────┐
  │           │
Query      Retriever (Top-K similarity)
  │           │
  └─────┬─────┘
        │
Translation to English (if needed)
        │
        ▼
Prompt Template + GPT-4o-mini
        │
        ▼
Answer streamed to React Frontend
```

---

## 🛠️ Tech Stack

### Backend
| Tool | Purpose |
|------|---------|
| FastAPI | REST API server |
| LangChain | RAG pipeline orchestration |
| OpenAI (`text-embedding-3-large`) | Text embeddings |
| OpenAI (`GPT-4o-mini`) | Answer generation |
| ChromaDB | Vector store for semantic search |
| youtube-transcript-api | Fetching video transcripts |
| translate | Translating non-English chunks to English |

### Frontend
| Tool | Purpose |
|------|---------|
| React 18 | UI framework |
| Tailwind CSS | Styling |
| React Hook Form | Form management & validation |
| Axios | HTTP requests to backend |

---

## 📁 Project Structure

```
youtube-ai-chatbot/
├── backend/
│   ├── main.py               # FastAPI app, routes, RAG pipeline
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables (not committed)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.jsx    # Main chatbot UI component
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── tailwind.config.js
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI API key

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/youtube-ai-chatbot.git
cd youtube-ai-chatbot
```

---

### 2. Backend Setup

```bash
cd backend
```

Create a virtual environment and activate it:

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will be running at `http://localhost:8000`

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be running at `http://localhost:5173`

---

## 🔌 API Reference

### `POST /url/upload`

Loads and processes the YouTube video transcript into the vector store.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "message": "Transcript processed successfully"
}
```

---

### `POST /api/chat`

Sends a user query and returns an AI-generated answer based on the video content.

**Request Body:**
```json
{
  "query": "What is the main topic of this video?",
  "history": [
    { "role": "user", "content": "previous question" },
    { "role": "assistant", "content": "previous answer" }
  ]
}
```

**Response:**
```json
"The main topic of this video is..."
```

---

## ⚙️ How It Works

1. **URL Upload** — The user pastes a YouTube URL. The backend extracts the video ID, fetches the transcript using `youtube-transcript-api`, and splits it into overlapping chunks of 500 characters.

2. **Embedding & Indexing** — Each chunk is embedded using OpenAI's `text-embedding-3-large` model and stored in a ChromaDB vector store in memory.

3. **Query Processing** — When the user asks a question, the retriever performs a similarity search and fetches the top-K most relevant chunks.

4. **Translation** — If the retrieved chunks are in a non-English language, they are translated to English using the `translate` library.

5. **Answer Generation** — The translated context, conversation history, and user query are passed to GPT-4o-mini via a structured prompt template. The answer is returned and displayed in the chat UI.

---

## 🧩 RAG Pipeline (LangChain)

```python
parallel_chain = RunnableParallel({
    "context": retriever | translate_to_english | format_docs,
    "query": RunnablePassthrough(),
    "history": RunnableLambda(lambda _: format_history(data.history)),
})

final_chain = parallel_chain | prompt | ChatOpenAI() | StrOutputParser()
```

---

## 📦 requirements.txt

```
fastapi
uvicorn
langchain
langchain-openai
langchain-chroma
langchain-text-splitters
langchain-core
youtube-transcript-api
chromadb
openai
python-dotenv
translate
pydantic
```

---

## 🌍 Multilingual Support

The chatbot supports videos in **any language**. When chunks in a non-English language are retrieved, they are automatically translated to English before being passed to the model. The final answer is always in English.

Tested with:
- ✅ English
- ✅ Hindi
- ✅ Mixed language videos

---

## 🔒 Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key from [platform.openai.com](https://platform.openai.com) |

---

## 🙌 Acknowledgements

- [LangChain](https://www.langchain.com/) — for the RAG orchestration framework
- [OpenAI](https://openai.com/) — for embeddings and language model
- [ChromaDB](https://www.trychroma.com/) — for the vector store
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) — for fetching transcripts

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📬 Contact

Made with ❤️ by [Aditya Soran](https://github.com/adityasoran0698)

> ⭐ If you found this project helpful, please give it a star!
