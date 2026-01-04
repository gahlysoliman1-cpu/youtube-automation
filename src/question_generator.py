"""
Question Generator Module - COMPLETE WORKING VERSION
"""

import os
import json
import logging
import random
import google.generativeai as genai
from groq import Groq
import openai
from typing import Dict, Optional
from datetime import datetime
from src.config import *

class QuestionGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_apis()
        
    def setup_apis(self):
        """Setup API clients for different AI models"""
        try:
            # Gemini - Use ONLY the old API (google.generativeai)
            if AI_CONFIG["primary"]["api_key"]:
                genai.configure(api_key=AI_CONFIG["primary"]["api_key"])
                self.gemini = genai.GenerativeModel(AI_CONFIG["primary"]["model"])
                self.logger.info("✅ Gemini API configured (using legacy api)")
            else:
                self.gemini = None
                
            # Groq
            if AI_CONFIG["secondary"]["api_key"]:
                self.groq = Groq(api_key=AI_CONFIG["secondary"]["api_key"])
                self.logger.info("✅ Groq API configured")
            else:
                self.groq = None
                
            # OpenAI
            if AI_CONFIG["tertiary"]["api_key"]:
                self.openai = openai
                self.openai.api_key = AI_CONFIG["tertiary"]["api_key"]
                self.logger.info("✅ OpenAI API configured")
            else:
                self.openai = None
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up AI APIs: {e}")
            self.gemini = None
            self.groq = None
            self.openai = None
    
    def generate_with_model(self, model_name: str, category: str) -> Optional[Dict]:
        """Generate question using specific model"""
        try:
            if model_name == "gemini":
                return self.generate_with_gemini(category)
            elif model_name == "groq":
                return self.generate_with_groq(category)
            elif model_name == "openai":
                return self.generate_with_openai(category)
            else:
                self.logger.warning(f"Unknown model: {model_name}, using fallback")
                return self.generate_fallback_question(category)
        except Exception as e:
            self.logger.error(f"❌ Error in generate_with_model: {e}")
            return self.generate_fallback_question(category)
    
    def generate_with_gemini(self, category: str) -> Optional[Dict]:
        """Generate question using Gemini"""
        if not self.gemini:
            self.logger.warning("Gemini not configured")
            return None
            
        try:
            prompt = PROMPTS["question_generation"].format(
                category=category,
                difficulty=CONTENT_CONFIG["difficulty"]
            )
            
            response = self.gemini.generate_content(prompt)
            
            if response.text:
                return self.parse_question_response(response.text, category)
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Gemini error: {e}")
            return None
    
    def generate_with_groq(self, category: str) -> Optional[Dict]:
        """Generate question using Groq"""
        if not self.groq:
            self.logger.warning("Groq not configured")
            return None
            
        try:
            prompt = PROMPTS["question_generation"].format(
                category=category,
                difficulty=CONTENT_CONFIG["difficulty"]
            )
            
            response = self.groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a trivia question generator."},
                    {"role": "user", "content": prompt}
                ],
                model=AI_CONFIG["secondary"]["model"],
                temperature=0.7,
                max_tokens=500
            )
            
            if response.choices:
                content = response.choices[0].message.content
                return self.parse_question_response(content, category)
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Groq error: {e}")
            return None
    
    def generate_with_openai(self, category: str) -> Optional[Dict]:
        """Generate question using OpenAI"""
        if not self.openai:
            self.logger.warning("OpenAI not configured")
            return None
            
        try:
            prompt = PROMPTS["question_generation"].format(
                category=category,
                difficulty=CONTENT_CONFIG["difficulty"]
            )
            
            response = self.openai.ChatCompletion.create(
                model=AI_CONFIG["tertiary"]["model"],
                messages=[
                    {"role": "system", "content": "You are a trivia question generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            if response.choices:
                content = response.choices[0].message.content
                return self.parse_question_response(content, category)
            return None
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI error: {e}")
            return None
    
    def parse_question_response(self, text: str, category: str) -> Dict:
        """Parse AI response into structured question data"""
        try:
            lines = text.strip().split('\n')
            question_data = {
                "category": category,
                "question": "",
                "options": [],
                "correct_answer": "",
                "explanation": "",
                "generated_at": datetime.now().isoformat()
            }
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("Question:"):
                    question_data["question"] = line.replace("Question:", "").strip()
                    current_section = "question"
                    
                elif line.startswith("Options:"):
                    current_section = "options"
                    
                elif line.startswith("A)") or line.startswith("B)") or line.startswith("C)") or line.startswith("D)"):
                    if current_section == "options":
                        option = line[3:].strip()
                        question_data["options"].append(option)
                        
                elif line.startswith("Correct Answer:"):
                    answer = line.replace("Correct Answer:", "").strip()
                    question_data["correct_answer"] = answer
                    
                elif line.startswith("Explanation:"):
                    question_data["explanation"] = line.replace("Explanation:", "").strip()
                    current_section = "explanation"
                    
                elif current_section == "explanation" and line:
                    question_data["explanation"] += " " + line
            
            # Validate parsed data
            if not question_data["question"]:
                # Extract question from first non-empty line
                for line in lines:
                    if line and not line.startswith(("Options:", "Correct Answer:", "Explanation:")):
                        question_data["question"] = line.strip()
                        break
            
            # Ensure we have 4 options
            if len(question_data["options"]) != 4:
                question_data["options"] = ["Option A", "Option B", "Option C", "Option D"]
            
            # Ensure we have a correct answer
            if not question_data["correct_answer"]:
                question_data["correct_answer"] = random.choice(["A", "B", "C", "D"])
            
            # Ensure we have an explanation
            if not question_data["explanation"]:
                question_data["explanation"] = f"This is a {category} trivia question."
            
            return question_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing question response: {e}")
            return self.generate_fallback_question(category)
    
    def generate_fallback_question(self, category: str) -> Dict:
        """Generate a simple fallback question"""
        fallback_questions = {
            "geography": {
                "question": "Which river is the longest in the world?",
                "options": ["Amazon River", "Nile River", "Yangtze River", "Mississippi River"],
                "correct_answer": "B",
                "explanation": "The Nile River is approximately 6,650 km long."
            },
            "culture": {
                "question": "What is the traditional dress of Scotland called?",
                "options": ["Kilt", "Kimono", "Sari", "Dirndl"],
                "correct_answer": "A",
                "explanation": "The kilt is a knee-length skirt-like garment with pleats."
            },
            "history": {
                "question": "In which year did World War II end?",
                "options": ["1943", "1944", "1945", "1946"],
                "correct_answer": "C",
                "explanation": "World War II ended in 1945."
            },
            "science": {
                "question": "What is the chemical symbol for gold?",
                "options": ["Go", "Gd", "Au", "Ag"],
                "correct_answer": "C",
                "explanation": "Au comes from the Latin word 'aurum' meaning gold."
            },
            "entertainment": {
                "question": "Which movie won the first Academy Award for Best Picture?",
                "options": ["Wings", "The Broadway Melody", "All Quiet on the Western Front", "Cimarron"],
                "correct_answer": "A",
                "explanation": "Wings won the first Oscar for Best Picture in 1929."
            },
            "sports": {
                "question": "Which country has won the most FIFA World Cups?",
                "options": ["Germany", "Italy", "Argentina", "Brazil"],
                "correct_answer": "D",
                "explanation": "Brazil has won the World Cup 5 times."
            },
            "technology": {
                "question": "What year was the first iPhone released?",
                "options": ["2005", "2006", "2007", "2008"],
                "correct_answer": "C",
                "explanation": "The first iPhone was announced in 2007 by Steve Jobs."
            },
            "music": {
                "question": "Who is known as the 'King of Pop'?",
                "options": ["Elvis Presley", "Michael Jackson", "Prince", "Madonna"],
                "correct_answer": "B",
                "explanation": "Michael Jackson earned this title due to his massive influence on pop music."
            }
        }
        
        if category in fallback_questions:
            question = fallback_questions[category].copy()
            question["category"] = category
            question["generated_at"] = datetime.now().isoformat()
            return question
        else:
            # Default fallback
            return {
                "category": category,
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct_answer": "B",
                "explanation": "Mars appears red due to iron oxide (rust) on its surface.",
                "generated_at": datetime.now().isoformat()
            }
    
    def save_question_to_file(self, question_data: Dict, index: int):
        """Save question data to JSON file"""
        try:
            filename = os.path.join(SHORTS_DIR, f"question_{index}.json")
            with open(filename, 'w') as f:
                json.dump(question_data, f, indent=2)
            self.logger.info(f"✅ Question saved: {filename}")
        except Exception as e:
            self.logger.error(f"❌ Error saving question: {e}")
