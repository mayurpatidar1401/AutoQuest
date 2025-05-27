from autoquest.agent import load_agent
from autoquest.embed import embed_qa_sheet_incrementally
from datetime import datetime
from fastapi import FastAPI, Request
from pytz import timezone
import pandas as pd
import os, sys
import re
import uvicorn

app = FastAPI()

# Load embeddings and agent on startup
print("📥 Initializing AutoQuest Agent...")
embed_qa_sheet_incrementally()
agent, qa_dict, vectordb = load_agent()

@app.get("/")
def root():
    return {"message": "AutoQuest is running"}

def clean_numeric_answer(text):
    match = re.search(r"\b([3-4])\b", str(text))
    return match.group(1) if match else "3"

def extract_answer_text(answer_obj, query):
    if isinstance(answer_obj, dict) and "result" in answer_obj:
        raw = answer_obj["result"]
    else:
        raw = str(answer_obj)

    # Determine if this is a Yes/No question (explicit options)
    is_yesno = bool(re.search(r"\b(Yes|No)\b", query, re.IGNORECASE))

    # Step 1: Strict match for Yes/No
    yn_match = re.search(r"(?i)Answer:\s*(Yes|No)\b", raw)
    if yn_match:
        return yn_match.group(1).strip()

    # Step 2: If marked as Yes/No type, fallback to any "yes" or "no" in output
    if is_yesno:
        if "yes" in raw.lower():
            return "Yes"
        elif "no" in raw.lower():
            return "No"
        else:
            return "Yes"  # Default fallback for yes/no questions

    # Step 3: Fallback to 3 or 4 if it's likely numeric
    num_match = re.search(r"\b([3-4])\b", raw)
    if num_match:
        return num_match.group(1)

    # Step 4: Fallback to generic answer
    generic_match = re.search(r"(?i)Answer:\s*(.+)", raw)
    if generic_match:
        return generic_match.group(1).strip()

    lines = raw.strip().splitlines()
    return lines[-1].strip() if lines else raw.strip()

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    query = data.get("question", "").strip()
    query_for_search  = re.sub(r"\n\s*(Yes|No)\b", "", query, flags=re.IGNORECASE).strip()
    query_key = query_for_search .lower()

    # Default to None, fill below
    answer = None

    # First try exact match
    if query_key in qa_dict:
        answer = qa_dict[query_key]
    else:
        # Try semantic match from Chroma vector store
        similar_docs = vectordb.similarity_search(query, k=1)
        if similar_docs:
            matched_doc = similar_docs[0]
            answer = matched_doc.metadata.get("answer", None)

        # If no similar result, use the LLM
        if not answer:
            response = agent.invoke({"question": query, "context": ""})
            raw_answer = response.get("result") if isinstance(response, dict) else str(response)
            answer = extract_answer_text(raw_answer, query)
        else:
            answer = extract_answer_text(answer, query)


    # ✅ Save to QA_sheet.xlsx in `data/`
    try:
        df = pd.DataFrame([{
            "Question": query,
            "Answer": answer
        }])

        file_path = os.path.join("data", "QA_sheet.xlsx")
        os.makedirs("data", exist_ok=True)

        if os.path.exists(file_path):
            existing_df = pd.read_excel(file_path)
            combined = pd.concat([existing_df, df], ignore_index=True)
            combined.drop_duplicates(subset=["Question", "Answer"], keep="last", inplace=True)
            combined.to_excel(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)

        print(f"✅ Logged Q&A to {file_path}")
    except Exception as e:
        print(f"❌ Could not log to Excel: {e}")

    return {"answer": extract_answer_text(answer, query)}

# Optional CLI mode for testing
def main():
    from prompt_toolkit import prompt
    print("🧠 AutoQuest - CLI Mode")
    while True:
        query = prompt("🧾 Ask a question (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            break
        response = agent.invoke({"question": query, "context": ""})
        raw_answer = response.get("result") if isinstance(response, dict) else str(response)
        cleaned_answer = extract_answer_text(raw_answer, query)
        print("🤖", cleaned_answer, "\n")


if __name__ == "__main__":
     if "runserver" in sys.argv:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
