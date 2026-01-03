"""
نظام الاحتياطي عند فشل المكونات
"""

import random
import json
import os
from typing import Dict, Any, Optional
from src.utils import logger
from src.constants import QUESTION_CATEGORIES, ENCOURAGEMENT_PHRASES

class FallbackSystem:
    """نظام الاحتياطي لضمان استمرارية التشغيل"""
    
    def __init__(self):
        self.questions_db = self._load_questions_database()
        self.emergency_assets = self._prepare_emergency_assets()
    
    def _load_questions_database(self) -> Dict[str, list]:
        """تحميل قاعدة بيانات الأسئلة الاحتياطية"""
        questions = {
            "general_knowledge": [
                {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
                {"question": "How many continents are there on Earth?", "answer": "7"},
                {"question": "What is the chemical symbol for gold?", "answer": "Au"},
                {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
                {"question": "What is the fastest land animal?", "answer": "Cheetah"}
            ],
            "culture": [
                {"question": "Which country is known as the Land of the Rising Sun?", "answer": "Japan"},
                {"question": "What is the traditional dress of Scotland called?", "answer": "Kilt"},
                {"question": "Which festival is known as the Festival of Lights in India?", "answer": "Diwali"},
                {"question": "What is the capital of Australia?", "answer": "Canberra"},
                {"question": "Which country gave us the pizza?", "answer": "Italy"}
            ],
            "entertainment": [
                {"question": "Who played Iron Man in the Marvel movies?", "answer": "Robert Downey Jr."},
                {"question": "Which band sang 'Bohemian Rhapsody'?", "answer": "Queen"},
                {"question": "What is the highest-grossing film of all time?", "answer": "Avatar"},
                {"question": "Which TV show features the characters Ross and Rachel?", "answer": "Friends"},
                {"question": "Who is known as the King of Pop?", "answer": "Michael Jackson"}
            ],
            "geography": [
                {"question": "Which river is the longest in the world?", "answer": "Nile River"},
                {"question": "What is the smallest country in the world?", "answer": "Vatican City"},
                {"question": "Which desert is the largest in the world?", "answer": "Sahara Desert"},
                {"question": "What is the capital of Canada?", "answer": "Ottawa"},
                {"question": "Which country has the most islands?", "answer": "Sweden"}
            ],
            "music": [
                {"question": "Who sang 'Shape of You'?", "answer": "Ed Sheeran"},
                {"question": "Which instrument has 88 keys?", "answer": "Piano"},
                {"question": "Who is known as the Queen of Pop?", "answer": "Madonna"},
                {"question": "Which band wrote 'Stairway to Heaven'?", "answer": "Led Zeppelin"},
                {"question": "What is the most streamed song on Spotify?", "answer": "Blinding Lights by The Weeknd"}
            ]
        }
        
        return questions
    
    def _prepare_emergency_assets(self) -> Dict[str, Any]:
        """إعداد الأصول الاحتياطية"""
        return {
            "backgrounds": [
                "#1a237e", "#311b92", "#4a148c", "#880e4f",
                "#b71c1c", "#d84315", "#ff8f00", "#33691e"
            ],
            "audio_available": True,
            "fonts_available": True
        }
    
    def get_question(self, category: Optional[str] = None) -> Dict[str, Any]:
        """الحصول على سؤال من النظام الاحتياطي"""
        if not category:
            category = random.choice(list(self.questions_db.keys()))
        
        if category in self.questions_db and self.questions_db[category]:
            question_data = random.choice(self.questions_db[category])
            
            return {
                "question": question_data["question"],
                "answer": question_data["answer"],
                "category": category,
                "fun_fact": self._get_fun_fact(category, question_data["answer"]),
                "source": "fallback_database"
            }
        
        # استخدم سؤال افتراضي إذا فشل كل شيء
        return self._get_emergency_question()
    
    def _get_fun_fact(self, category: str, answer: str) -> str:
        """الحصول على معلومة مسلية"""
        fun_facts = {
            "general_knowledge": {
                "Jupiter": "Jupiter is so large that all other planets could fit inside it.",
                "7": "The seven continents were once joined together in a supercontinent called Pangaea.",
                "Au": "Gold is so malleable that one ounce can be stretched into a wire 50 miles long."
            },
            "geography": {
                "Nile River": "The Nile River flows through 11 different countries in Africa.",
                "Vatican City": "Vatican City is the smallest country in the world at just 0.17 square miles."
            }
        }
        
        category_facts = fun_facts.get(category, {})
        return category_facts.get(answer, "Interesting fact: This question tests your knowledge!")
    
    def _get_emergency_question(self) -> Dict[str, Any]:
        """الحصول على سؤال طوارئ"""
        emergency_questions = [
            {
                "question": "What is 2 + 2?",
                "answer": "4",
                "category": "math",
                "fun_fact": "In binary, 2 + 2 = 100"
            },
            {
                "question": "What color is the sky on a clear day?",
                "answer": "Blue",
                "category": "science",
                "fun_fact": "The sky appears blue due to Rayleigh scattering of sunlight"
            },
            {
                "question": "How many hours are in a day?",
                "answer": "24",
                "category": "time",
                "fun_fact": "A day on Venus is longer than a year on Venus"
            }
        ]
        
        question = random.choice(emergency_questions)
        question["source"] = "emergency_fallback"
        
        return question
    
    def get_encouragement_phrase(self) -> str:
        """الحصول على عبارة تشجيعية"""
        return random.choice(ENCOURAGEMENT_PHRASES)
    
    def get_simple_background(self, category: str) -> str:
        """إنشاء خلفية بسيطة"""
        colors = self.emergency_assets["backgrounds"]
        color = random.choice(colors)
        
        # في بيئة حقيقية، سيتم إنشاء صورة بهذا اللون
        # هنا نعيد اسم اللون فقط
        return color
    
    def log_fallback_usage(self, component: str, reason: str):
        """تسجيل استخدام النظام الاحتياطي"""
        logger.warning(f"Fallback used for {component}: {reason}")
