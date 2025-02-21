import os
import requests
import json
import datetime
import csv

def get_gemini_response(query, conversation_history=[]):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")
    
    history_text = "\n".join([f"Human: {q}\nAI: {a}" for q, a in conversation_history])
    full_query = f"{history_text}\n\nCurrent query: {query}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": full_query}]}]}
    
    response = requests.post(f"{url}?key={api_key}", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No response.")
    else:
        return f"Error: {response.status_code} - {response.text}"

def save_markdown(report_text, filename):
    os.makedirs(os.path.expanduser("~/research"), exist_ok=True)
    filepath = os.path.expanduser(f"~/research/{filename}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Markdown report saved to: {filepath}")

def save_csv(data_rows, headers, filename):
    os.makedirs(os.path.expanduser("~/research"), exist_ok=True)
    filepath = os.path.expanduser(f"~/research/{filename}")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)
    print(f"CSV report saved to: {filepath}")

def research_species(species_name):
    conversation_history = []
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename_md = f"{date_str}_{species_name.replace(' ', '_')}.md"
    filename_csv = f"{date_str}_{species_name.replace(' ', '_')}.csv"
    
    research_queries = [
        f"Provide a scientific overview of {species_name}, including classification, habitat, and behavior.",
        f"List key characteristics and adaptations of {species_name}.",
        f"Provide dietary habits and common predators of {species_name}.",
        f"Detail the reproductive cycle and lifespan of {species_name}.",
        f"Describe the conservation status and any threats to {species_name}."
    ]
    
    markdown_report = f"# Research Report: {species_name}\n\n## Table of Contents\n"
    markdown_report += "\n".join([f"- [{query}](#{query.lower().replace(' ', '-')})" for query in research_queries])
    markdown_report += "\n\n"
    
    csv_data = []
    headers = ["Query", "Response"]
    
    for query in research_queries:
        print(f"Researching: {query}")
        response = get_gemini_response(query, conversation_history)
        conversation_history.append((query, response))
        
        markdown_report += f"## {query}\n\n{response}\n\n"
        csv_data.append([query, response])
    
    save_markdown(markdown_report, filename_md)
    save_csv(csv_data, headers, filename_csv)

if __name__ == "__main__":
    research_species("Passer domesticus")
