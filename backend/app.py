from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import ollama

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

app = Flask(__name__)
CORS(app)

# ✅ Faster + good quality embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    question = data.get("question", "").strip()

    if not text or not question:
        return jsonify({"answer": "Missing text or question"}), 400

    # ✅ Clean text (remove extra spaces)
    text = re.sub(r"\s+", " ", text)

    # 🔥 STEP 1: Better chunking (keeps sentences intact)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    docs = splitter.split_text(text)

    if not docs:
        return jsonify({"answer": "No product data found"})

    # 🔥 STEP 2: Vector store
    db = FAISS.from_texts(docs, embeddings)

    # 🔥 STEP 3: Retrieve best chunks
    relevant_docs = db.similarity_search(question, k=5)

    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # 🔥 STEP 4: Strong extraction prompt (generic)
    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a product assistant. "
                    "Answer ONLY from the provided context. "
                    "Extract exact values if present. "
                    "Keep answer very short (1 line). "
                    "Do NOT add general knowledge. "
                    "If answer is not found, reply exactly: Not available in product info."
                )
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{question}

Answer:
"""
            }
        ]
    )

    answer = response.get("message", {}).get("content", "No response")

    # ✅ Optional: return source snippet (good for UI / resume)
    sources = [doc.page_content[:200] for doc in relevant_docs]

    return jsonify({
        "answer": answer.strip(),
        "sources": sources
    })


@app.route("/")
def home():
    return "API is running 🚀"


if __name__ == "__main__":
    app.run(debug=True)