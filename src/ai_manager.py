"""
مدير نماذج الذكاء الاصطناعي - نسخة معدلة
"""

import random
import json
import re
from typing import Dict, Any, Optional
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
        self.models = {}
        self.available_models = []
        self.initialize_models()
    
    def initialize_models(self):
        """تهيئة نماذج الذكاء الاصطناعي المتاحة"""
        # Gemini
        if config.gemini_api_key and config.gemini_api_key.strip():
            try:
                genai.configure(api_key=config.gemini_api_key)
                self.models["gemini"] = genai.GenerativeModel('gemini-pro')
                self.available_models.append("gemini")
                logger.info("✅ Gemini model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
        
        # Groq
        if config.groq_api_key and config.groq_api_key.strip():
            try:
                self.models["groq"] = Groq(api_key=config.groq_api_key)
                self.available_models.append("groq")
                logger.info("✅ Groq model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq: {e}")
        
        # OpenAI
        if config.openai_api_key and config.openai_api_key.strip():
            try:
                self.models["openai"] = OpenAI(api_key=config.openai_api_key)
                self.available_models.append("openai")
                logger.info("✅ OpenAI model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI: {e}")
        
        # تسجيل النماذج المتاحة
        logger.info(f"Available AI models: {self.available_models}")
    
    def generate_question(self) -> Dict[str, Any]:
        """توليد سؤال باستخدام أفضل نموذج متاح"""
        question_data = None
        
        # محاولة استخدام النماذج المتاحة بالترتيب
        for model_name in self.available_models:
            if question_data:
                break
                
            try:
                logger.info(f"Generating question using {model_name}")
                question_data = self._generate_with_model(model_name)
                if question_data:
                    logger.info(f"✅ Successfully generated question with {model_name}")
                    break
            except Exception as e:
                logger.error(f"❌ Failed to generate with {model_name}: {e}")
        
        # استخدام النظام الاحتياطي إذا فشلت جميع النماذج
        if not question_data:
            logger.warning("⚠️ All AI models failed, using fallback")
            question_data = self.fallback.get_question()
            question_data["source"] = "fallback"
        
        return question_data
    
    def _generate_with_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """توليد سؤال باستخدام نموذج محدد"""
        category = random.choice(QUESTION_CATEGORIES)
        
        if model_name == "gemini":
            return self._generate_with_gemini(category)
        elif model_name == "groq":
            return self._generate_with_groq(category)
        elif model_name == "openai":
            return self._generate_with_openai(category)
        
        return None
    
    def _generate_with_gemini(self, category: str) -> Optional[Dict[str, Any]]:
        """التوليد باستخدام Gemini"""
        try:
            prompt = f"""Generate a {category} quiz question for YouTube Shorts.
            
            Format: Q: [question]
            A: [answer]
            
            Rules:
            1. Question must be engaging and interesting
            2. Answer should be specific and clear
            3. Question length: 10-15 words max
            4. Include a fun fact if possible
            5. Make it suitable for international audience
            
            Example for geography:
            Q: Guess which country this flag belongs to? 🇯🇵
            A: Japan
            Fun fact: Japan has over 6,800 islands
            
            Now generate a {category} question:"""
            
            response = self.models["gemini"].generate_content(prompt)
            content = response.text
            
            # تحليل الاستجابة
            return self._parse_ai_response(content, category, "gemini")
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None
    
    def _generate_with_groq(self, category: str) -> Optional[Dict[str, Any]]:
        """التوليد باستخدام Groq"""
        try:
            prompt = f"""Generate a {category} quiz question for YouTube Shorts in this exact format:
            
            Q: [Your question here?]
            A: [Exact answer here]
            Fact: [Optional fun fact]
            
            Make the question fun and engaging. Keep it under 15 words."""
            
            response = self.models["groq"].chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            content = response.choices[0].message.content
            
            return self._parse_ai_response(content, category, "groq")
            
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return None
    
    def _generate_with_openai(self, category: str) -> Optional[Dict[str, Any]]:
        """التوليد باستخدام OpenAI"""
        try:
            prompt = f"""Create a {category} question for YouTube Shorts quiz.
            
            Requirements:
            - Question format: Start with "Q: "
            - Answer format: Start with "A: "
            - Optional fun fact: Start with "Fact: "
            - Question should be catchy and short
            - Answer should be precise
            
            Generate now:"""
            
            response = self.models["openai"].chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            content = response.choices[0].message.content
            
            return self._parse_ai_response(content, category, "openai")
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return None
    
    def _parse_ai_response(self, content: str, category: str, source: str) -> Optional[Dict[str, Any]]:
        """تحليل استجابة الذكاء الاصطناعي"""
        try:
            # استخراج السؤال
            question_match = re.search(r'Q:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            if not question_match:
                question_match = re.search(r'Question:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            
            # استخراج الإجابة
            answer_match = re.search(r'A:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            if not answer_match:
                answer_match = re.search(r'Answer:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            
            # استخراج المعلومة المسلية
            fact_match = re.search(r'Fact:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            
            if question_match and answer_match:
                question = question_match.group(1).strip()
                answer = answer_match.group(1).strip()
                fun_fact = fact_match.group(1).strip() if fact_match else ""
                
                # تنظيف النص
                question = question.replace('"', '').replace("'", "")
                answer = answer.replace('"', '').replace("'", "")
                
                return {
                    "question": question,
                    "answer": answer,
                    "category": category,
                    "fun_fact": fun_fact,
                    "source": source
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return None
    
    def generate_seo_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """توليد بيانات SEO للفيديو"""
        question = question_data.get("question", "")
        category = question_data.get("category", "")
        
        # توليد العنوان (مختصر)
        title = f"{question[:50]}... #shorts" if len(question) > 50 else f"{question} #shorts"
        
        # توليد الوصف
        description = f"""Can you answer this {category} question? 🤔

{question}

💡 Challenge: Write your answer in comments before the timer ends!

🔔 Subscribe for daily quizzes!
▶️ Watch our other shorts
👍 Like if you enjoy quizzes

#shorts #quiz #trivia #challenge #{category} #funquiz"""
        
        # الهاشتاجات
        hashtags = [
            "#shorts", "#quiz", "#trivia", "#challenge",
            "#testyourknowledge", f"#{category}",
            "#brainteaser", "#puzzle", "#funquiz",
            "#youtubeshorts", "#shortvideo"
        ]
        
        return {
            "title": title[:100],
            "description": description[:5000],
            "tags": hashtags[:20],  # YouTube allows max 20 tags
            "category": category
        }
