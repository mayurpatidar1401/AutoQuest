AutoQuest

AutoQuest is a local AI-powered assistant that automatically answers job application questions using your existing resume context and a growing knowledge base of previous Q&A entries. It supports:

Fast and reliable response generation using the Mistral LLM via Ollama

Offline semantic search using ChromaDB and sentence-transformers

Logging new questions and answers for future accuracy

An API (via FastAPI) to integrate with your job automation tools

🚀 Features

✅ Automatically answer job application questions (Yes/No, multiple choice, open-ended)

🧠 Learns from QA_sheet.xlsx and semantic embeddings

🔍 Semantic similarity search for previous Q&A

📈 Grows its knowledge over time as new answers are logged

🌐 REST API endpoint (/ask) for integration with job bots

📁 Project Structure

AutoQuest/
├── main.py                      # Entry point with FastAPI + CLI
├── autoquest/
│   ├── agent.py                 # LLM & Retrieval chain setup
│   ├── embed.py                 # Document + Excel embedding logic
│   ├── config.py                # Loads config.yaml
│   └── config.yaml              # All configuration settings
├── data/
│   └── QA_sheet.xlsx            # Your growing personal knowledge base
├── chromadb/                   # Persistent vector store
└── requirements.txt            # Python dependencies

🛠️ Installation

Clone the repository:

bash
Copy code
git clone https://github.com/mayurpatidar1401/AutoQuest.git
cd AutoQuest

Create virtual environment:

bash
Copy code
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

Install dependencies:

bash
Copy code
pip install -r requirements.txt

Run the server:
bash
Copy code
python main.py runserver

Test the API:
bash
Copy code
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question": "What is your current job title?"}'

🧠 How It Works

1. On startup, AutoQuest embeds new entries from QA_sheet.xlsx.

2. When a question is asked:

 - If an exact match exists in Excel, it returns it

 - Else, it checks the vector DB for a semantically close answer

 - Else, it uses the LLM to generate a response

3. The final answer is logged into QA_sheet.xlsx for future reuse.

🤖 Notes

This tool runs fully locally, with no external API calls

Supports both API mode and CLI mode

Easily pluggable into LinkedIn or job portal bots

