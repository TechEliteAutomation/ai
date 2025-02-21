import os
import requests
import json
import datetime
import csv
import schedule
import time
import yaml
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple
import logging
from collections import defaultdict

class ResearchAgent:
    def __init__(self, config_path: str = "research_config.yaml"):
        self.setup_logging()
        self.load_configuration(config_path)
        self.conversation_history = defaultdict(list)
        self.setup_directories()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('research_agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_configuration(self, config_path: str):
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.warning("Configuration file not found. Using default configuration.")
            self.config = {
                'api_key': os.getenv("GEMINI_API_KEY"),
                'research_categories': ['technology', 'market_trends', 'industry_developments'],
                'update_frequency': {
                    'technology': '12h',
                    'market_trends': '24h',
                    'industry_developments': '48h'
                },
                'output_directory': '~/research_reports'
            }

    def setup_directories(self):
        self.base_dir = Path(os.path.expanduser(self.config['output_directory']))
        for category in self.config['research_categories']:
            (self.base_dir / category / 'markdown').mkdir(parents=True, exist_ok=True)
            (self.base_dir / category / 'csv').mkdir(parents=True, exist_ok=True)

    def get_ai_response(self, query: str, category: str) -> str:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
        history_text = "\n".join([
            f"Human: {q}\nAI: {a}" 
            for q, a in self.conversation_history[category]
        ])
        
        full_query = f"""Context: You are analyzing {category} trends.
Previous conversation: {history_text}
Current query: {query}
Please provide a detailed, well-structured analysis."""

        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": full_query}]}]}

        try:
            response = requests.post(
                f"{url}?key={self.config['api_key']}", 
                headers=headers, 
                json=data
            )
            response.raise_for_status()
            return response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No response.")
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            return f"Error: {str(e)}"

    def generate_research_queries(self, category: str) -> List[str]:
        base_queries = {
            'technology': [
                "What are the latest breakthrough technologies in the past week?",
                "Identify emerging technology trends and their potential impact",
                "Detail significant technological advancements and their applications",
                "Analyze current technology adoption patterns",
                "Examine potential disruptions in the technology landscape"
            ],
            'market_trends': [
                "What are the current market shifts and patterns?",
                "Identify emerging market opportunities and challenges",
                "Analyze consumer behavior changes and preferences",
                "Detail market growth areas and declining sectors",
                "Examine competitive landscape changes"
            ],
            'industry_developments': [
                "What are the major industry developments and announcements?",
                "Analyze regulatory changes and their impact",
                "Identify industry consolidation and partnership trends",
                "Detail changes in industry best practices",
                "Examine industry innovation patterns"
            ]
        }
        return base_queries.get(category, [])

    def generate_report(self, category: str) -> Tuple[str, List[List[str]]]:
        queries = self.generate_research_queries(category)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        markdown_report = f"""# {category.replace('_', ' ').title()} Research Report
Date: {date_str}

## Executive Summary

This report provides a comprehensive analysis of current {category.replace('_', ' ')} trends and developments.

## Table of Contents\n"""
        
        markdown_report += "\n".join([f"- [{query}](#{query.lower().replace(' ', '-')})" for query in queries])
        markdown_report += "\n\n"
        
        csv_data = []
        headers = ["Query", "Response", "Date", "Category"]
        
        for query in queries:
            self.logger.info(f"Researching {category}: {query}")
            response = self.get_ai_response(query, category)
            self.conversation_history[category].append((query, response))
            
            markdown_report += f"## {query}\n\n{response}\n\n"
            csv_data.append([query, response, date_str, category])
            
            # Keep conversation history manageable
            if len(self.conversation_history[category]) > 10:
                self.conversation_history[category].pop(0)
        
        return markdown_report, csv_data

    def save_reports(self, category: str, markdown_content: str, csv_data: List[List[str]]):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Save Markdown report
        markdown_path = self.base_dir / category / 'markdown' / f"{date_str}_{category}_report.md"
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        self.logger.info(f"Markdown report saved to: {markdown_path}")
        
        # Save CSV data
        csv_path = self.base_dir / category / 'csv' / f"{date_str}_{category}_data.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Query", "Response", "Date", "Category"])
            writer.writerows(csv_data)
        self.logger.info(f"CSV data saved to: {csv_path}")

    def research_category(self, category: str):
        try:
            markdown_content, csv_data = self.generate_report(category)
            self.save_reports(category, markdown_content, csv_data)
        except Exception as e:
            self.logger.error(f"Error researching {category}: {str(e)}")

    def schedule_research(self):
        for category, frequency in self.config['update_frequency'].items():
            if frequency.endswith('h'):
                hours = int(frequency[:-1])
                schedule.every(hours).hours.do(self.research_category, category)
            elif frequency.endswith('d'):
                days = int(frequency[:-1])
                schedule.every(days).days.do(self.research_category, category)

    def run(self):
        self.logger.info("Starting Research Agent...")
        self.schedule_research()
        
        # Initial research for all categories
        with ThreadPoolExecutor() as executor:
            executor.map(self.research_category, self.config['research_categories'])
        
        # Continue with scheduled research
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    agent = ResearchAgent()
    agent.run()
