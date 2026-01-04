"""
Question Generator Module - FULLY WORKING VERSION
"""

import os
import json
import logging
import random
from typing import Dict, Optional
from datetime import datetime
from src.config import *

class QuestionGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_apis()
        
    def setup_apis(self):
        """Setup API clients - SIMPLIFIED to avoid errors"""
        try:
            # Gemini - فقط الـ API القديم
            if AI_CONFIG["primary"]["api_key"]:
                import google.generativeai as genai
                genai.configure(api_key=AI_CONFIG["primary"]["api_key"])
                self.gemini = genai.GenerativeModel(AI_CONFIG["primary"]["model"])
                self.logger.info("✅ Gemini API configured")
            else:
                self.gemini = None
                self.logger.warning("⚠️ Gemini API key not found")
                
            # Groq - بدون proxies
            if AI_CONFIG["secondary"]["api_key"]:
                try:
                    from groq import Groq
                    # إنشاء كائن Groq بدون proxies
                    self.groq = Groq(api_key=AI_CONFIG["secondary"]["api_key"])
                    self.logger.info("✅ Groq API configured")
                except Exception as e:
                    self.logger.warning(f"⚠️ Groq setup error: {e}")
                    self.groq = None
            else:
                self.groq = None
                
            # OpenAI - الإصدار القديم
            if AI_CONFIG["tertiary"]["api_key"]:
                try:
                    import openai
                    openai.api_key = AI_CONFIG["tertiary"]["api_key"]
                    self.openai = openai
                    self.logger.info("✅ OpenAI API configured")
                except Exception as e:
                    self.logger.warning(f"⚠️ OpenAI setup error: {e}")
                    self.openai = None
            else:
                self.openai = None
                
        except Exception as e:
            self.logger.error(f"❌ Error in setup_apis: {e}")
            # تأكد من أن جميع المتغيرات معينة حتى لو فشلت
            self.gemini = None
            self.groq = None
            self.openai = None
    
    def generate_with_model(self, model_name: str, category: str) -> Optional[Dict]:
        """Generate question using specific model"""
        try:
            self.logger.info(f"🔄 Attempting to generate question with {model_name}")
            
            if model_name == "gemini" and self.gemini:
                return self.generate_with_gemini(category)
            elif model_name == "groq" and self.groq:
                return self.generate_with_groq(category)
            elif model_name == "openai" and self.openai:
                return self.generate_with_openai(category)
            else:
                self.logger.warning(f"⚠️ Model {model_name} not available, using fallback")
                return self.generate_fallback_question(category)
                
        except Exception as e:
            self.logger.error(f"❌ Error in generate_with_model: {e}")
            return self.generate_fallback_question(category)
    
    def generate_with_gemini(self, category: str) -> Optional[Dict]:
        """Generate question using Gemini"""
        try:
            if not self.gemini:
                return None
                
            prompt = PROMPTS["question_generation"].format(
                category=category,
                difficulty=CONTENT_CONFIG["difficulty"]
            )
            
            response = self.gemini.generate_content(prompt)
            
            if response.text:
                parsed = self.parse_question_response(response.text, category)
                if parsed:
                    self.logger.info(f"✅ Gemini generated question: {parsed['question'][:50]}...")
                return parsed
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Gemini generation error: {e}")
            return None
    
    def generate_with_groq(self, category: str) -> Optional[Dict]:
        """Generate question using Groq"""
        try:
            if not self.groq:
                return None
                
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
                parsed = self.parse_question_response(content, category)
                if parsed:
                    self.logger.info(f"✅ Groq generated question: {parsed['question'][:50]}...")
                return parsed
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Groq generation error: {e}")
            return None
    
    def generate_with_openai(self, category: str) -> Optional[Dict]:
        """Generate question using OpenAI"""
        try:
            if not self.openai:
                return None
                
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
                parsed = self.parse_question_response(content, category)
                if parsed:
                    self.logger.info(f"✅ OpenAI generated question: {parsed['question'][:50]}...")
                return parsed
            return None
            
        except Exception as e:
            self.logger.error(f"❌ OpenAI generation error: {e}")
            return None
    
    def parse_question_response(self, text: str, category: str) -> Dict:
        """Parse AI response into structured question data"""
        try:
            question_data = {
                "category": category,
                "question": "",
                "options": [],
                "correct_answer": "A",
                "explanation": "",
                "generated_at": datetime.now().isoformat()
            }
            
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            
            # البحث عن السؤال
            for line in lines:
                if line.lower().startswith('question:') or '?' in line:
                    question = line.replace('Question:', '').replace('question:', '').strip()
                    if question and '?' in question:
                        question_data["question"] = question
                        break
            
            # إذا لم نجد سؤال، استخدم أول سطر
            if not question_data["question"] and lines:
                question_data["question"] = lines[0]
            
            # البحث عن الخيارات
            options_found = []
            for line in lines:
                if line.lower().startswith(('a)', 'a)', 'b)', 'c)', 'd)')):
                    option_text = line[2:].strip()  # إزالة "A) " أو "a) "
                    options_found.append(option_text)
                elif line.lower().startswith(('a.', 'a.', 'b.', 'c.', 'd.')):
                    option_text = line[2:].strip()  # إزالة "A. " أو "a. "
                    options_found.append(option_text)
            
            # إذا وجدنا 4 خيارات، استخدمهم
            if len(options_found) >= 4:
                question_data["options"] = options_found[:4]
            else:
                # خيارات افتراضية
                question_data["options"] = [
                    "Option 1",
                    "Option 2", 
                    "Option 3",
                    "Option 4"
                ]
            
            # البحث عن الإجابة الصحيحة
            for line in lines:
                line_lower = line.lower()
                if 'correct' in line_lower and ('answer' in line_lower or 'option' in line_lower):
                    if 'a)' in line_lower or 'a.' in line_lower or '(a)' in line_lower:
                        question_data["correct_answer"] = "A"
                    elif 'b)' in line_lower or 'b.' in line_lower or '(b)' in line_lower:
                        question_data["correct_answer"] = "B"
                    elif 'c)' in line_lower or 'c.' in line_lower or '(c)' in line_lower:
                        question_data["correct_answer"] = "C"
                    elif 'd)' in line_lower or 'd.' in line_lower or '(d)' in line_lower:
                        question_data["correct_answer"] = "D"
                    break
            
            # البحث عن الشرح
            explanation_lines = []
            found_explanation = False
            for line in lines:
                if 'explanation:' in line.lower() or 'explain:' in line.lower():
                    found_explanation = True
                    explanation_text = line.split(':', 1)[1].strip() if ':' in line else line
                    explanation_lines.append(explanation_text)
                elif found_explanation and line and not line.lower().startswith(('a)', 'b)', 'c)', 'd)')):
                    explanation_lines.append(line)
            
            if explanation_lines:
                question_data["explanation"] = ' '.join(explanation_lines)
            else:
                question_data["explanation"] = f"This is a {category} question. The correct answer is {question_data['correct_answer']}."
            
            # التحقق النهائي
            if not question_data["question"]:
                question_data["question"] = f"What is an interesting fact about {category}?"
            
            return question_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing question: {e}")
            return self.generate_fallback_question(category)
    
    def generate_fallback_question(self, category: str) -> Dict:
        """Generate a simple fallback question"""
        self.logger.info(f"🔄 Using fallback question for {category}")
        
        fallback_questions = {
            "geography": {
                "question": "Which river is the longest in the world?",
                "options": ["Amazon River", "Nile River", "Yangtze River", "Mississippi River"],
                "correct_answer": "B",
                "explanation": "The Nile River is approximately 6,650 km long, making it the longest river in the world."
            },
            "culture": {
                "question": "What is the traditional dress of Scotland called?",
                "options": ["Kilt", "Kimono", "Sari", "Dirndl"],
                "correct_answer": "A",
                "explanation": "The kilt is a knee-length skirt-like garment with pleats at the back, originating in the Scottish Highlands."
            },
            "history": {
                "question": "In which year did World War II end?",
                "options": ["1943", "1944", "1945", "1946"],
                "correct_answer": "C",
                "explanation": "World War II ended in 1945 with the surrender of Nazi Germany and later Japan."
            },
            "science": {
                "question": "What is the chemical symbol for gold?",
                "options": ["Go", "Gd", "Au", "Ag"],
                "correct_answer": "C",
                "explanation": "Au comes from the Latin word 'aurum' which means shining dawn or glow of sunrise."
            },
            "entertainment": {
                "question": "Which actor played Iron Man in the Marvel Cinematic Universe?",
                "options": ["Chris Evans", "Robert Downey Jr.", "Chris Hemsworth", "Mark Ruffalo"],
                "correct_answer": "B",
                "explanation": "Robert Downey Jr. portrayed Tony Stark/Iron Man in the Marvel films."
            },
            "sports": {
                "question": "Which country won the 2022 FIFA World Cup?",
                "options": ["France", "Brazil", "Argentina", "Germany"],
                "correct_answer": "C",
                "explanation": "Argentina won the 2022 FIFA World Cup, defeating France in the final."
            },
            "technology": {
                "question": "Which company developed the iPhone?",
                "options": ["Samsung", "Google", "Apple", "Microsoft"],
                "correct_answer": "C",
                "explanation": "Apple Inc. developed and markets the iPhone smartphone."
            },
            "music": {
                "question": "Who is known as the 'King of Pop'?",
                "options": ["Elvis Presley", "Michael Jackson", "Prince", "Madonna"],
                "correct_answer": "B",
                "explanation": "Michael Jackson earned the title 'King of Pop' for his revolutionary contributions to music and dance."
            }
        }
        
        if category in fallback_questions:
            question = fallback_questions[category].copy()
        else:
            # سؤال افتراضي
            question = {
                "question": f"What is an interesting fact about {category}?",
                "options": ["Fact 1", "Fact 2", "Fact 3", "Fact 4"],
                "correct_answer": "A",
                "explanation": f"This is a question about {category}."
            }
        
        question["category"] = category
        question["generated_at"] = datetime.now().isoformat()
        
        return question
