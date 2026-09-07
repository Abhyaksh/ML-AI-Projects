# import os
# from dotenv import load_dotenv

# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings

# import google.generativeai as genai

# # Load environment variables
# load_dotenv()

# # Configure Gemini
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# # Load Gemini Model
# model = genai.GenerativeModel("gemini-2.5-flash")

# # Load embedding model
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

# # Load FAISS vector database
# db = FAISS.load_local(
#     "faiss_index",
#     embeddings,
#     allow_dangerous_deserialization=True
# )

# def ask_question(question):

#     # Retrieve top 3 relevant chunks
#     docs = db.similarity_search(question, k=3)

#     context = "\n\n".join([doc.page_content for doc in docs])
    
#     prompt = f"""
# You are an experienced Investment Banking Analyst.

# You are answering questions about a Financial Modelling and Valuation Excel workbook.

# Instructions:

# - Use the retrieved context as the primary source.
# - Explain the answer in simple professional language.
# - If the context contains numerical values, include them.
# - If the context contains formulas or calculations, explain them.
# - You may use your finance knowledge to explain concepts like WACC, DCF, Enterprise Value, EBITDA, etc., but do NOT invent numbers that are not present in the context.
# - If the workbook does not contain the requested information, reply:
#   "I couldn't find that information in the financial model."

# Context:
# {context}

# Question:
# {question}

# Answer in this format:

# Answer:
# ...

# Key Figures:
# ...

# Explanation:
# ...
# """

#     response = model.generate_content(prompt)

#     return response.text

import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

import google.generativeai as genai

# ---------------- Load Environment ---------------- #

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- Embedding Model ---------------- #

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------- Load FAISS ---------------- #

def load_vector_db(index_folder="faiss_index"):

    db = FAISS.load_local(
        index_folder,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db


# ---------------- Ask Question ---------------- #

def ask_question(
    question,
    index_folder="faiss_index"
):

    # Load selected vector database
    db = load_vector_db(index_folder)

    # Retrieve top relevant chunks
    docs = db.similarity_search(
        question,
        k=5
    )

    # Context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # Source Sheets
    sources = []

    for doc in docs:

        source = doc.metadata.get("source", "")

        if source:

            source = os.path.basename(source)

            source = source.replace(".txt", "")
            source = source.replace("_", " ")

            if source not in sources:
                sources.append(source)

    # Prompt
    prompt = f"""
You are a Senior Investment Banking Analyst.

You are answering questions about a Financial Modelling & Valuation Excel workbook.

Rules:

- Use ONLY the retrieved context.
- Never invent financial numbers.
- If numerical values exist, include them.
- Explain calculations wherever possible.
- Explain finance concepts professionally but simply.
- Display WACC, Growth Rates and Cost of Debt as percentages.
- If information is unavailable, reply:
"I couldn't find that information in the workbook."

Context:
{context}

Question:
{question}

Return the answer in exactly this format:

### Answer

### Key Figures

### Explanation
"""

    response = model.generate_content(prompt)

    return {
        "answer": response.text,
        "sources": sources
    }


# ---------------- Test ---------------- #

if __name__ == "__main__":

    while True:

        q = input("\nAsk: ")

        if q.lower() == "exit":
            break

        result = ask_question(q)

        print("\n")
        print(result["answer"])

        print("\nSources:")
        print(result["sources"])