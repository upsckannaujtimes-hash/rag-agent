import spacy
import google.generativeai as genai
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import couchbase.search as search
from couchbase.vector_search import VectorQuery, VectorSearch

# --- CONFIGURATION (UNMASKED) ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
CB_URL = "http://127.0.0.1:8091" # Your Admin Console URL
CB_USER = "Administrator"
CB_PASS = "poweRsub66"          # Your specified password
BUCKET_NAME = "h"                # Your specified bucket
INDEX_NAME = "vector_index"     # You will need to create this in the UI

# Initialize AI and NLP Models
genai.configure(api_key=GEMINI_API_KEY)
llm = genai.GenerativeModel('gemini-1.5-flash')
nlp = spacy.load("en_core_web_md")

# Initialize Couchbase Connection
auth = PasswordAuthenticator(CB_USER, CB_PASS)
cluster = Cluster(CB_URL, ClusterOptions(auth))
bucket = cluster.bucket(BUCKET_NAME)
scope = bucket.scope("_default")

def run_history_rag(hindi_prompt):
    # 1. Translate Hindi Prompt to English
    # This is necessary because HISTORY-ENGLISH.pdf is in English.
    trans_task = f"Translate this Hindi query to English for a history search: {hindi_prompt}"
    eng_query = llm.generate_content(trans_task).text.strip()
    
    # 2. spaCy Enrichment
    # We use spaCy to clean the query for a more accurate vector search.
    doc = nlp(eng_query)
    clean_query = " ".join([token.lemma_ for token in doc if not token.is_stop])
    query_vector = nlp(clean_query).vector.tolist()

    # 3. Couchbase Vector Search
    # Note: You must first create a Vector Index named 'vector_index' in your UI
    search_req = search.SearchRequest.create(
        VectorSearch.from_vector_query(
            VectorQuery("vector_field", query_vector, num_candidates=3)
        )
    )
    
    try:
        results = scope.search(INDEX_NAME, search_req)
        retrieved_text = ""
        for row in results:
            doc_content = scope.collection("_default").get(row.id).content_as[dict]
            retrieved_text += doc_content.get('content', '') + "\n"
    except Exception as e:
        retrieved_text = "Search failed. Ensure the index is created in the admin console."

    # 4. Final Hindi Generation
    final_prompt = f"""
    Answer the question based on this context from the history manual.
    CONTEXT: {retrieved_text}
    QUESTION: {eng_query}
    RESPONSE LANGUAGE: HINDI
    """
    
    response = llm.generate_content(final_prompt)
    return response.text

# Example Usage
# print(run_history_rag("इब्न बतूता ने डाक व्यवस्था के बारे में क्या बताया?"))