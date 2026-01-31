# database.py
import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

DB_FILE = "knowledge_base.json"

def initialize_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump([], f)

def save_to_database(raw_text):
    """
    RAG END: Takes raw text, automatically chunks it, saves to DB.
    """
    initialize_db()
    
    # Automatic Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    
    # Save to JSON
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for chunk in chunks:
        data.append({"content": chunk})
        
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"[Database] Saved {len(chunks)} chunks.")

def search_database(query):
    """
    USER END: Finds relevant chunks for the RAG system.
    """
    initialize_db()
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Simple keyword search (RAG retrieval)
    query_words = set(query.lower().split())
    relevant_chunks = []
    
    for item in data:
        chunk_text = item['content'].lower()
        # Basic match logic
        match_count = sum(1 for word in query_words if word in chunk_text)
        if match_count > 0:
            relevant_chunks.append(item['content'])
            
    return relevant_chunks[:3]