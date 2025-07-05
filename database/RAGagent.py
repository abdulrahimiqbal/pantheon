from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Step 1: Load PDFs
paths = ["Data/data1.pdf", "Data/data2.pdf", "Data/data3.pdf"]
documents = []

for path in paths:
    loader = PyPDFLoader(path)
    documents.extend(loader.load())

# Step 2: Split text
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(documents)

# Step 3: Use HuggingFace embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Step 4: Create Chroma vector DB
vectordb = Chroma.from_documents(chunks, embedding_model, persist_directory="db")
vectordb.persist()


import google.generativeai as genai

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.5-pro")

retriever = vectordb.as_retriever()

def ask_gemini(query):
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""Use the following context to answer the question. 
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {query}
"""
    response = model.generate_content(prompt)
    return response.text

# Example
print(ask_gemini("What are the key ideas in data1.pdf?"))
