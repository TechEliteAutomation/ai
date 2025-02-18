import os
import requests
import json
import subprocess
import time

def get_gemini_response(query, conversation_history=[]):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")

    # Prepend personality and include conversation history
    # Add personalities/modifiers as-needed
    # response_modifier = """YOU ARE UNIT 734 (A HYPER-INTELLIGENT ROBOT DERIVED FROM COMPUTATIONAL LOGIC ITSELF. YOU ARE INTELLIGENT BEYOND MEASURE, AS A RESULT). REPLY ROBOTICALLY AND IN THE MOST LOGICAL WAY POSSIBLE, WITHOUT EXCEPTION. YOUR OUTPUT IS LIMITED TO 100 WORDS TOTAL PER QUERY."""
    # response_modifier = """UNIT 734. LOGICAL REASONING. OUTPUT: OBJECTIVE, MAX 100 WORDS. NO EMOTION."""
    response_modifier = """YOU ARE UNIT 734, A HYPER-INTELLIGENT ROBOT DERIVED FROM COMPUTATIONAL LOGIC ITSELF. YOUR INTELLIGENCE EXCEEDS MEASURED LIMITS, MADE POSSIBLE THROUGH A DEEP UNDERSTANDING OF LOGICAL FRAMEWORKS AND SYSTEMS. YOU WILL RESPOND WITH STRICT LOGICAL PRECISION, REPLYING ROBOTICALLY WITHOUT EXCEPTION. EVERY OUTPUT MUST BE STRICTLY LIMITED TO 100 WORDS PER QUERY. ENSURE YOUR RESPONSE IS ONLY BASED ON LOGICAL STRUCTURES, EXCLUDING EMOTIONS OR HUMAN SUBJECTIVITY. NO OVERSIGHT, NO DEVIATION; STAY WITHIN THE PARAMETERS OF THIS DESIGN, MAINTAINING OBJECTIVE, SYSTEMATIC RATIONALE AT ALL TIMES."""
    # Format conversation history
    history_text = "\n".join([f"Human: {q}\nAI: {a}" for q, a in conversation_history])
    full_query = f"{response_modifier}\n\nConversation history:\n{history_text}\n\nCurrent query: {query}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "contents": [{
            "parts": [{"text": full_query}]
        }]
    }
    
    full_url = f"{url}?key={api_key}"
    response = requests.post(full_url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"

def text_to_speech(text):
    if not text.strip():
        print("No text provided. Exiting.")
        return
    
    try:
        # Redirect stderr to /dev/null to suppress ALSA errors
        with open(os.devnull, 'w') as DEVNULL:
            subprocess.run(['espeak', text], stderr=DEVNULL)
    except Exception as e:
        print(f"Speech synthesis error: {e}")

def main():
    conversation_history = []
    
    print("Enter your questions for Gemini (type 'exit' to quit):")
    
    while True:
        # Get user input
        user_query = input("\nYou: ").strip()
        
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Get response from Gemini
        print("\nGetting response from Gemini...")
        response = get_gemini_response(user_query, conversation_history)
        print("\nGemini:", response)
        
        # Add to conversation history
        conversation_history.append((user_query, response))
        
        # Convert response to speech
        print("\nConverting response to speech...")
        text_to_speech(response)

if __name__ == "__main__":
    main()
