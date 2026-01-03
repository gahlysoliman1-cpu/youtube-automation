"""
مولد الأسئلة والمحتوى
"""

import random
from typing import Dict, Any, List
from src.ai_manager import AIManager
from src.utils import logger, generate_unique_id
from src.fallback_system import FallbackSystem
from src.constants import ENCOURAGEMENT_PHRASES

class QuestionGenerator:
    """مولد الأسئلة والمحتوى"""
    
    def __init__(self):
        self.ai_manager = AIManager()
        self.fallback = FallbackSystem()
        self.generated_questions = set()
    
    def generate_quiz_content(self) -> Dict[str, Any]:
        """توليد محتوى كامل للاختبار"""
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                # توليد السؤال باستخدام AI
                question_data = self.ai_manager.generate_question()
                
                if not question_data:
                    logger.warning("AI generation failed, using fallback")
                    question_data = self.fallback.get_question()
                
                # التحقق من عدم التكرار
                question_hash = generate_unique_id(
                    question_data.get("question", "") + 
                    question_data.get("answer", "")
                )
                
                if question_hash in self.generated_questions:
                    logger.info(f"Duplicate question detected, retrying...")
                    continue
                
                self.generated_questions.add(question_hash)
                
                # توليد بيانات SEO
                seo_data = self.ai_manager.generate_seo_data(question_data)
                
                # اختيار عبارة تشجيعية عشوائية
                encouragement = random.choice(ENCOURAGEMENT_PHRASES)
                
                # تجميع البيانات
                content_data = {
                    "id": question_hash,
                    "question": question_data.get("question", ""),
                    "answer": question_data.get("answer", ""),
                    "category": question_data.get("category", ""),
                    "fun_fact": question_data.get("fun_fact", ""),
                    "encouragement": encouragement,
                    "seo": seo_data,
                    "timestamp": generate_unique_id(str(random.random())),
                    "source": question_data.get("source", "fallback")
                }
                
                logger.info(f"Generated content: {content_data['question'][:50]}...")
                return content_data
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    logger.error("All attempts failed, using emergency fallback")
                    return self._get_emergency_content()
        
        return self._get_emergency_content()
    
    def _get_emergency_content(self) -> Dict[str, Any]:
        """الحصول على محتوى طوارئ عند فشل كل المحاولات"""
        emergency_questions = [
            {
                "question": "Guess which country this flag belongs to? 🇺🇸",
                "answer": "United States of America",
                "category": "geography",
                "fun_fact": "The US flag has 50 stars representing 50 states"
            },
            {
                "question": "Which planet is known as the Red Planet? 🔴",
                "answer": "Mars",
                "category": "science",
                "fun_fact": "Mars has the largest volcano in the solar system"
            },
            {
                "question": "What is the capital of France? 🇫🇷",
                "answer": "Paris",
                "category": "geography",
                "fun_fact": "Paris is called the 'City of Light'"
            }
        ]
        
        question = random.choice(emergency_questions)
        encouragement = random.choice(ENCOURAGEMENT_PHRASES)
        
        return {
            "id": generate_unique_id(question["question"]),
            "question": question["question"],
            "answer": question["answer"],
            "category": question["category"],
            "fun_fact": question.get("fun_fact", ""),
            "encouragement": encouragement,
            "seo": {
                "title": f"{question['question']} #shorts #quiz",
                "description": f"Can you answer this {question['category']} question? {question['question']}",
                "tags": ["#shorts", "#quiz", "#trivia", f"#{question['category']}"],
                "category": question["category"]
            },
            "timestamp": generate_unique_id(str(random.random())),
            "source": "emergency_fallback"
        }
