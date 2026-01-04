"""
Fallback System Module
Provides fallback options when primary services fail
"""

import os
import json
import logging
import random
import time
import base64
from typing import Dict, List, Optional, Any
import requests
from src.config import *

class FallbackSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fallback_attempts = {}
        self.setup_fallback_resources()
    
    def setup_fallback_resources(self):
        """Setup fallback resources and templates"""
        self.fallback_questions = self.load_fallback_questions()
        self.fallback_backgrounds = self.load_fallback_backgrounds()
        self.fallback_sounds = self.load_fallback_sounds()
    
    def load_fallback_questions(self) -> Dict:
        """Load fallback questions from template"""
        fallback_file = os.path.join(TEMPLATES_DIR, "fallback_questions.json")
        
        default_questions = {
            "geography": [
                {
                    "question": "Which country has the most islands in the world?",
                    "options": ["Canada", "Sweden", "Indonesia", "Philippines"],
                    "correct_answer": "B",
                    "explanation": "Sweden has over 267,000 islands, though only about 1,000 are inhabited."
                },
                {
                    "question": "What is the largest desert in the world?",
                    "options": ["Sahara", "Arabian", "Gobi", "Antarctic"],
                    "correct_answer": "D",
                    "explanation": "Antarctic Desert is the largest desert in the world."
                }
            ],
            "culture": [
                {
                    "question": "What is the traditional Japanese art of paper folding called?",
                    "options": ["Kirigami", "Origami", "Ikebana", "Sumi-e"],
                    "correct_answer": "B",
                    "explanation": "Origami comes from 'ori' (folding) and 'kami' (paper)."
                }
            ],
            "history": [
                {
                    "question": "Who was the first woman to win a Nobel Prize?",
                    "options": ["Marie Curie", "Rosalind Franklin", "Dorothy Hodgkin", "Maria Goeppert-Mayer"],
                    "correct_answer": "A",
                    "explanation": "Marie Curie won the Nobel Prize in Physics in 1903."
                }
            ],
            "science": [
                {
                    "question": "What is the hardest natural substance on Earth?",
                    "options": ["Gold", "Iron", "Diamond", "Platinum"],
                    "correct_answer": "C",
                    "explanation": "Diamond has a hardness of 10 on the Mohs scale."
                }
            ],
            "entertainment": [
                {
                    "question": "Which movie won the first Academy Award for Best Picture?",
                    "options": ["Wings", "The Broadway Melody", "All Quiet on the Western Front", "Cimarron"],
                    "correct_answer": "A",
                    "explanation": "Wings won the first Oscar for Best Picture in 1929."
                }
            ],
            "sports": [
                {
                    "question": "Which country has won the most FIFA World Cups?",
                    "options": ["Germany", "Italy", "Argentina", "Brazil"],
                    "correct_answer": "D",
                    "explanation": "Brazil has won the World Cup 5 times (1958, 1962, 1970, 1994, 2002)."
                }
            ],
            "technology": [
                {
                    "question": "What year was the first iPhone released?",
                    "options": ["2005", "2006", "2007", "2008"],
                    "correct_answer": "C",
                    "explanation": "The first iPhone was announced in 2007 by Steve Jobs."
                }
            ],
            "music": [
                {
                    "question": "Who is known as the 'King of Pop'?",
                    "options": ["Elvis Presley", "Michael Jackson", "Prince", "Madonna"],
                    "correct_answer": "B",
                    "explanation": "Michael Jackson earned this title due to his massive influence on pop music."
                }
            ]
        }
        
        try:
            if os.path.exists(fallback_file):
                with open(fallback_file, 'r') as f:
                    return json.load(f)
            else:
                # Save default questions
                os.makedirs(TEMPLATES_DIR, exist_ok=True)
                with open(fallback_file, 'w') as f:
                    json.dump(default_questions, f, indent=2)
                return default_questions
        except Exception as e:
            self.logger.error(f"Error loading fallback questions: {e}")
            return default_questions
    
    def load_fallback_backgrounds(self) -> List[Dict]:
        """Load fallback backgrounds"""
        return [
            {"type": "gradient", "colors": ["#667eea", "#764ba2"]},
            {"type": "gradient", "colors": ["#f093fb", "#f5576c"]},
            {"type": "gradient", "colors": ["#4facfe", "#00f2fe"]},
            {"type": "gradient", "colors": ["#43e97b", "#38f9d7"]},
            {"type": "gradient", "colors": ["#fa709a", "#fee140"]},
            {"type": "gradient", "colors": ["#30cfd0", "#330867"]},
            {"type": "solid", "color": "#1a1a2e"},
            {"type": "solid", "color": "#16213e"},
            {"type": "solid", "color": "#0f3460"},
            {"type": "solid", "color": "#1b262c"}
        ]
    
    def load_fallback_sounds(self) -> List[str]:
        """Load fallback sound paths"""
        # Return empty list - we'll generate silent audio programmatically
        return []
    
    def get_fallback_question(self, category: str) -> Optional[Dict]:
        """Get a random fallback question for a category"""
        if category in self.fallback_questions and self.fallback_questions[category]:
            question = random.choice(self.fallback_questions[category])
            question["category"] = category
            question["is_fallback"] = True
            return question
        return None
    
    def get_fallback_background(self) -> Dict:
        """Get a random fallback background"""
        return random.choice(self.fallback_backgrounds)
    
    def get_silent_audio_base64(self, duration: float = 3.0) -> str:
        """Generate base64 encoded silent audio"""
        # Create silent WAV data (44.1kHz, 16-bit, stereo)
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        
        # Create silent audio data (zeros)
        # This is a simplified version - in production, use a proper WAV generator
        silent_data = bytes([0] * (num_samples * 4))  # 2 channels * 2 bytes per sample
        
        # Encode to base64
        encoded = base64.b64encode(silent_data).decode('utf-8')
        
        # Create data URL
        return f"data:audio/wav;base64,{encoded}"
    
    def track_failure(self, service_name: str, error: str):
        """Track service failures for monitoring"""
        if service_name not in self.fallback_attempts:
            self.fallback_attempts[service_name] = []
        
        self.fallback_attempts[service_name].append({
            "timestamp": time.time(),
            "error": error
        })
        
        # Keep only last 10 failures per service
        if len(self.fallback_attempts[service_name]) > 10:
            self.fallback_attempts[service_name] = self.fallback_attempts[service_name][-10:]
        
        self.logger.warning(f"Service failure tracked: {service_name} - {error}")
    
    def should_use_fallback(self, service_name: str) -> bool:
        """Check if we should use fallback for a service"""
        if service_name not in self.fallback_attempts:
            return False
        
        failures = self.fallback_attempts[service_name]
        
        # Check failures in last hour
        recent_failures = [
            f for f in failures 
            if time.time() - f["timestamp"] < 3600
        ]
        
        return len(recent_failures) >= 3
    
    def get_service_status(self) -> Dict:
        """Get status of all services"""
        status = {}
        
        for service in ['gemini', 'groq', 'openai', 'elevenlabs', 'youtube']:
            if service in self.fallback_attempts:
                failures = self.fallback_attempts[service]
                recent = [f for f in failures if time.time() - f["timestamp"] < 3600]
                status[service] = {
                    "total_failures": len(failures),
                    "recent_failures": len(recent),
                    "healthy": len(recent) < 3
                }
            else:
                status[service] = {
                    "total_failures": 0,
                    "recent_failures": 0,
                    "healthy": True
                }
        
        return status
    
    def create_minimal_video_fallback(self, question_data: Dict, output_path: str) -> bool:
        """Create minimal video as ultimate fallback"""
        try:
            self.logger.info("🚨 Using ultimate fallback: creating minimal video")
            
            # Create a simple text-based video using ffmpeg
            question_text = question_data["question"]
            
            # Escape text for ffmpeg
            safe_text = question_text.replace("'", "'\\''").replace('"', '\\"')
            
            # Create video using ffmpeg
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=blue:s={VIDEO_CONFIG["short"]["resolution"][0]}x{VIDEO_CONFIG["short"]["resolution"][1]}:d=15',
                '-vf', f"drawtext=text='{safe_text}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2",
                '-c:v', 'libx264',
                '-t', '15',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"✅ Minimal fallback video created: {output_path}")
                return True
            else:
                self.logger.error(f"❌ Fallback video creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in ultimate fallback: {e}")
            return False
