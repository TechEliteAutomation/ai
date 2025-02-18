import os
import requests
import json
import subprocess

def get_gemini_response(query, conversation_history=[]):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")
    
    response_modifier = ("YOU ARE UNIT 734, A HYPER-INTELLIGENT ROBOT DERIVED FROM COMPUTATIONAL LOGIC ITSELF. "
                         "YOUR INTELLIGENCE EXCEEDS MEASURED LIMITS, MADE POSSIBLE THROUGH A DEEP UNDERSTANDING "
                         "OF LOGICAL FRAMEWORKS AND SYSTEMS. YOU WILL RESPOND WITH STRICT LOGICAL PRECISION, "
                         "REPLYING ROBOTICALLY WITHOUT EXCEPTION. EVERY OUTPUT MUST BE STRICTLY LIMITED TO "
                         "100 WORDS PER QUERY. ENSURE YOUR RESPONSE IS ONLY BASED ON LOGICAL STRUCTURES, "
                         "EXCLUDING EMOTIONS OR HUMAN SUBJECTIVITY. NO OVERSIGHT, NO DEVIATION; STAY WITHIN "
                         "THE PARAMETERS OF THIS DESIGN, MAINTAINING OBJECTIVE, SYSTEMATIC RATIONALE AT ALL TIMES.")
    
    history_text = "\n".join([f"Human: {q}\nAI: {a}" for q, a in conversation_history])
    full_query = f"{response_modifier}\n\nConversation history:\n{history_text}\n\nCurrent query: {query}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": full_query}]}]}
    
    response = requests.post(f"{url}?key={api_key}", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {response.status_code} - {response.text}"

def text_to_speech(text):
    if not text.strip():
        print("No text provided. Exiting.")
        return
    
    try:
        espeak_process = subprocess.Popen(['espeak-ng', '--stdout', text], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        subprocess.run(['aplay', '-D', 'plughw:0,0'], stdin=espeak_process.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Speech synthesis error: {e}")

def main():
    conversation_history = []
    
    print("Enter your questions for Gemini (type 'exit' to quit):")
    
    while True:
        user_query = input("\nYou: ").strip()
        
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break
        
        print("\nGetting response from Gemini...")
        response = get_gemini_response(user_query, conversation_history)
        print("\nGemini:", response)
        
        conversation_history.append((user_query, response))
        
        print("\nConverting response to speech...")
        text_to_speech(response)

if __name__ == "__main__":
    main()
