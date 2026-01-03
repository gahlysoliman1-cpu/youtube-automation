"""
مدير نماذج الذكاء الاصطناعي
"""

import random
from typing import Dict, Any, Optional, Tuple
import google.generativeai as genai
from groq import Groq
from openai import OpenAI
from src.config import config
from src.utils import logger
from src.fallback_system import FallbackSystem
from src.constants import QUESTION_CATEGORIES, ENCOURAGEMENT_PHRASES

class AIManager:
    """مدير نماذج الذكاء الاصطناعي"""
    
    def __init__(self):
        self.fallback = FallbackSystem()
        self.initialize_models()
    
    def initialize_models(self):
        """تهيئة نماذج الذكاء الاصطناعي"""
        self.models = {}
        
        # Gemini
        if config.gemini_api_key:
            try:
                genai.configure(api_key=config.gemini_api_key)
                self.models["gemini"] = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini model initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        
        # Groq
        if config.groq_api_key:
            try:
                self.models["groq"] = Groq(api_key=config.groq_api_key)
                logger.info("Groq model initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
        
        # OpenAI
        if config.openai_api_key:
            try:
                self.models["openai"] = OpenAI(api_key=config.openai_api_key)
                logger.info("OpenAI model initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
    
    def generate_question(self) -> Dict[str, Any]:
        """توليد سؤال باستخدام أفضل نموذج متاح"""
        question_data = None
        
        for model_name in ["gemini", "groq", "openai"]:
            if model_name in self.models and question_data is None:
                try:
                    logger.info(f"Generating question using {model_name}")
                    question_data = self._generate_with_model(model_name)
                    if question_data:
                        logger.info(f"Successfully generated question with {model_name}")
                        break
                except Exception as e:
                    logger.error(f"Failed to generate with {model_name}: {e}")
        
        if not question_data:
            logger.warning("All AI models failed, using fallback")
            question_data = self.fallback.get_question()
        
        return question_data
    
    def _generate_with_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """توليد سؤال باستخدام نموذج محدد"""
        category = random.choice(QUESTION_CATEGORIES)
        prompt = self._create_prompt(category)
        
        if model_name == "gemini":
            return self._generate_with_gemini(prompt, category)
        elif model_name == "groq":
            return self._generate_with_groq(prompt, category)
        elif model_name == "openai":
            return self._generate_with_openai(prompt, category)
        
        return None
    
    def _create_prompt(self, category: str) -> str:
        """إنشاء نص prompt للنموذج"""
        category_prompts = {
            "general_knowledge": "Create an interesting general knowledge question",
            "culture": "Create a cultural question about different countries",
            "entertainment": "Create an entertainment question about movies, music, or celebrities",
            "geography": "Create a geography question about countries, flags, or landmarks",
            "music": "Create a music recognition question",
            "history": "Create a historical facts question",
            "science": "Create a science trivia question"
        }
        
        base_prompt = f"""
        Generate a {category} question for a YouTube Shorts quiz.
        
        Requirements:
        1. Question should be engaging and interesting
        2. Answer should be specific and clear
        3. Keep question concise (max 15 words)
        4. Make it suitable for international audience
        5. Include fun fact if possible
        
        Example formats:
        - "Guess which country this flag belongs to?"
        - "Which song does this lyric come from?"
        - "What is the capital of this country?"
        - "Which famous person said this quote?"
        
        Return in JSON format:
        {{
            "question": "The question text here",
            "answer": "The exact answer here",
            "category": "{category}",
            "fun_fact": "Optional interesting fact"
        }}
        """
        
        return base_prompt
    
    def _generate_with_gemini(self, prompt: str, category: str) -> Optional[Dict[str, Any]]:
        """التوليد باستخدام Gemini"""
        try:
            response = self.models["gemini"].generate_content(prompt)
            content = response.text
            
            # استخراج JSON من النص
            import json
            import re
            
            # البحث عن JSON في النص
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                return {
                    "question": data.get("question", ""),
                    "answer": data.get("answer", ""),
                    "category": category,
                    "fun_fact": data.get("fun_fact", ""),
                    "source": "gemini"
                }
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
        
        return None
    
    def _generate_with_groq(self, prompt: str, category: str) -> Optional[Dict[str, Any]]:
        """التوليد باستخدام Groq"""
        try:
            response = self.models["groq"].chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            
            # استخراج JSON من النص
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                return {
                    "question": data.get("question", ""),
                    "answer": data.get("answer", ""),
                    "category": category,
                    "fun_fact": data.get("fun_fact", ""),
                    "source": "groq"
                }
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
        
        return None
    
    def _generate_with_openai(self, prompt: str, category: str) -> Optional[Dict[str, Any]]:
        """التوليد باستخدام OpenAI"""
        try:
            response = self.models["openai"].chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            
            # استخراج JSON من النص
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                return {
                    "question": data.get("question", ""),
                    "answer": data.get("answer", ""),
                    "category": category,
                    "fun_fact": data.get("fun_fact", ""),
                    "source": "openai"
                }
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
        
        return None
    
    def generate_seo_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """توليد بيانات SEO للفيديو"""
        question = question_data.get("question", "")
        category = question_data.get("category", "")
        
        # توليد العنوان
        title = f"{question} 🤔 #shorts #quiz #trivia"
        
        # توليد الوصف
        description = f"""Can you answer this {category} question? 🤔

{question}

Challenge yourself and write your answer in the comments before the timer ends! ⏰

Don't forget to like and subscribe for daily quizzes! 🔔

#shorts #quiz #trivia #challenge #testyourknowledge #{category}"""

        # الهاشتاجات
        hashtags = [
            "#shorts", "#quiz", "#trivia", "#challenge",
            "#testyourknowledge", f"#{category}",
            "#brainteaser", "#puzzle", "#funquiz"
        ]
        
        return {
            "title": title[:100],  # الحد الأقصى 100 حرف
            "description": description[:5000],  # الحد الأقصى 5000 حرف
            "tags": hashtags,
            "category": category
        }
