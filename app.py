# app.py
import os
import google.generativeai as genai

# STRICT IMPORTS
from database import *
from pdf_to_raw_text import *

# --- CONFIGURATION ---
api_key = os.getenv("GOOGLE_API_KEY") 
if not api_key:
    print("Missing GOOGLE_API_KEY")
    exit()

genai.configure(api_key=api_key)
# Using 2.0 Flash for best speed and native audio understanding
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# --- NEW: AUDIO TO TEXT (Using Native Gemini - No extra libs!) ---
def speech_to_hindi_text(file_path):
    """
    Takes an audio file (mp3, wav) and uses Gemini to transcribe it to Hindi text.
    No PyAudio, no Spacy, no installation errors.
    """
    print(f"--- Transcribing Audio: {file_path} ---")
    
    if not os.path.exists(file_path):
        return "Error: Audio file not found."

    try:
        # Upload file to Gemini
        myfile = genai.upload_file(file_path)
        
        # Prompt Gemini to transcribe specifically in Hindi
        prompt = "Listen to this audio file and transcribe the speech into Hindi text. Only output the transcribed text."
        response = model.generate_content([prompt, myfile])
        
        # Clean up text
        return response.text.strip()
    except Exception as e:
        print(f"Audio Error: {e}")
        return "Could not understand audio."

# --- TRANSLATION LOGIC ---
def translate_hindi_to_english(text):
    """Hindi Text -> English Text"""
    prompt = f"Translate this Hindi text to English. Only output the translation:\n{text}"
    response = model.generate_content(prompt)
    return response.text.strip()

def translate_to_hindi(text):
    """English Text -> Hindi Text"""
    prompt = f"Translate this English answer to Hindi. Only output the Hindi translation:\n{text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# --- RAG LOGIC ---
def generate_rag_answer(query, context):
    prompt = f"""
    Context: {context}
    Query: {query}
    Answer the query based ONLY on the context provided.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# --- 1. RAG END (ADMIN) ---
def run_rag_ingestion(file_path):
    print(f"--- Uploading {file_path} ---")
    raw_text = extract_text(file_path)
    if not raw_text:
        print("Error: Could not extract text.")
        return
    save_to_database(raw_text)
    print("--- Upload Complete ---")

# --- 2. USER END (CLIENT) ---
def run_user_agent(input_data):
    """
    Smart Input:
    - If 'input_data' is a text string (Hindi): Uses it directly.
    - If 'input_data' is a file path (.mp3/.wav): Transcribes it first.
    """
    
    # Step 0: Check if input is Audio or Text
    hindi_prompt = ""
    if isinstance(input_data, str) and os.path.exists(input_data):
        # It's a file path!
        hindi_prompt = speech_to_hindi_text(input_data)
    elif isinstance(input_data, str):
        # It's raw text!
        hindi_prompt = input_data
    else:
        return "Invalid input format."

    print(f"--- User Input (Hindi): {hindi_prompt} ---")
    
    # 1. Hindi -> English (For Searching)
    english_query = translate_hindi_to_english(hindi_prompt)
    print(f"--- Internal Query (Eng): {english_query} ---")
    
    # 2. Search Database
    relevant_chunks = search_database(english_query)
    
    if not relevant_chunks:
        return "माफ़ करें, मुझे डेटाबेस में कोई जानकारी नहीं मिली।"
    
    context = "\n".join(relevant_chunks)
    
    # 3. Generate Answer in English
    english_answer = generate_rag_answer(english_query, context)
    
    # 4. English -> Hindi (Final Output)
    final_hindi_answer = translate_to_hindi(english_answer)
    
    return final_hindi_answer

if __name__ == "__main__":
    print("System Ready. Supports Text or Audio Files (mp3/wav).")
    
    # --- TEST WITH TEXT ---
    # response = run_user_agent("इस मैनुअल में इंस्टालेशन कैसे करें?")
    # print(f"Bot: {response}")

    # --- TEST WITH AUDIO ---
    # Assuming you have a file called 'question.mp3' in the same folder
    # response = run_user_agent("question.mp3")
    # print(f"Bot: {response}")
    # ... (keep all your existing code above) ...

# --- WEB SERVER STARTER ---
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    # Get data from the user (Text or Audio File URL)
    data = request.json
    user_input = data.get('input') # Can be Hindi Text or File Path

    # Run your RAG Logic
    response_text = run_user_agent(user_input)
    
    return jsonify({"answer": response_text})

if __name__ == '__main__':
    # IMPORTANT FOR RENDER:
    # '0.0.0.0' makes it accessible to the outside world
    # Port 10000 is standard for Render free tier
    app.run(host='0.0.0.0', port=10000)
