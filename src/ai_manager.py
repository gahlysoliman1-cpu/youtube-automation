"""
مدير نماذج الذكاء الاصطناعي - نسخة مُصلحة
"""

import random
import json
import re
from typing import Dict, Any, Optional
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
                import google.generativeai as genai
                genai.configure(api_key=config.gemini_api_key)
                
                # استخدام نموذج Gemini Pro الصحيح
                self.models["gemini"] = {
                    "model": genai.GenerativeModel('gemini-1.0-pro'),
                    "client": genai
                }
                self.available_models.append("gemini")
                logger.info("✅ Gemini model initialized (gemini-1.0-pro)")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                # محاولة نموذج آخر
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=config.gemini_api_key)
                    self.models["gemini"] = {
                        "model": genai.GenerativeModel('gemini-pro'),
                        "client": genai
                    }
                    self.available_models.append("gemini")
                    logger.info("✅ Gemini model initialized (gemini-pro)")
                except Exception as e2:
                    logger.error(f"❌ Failed to initialize Gemini with fallback: {e2}")
        
        # Groq (تعطيل مؤقتاً بسبب مشاكل في التهيئة)
        if False and config.groq_api_key and config.groq_api_key.strip():
            try:
                from groq import Groq
                self.models["groq"] = Groq(api_key=config.groq_api_key)
                self.available_models.append("groq")
                logger.info("✅ Groq model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq: {e}")
        
        # OpenAI (تعطيل مؤقتاً بسبب مشاكل في التهيئة)
        if False and config.openai_api_key and config.openai_api_key.strip():
            try:
                from openai import OpenAI
                self.models["openai"] = OpenAI(api_key=config.openai_api_key)
                self.available_models.append("openai")
                logger.info("✅ OpenAI model initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI: {e}")
        
        # تسجيل النماذج المتاحة
        logger.info(f"📊 Available AI models: {self.available_models}")
        
        # إذا لم تتوفر أي نماذج، استخدم النظام الاحتياطي
        if not self.available_models:
            logger.warning("⚠️ No AI models available, will use fallback only")
    
    def generate_question(self) -> Dict[str, Any]:
        """توليد سؤال باستخدام أفضل نموذج متاح"""
        question_data = None
        
        # محاولة استخدام النماذج المتاحة بالترتيب
        for model_name in self.available_models:
            if question_data:
                break
                
            try:
                logger.info(f"⚡ Generating question using {model_name}")
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
        
        if model_name == "gemini" and "gemini" in self.models:
            return self._generate_with_gemini(category)
        elif model_name == "groq" and "groq" in self.models:
            return self._generate_with_groq(category)
        elif model_name == "openai" and "openai" in self.models:
            return self._generate_with_openai(category)
        
        return None
    
    def _generate_with_gemini(self, category: str) -> Optional[Dict[str, Any]]:
        """التوليد باستخدام Gemini"""
        try:
            # نموذج أكثر بساطة لـ Gemini
            prompt = f"""Create a fun {category} trivia question for a YouTube Short.
            
            The question should be:
            1. Clear and easy to understand
            2. Interesting and engaging
            3. Maximum 15 words
            
            Format your response like this:
            QUESTION: [Your question here?]
            ANSWER: [The correct answer]
            FACT: [An interesting related fact]
            
            Example for geography:
            QUESTION: Which country has the most islands?
            ANSWER: Sweden
            FACT: Sweden has over 267,000 islands!
            
            Now create a {category} question:"""
            
            gemini_model = self.models["gemini"]["model"]
            response = gemini_model.generate_content(prompt)
            content = response.text
            
            # تحليل الاستجابة
            return self._parse_gemini_response(content, category)
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None
    
    def _parse_gemini_response(self, content: str, category: str) -> Optional[Dict[str, Any]]:
        """تحليل استجابة Gemini"""
        try:
            # البحث عن السؤال
            question_match = re.search(r'QUESTION:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            if not question_match:
                question_match = re.search(r'Q:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            
            # البحث عن الإجابة
            answer_match = re.search(r'ANSWER:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            if not answer_match:
                answer_match = re.search(r'A:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            
            # البحث عن الحقيقة
            fact_match = re.search(r'FACT:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            if not fact_match:
                fact_match = re.search(r'Fact:\s*(.*?)(?:\n|$)', content, re.IGNORECASE)
            
            if question_match and answer_match:
                question = question_match.group(1).strip()
                answer = answer_match.group(1).strip()
                fun_fact = fact_match.group(1).strip() if fact_match else ""
                
                # تنظيف النص
                question = self._clean_text(question)
                answer = self._clean_text(answer)
                
                # التأكد من أن السؤال ينتهي بعلامة استفهام
                if not question.endswith('?'):
                    question = question + '?'
                
                return {
                    "question": question,
                    "answer": answer,
                    "category": category,
                    "fun_fact": fun_fact,
                    "source": "gemini"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """تنظيف النص"""
        if not text:
            return ""
        
        # إزالة علامات الاقتباس الزائدة
        text = text.replace('"', '').replace("'", "").strip()
        
        # إزالة النقاط في البداية
        text = re.sub(r'^[\.\-\*\d]+', '', text).strip()
        
        return text
    
    def generate_seo_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """توليد بيانات SEO للفيديو"""
        question = question_data.get("question", "")
        category = question_data.get("category", "")
        
        # تقصير السؤال إذا كان طويلاً
        short_question = question[:60] + "..." if len(question) > 60 else question
        
        # توليد العنوان
        title = f"Can you answer this {category} question? {short_question} #shorts"
        
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
            "tags": hashtags[:20],
            "category": category
        }
