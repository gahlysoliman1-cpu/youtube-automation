"""
Question Generator Module - FIXED VERSION
"""

import os
import json
import logging
import random
from typing import Dict, Optional
import google.generativeai as genai  # Keep legacy for now
try:
    import google.genai as genai_new
    GENAI_NEW_AVAILABLE = True
except:
    GENAI_NEW_AVAILABLE = False
from groq import Groq
import openai
from src.config import *

class QuestionGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_apis()
        
    def setup_apis(self):
        """Setup API clients for different AI models"""
        try:
            # Gemini - try new version first
            if GENAI_NEW_AVAILABLE and AI_CONFIG["primary"]["api_key"]:
                self.gemini_new = genai_new
                genai_new.configure(api_key=AI_CONFIG["primary"]["api_key"])
                self.gemini = None
                self.logger.info("✅ Using new google-genai package")
            elif AI_CONFIG["primary"]["api_key"]:
                # Fallback to old version
                genai.configure(api_key=AI_CONFIG["primary"]["api_key"])
                self.gemini = genai.GenerativeModel(AI_CONFIG["primary"]["model"])
                self.gemini_new = None
                self.logger.info("✅ Using legacy google-generativeai package")
            else:
                self.gemini = None
                self.gemini_new = None
                
            # Groq
            if AI_CONFIG["secondary"]["api_key"]:
                self.groq = Groq(api_key=AI_CONFIG["secondary"]["api_key"])
            else:
                self.groq = None
                
            # OpenAI
            if AI_CONFIG["tertiary"]["api_key"]:
                self.openai = openai
            else:
                self.openai = None
                
            self.logger.info("✅ AI APIs configured")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up AI APIs: {e}")
            # Setup fallbacks
            self.gemini = None
            self.gemini_new = None
            self.groq = None
            self.openai = None
    
    def generate_with_gemini(self, category: str) -> Optional[Dict]:
        """Generate question using Gemini (both old and new versions)"""
        # Try new API first
        if self.gemini_new:
            try:
                client = genai_new.Client(api_key=AI_CONFIG["primary"]["api_key"])
                prompt = PROMPTS["question_generation"].format(
                    category=category,
                    difficulty=CONTENT_CONFIG["difficulty"]
                )
                
                response = client.models.generate_content(
                    model=AI_CONFIG["primary"]["model"],
                    contents=prompt
                )
                
                if response.text:
                    return self.parse_question_response(response.text, category)
                return None
                
            except Exception as e:
                self.logger.error(f"❌ New Gemini API error: {e}")
        
        # Try old API
        if self.gemini:
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
                self.logger.error(f"❌ Old Gemini API error: {e}")
        
        return None
    
    # بقية الدوال تبقى كما هي بدون تغيير...
    # generate_with_groq, generate_with_openai, parse_question_response, etc.
    # ... (نفس الكود السابق)
