"""
مولد الصوت والتسجيلات الصوتية
"""

import os
import tempfile
from typing import Optional, Tuple
from src.config import config
from src.utils import logger, validate_file_exists
from src.constants import AUDIO_DIR
import requests
from elevenlabs import generate, save
from io import BytesIO

class AudioGenerator:
    """مولد الصوت والتسجيلات الصوتية"""
    
    def __init__(self):
        self.fallback_voices = ["google", "system"]
    
    def generate_question_audio(self, question: str, encouragement: str) -> Optional[str]:
        """توليد تسجيل صوتي للسؤال والعبارة التشجيعية"""
        audio_path = None
        
        # محاولة استخدام ElevenLabs أولاً
        if config.eleven_api_key:
            audio_path = self._generate_with_elevenlabs(question, encouragement)
        
        # إذا فشل، حاول باستخدام Camb AI
        if not audio_path and config.camb_ai_key:
            audio_path = self._generate_with_camb_ai(question, encouragement)
        
        # إذا فشل، حاول باستخدام Google TTS
        if not audio_path:
            audio_path = self._generate_with_google_tts(question, encouragement)
        
        # إذا فشل كل شيء، استخدم صوت النظام
        if not audio_path:
            audio_path = self._generate_with_system_tts(question, encouragement)
        
        return audio_path
    
    def _generate_with_elevenlabs(self, question: str, encouragement: str) -> Optional[str]:
        """التوليد باستخدام ElevenLabs"""
        try:
            from elevenlabs import set_api_key
            set_api_key(config.eleven_api_key)
            
            full_text = f"{question}. {encouragement}"
            
            audio = generate(
                text=full_text,
                voice="Rachel",
                model="eleven_monolingual_v1"
            )
            
            audio_path = os.path.join(AUDIO_DIR, f"question_{os.urandom(4).hex()}.mp3")
            save(audio, audio_path)
            
            if validate_file_exists(audio_path):
                logger.info(f"Generated audio with ElevenLabs: {audio_path}")
                return audio_path
        
        except Exception as e:
            logger.error(f"ElevenLabs generation failed: {e}")
        
        return None
    
    def _generate_with_camb_ai(self, question: str, encouragement: str) -> Optional[str]:
        """التوليد باستخدام Camb AI"""
        try:
            full_text = f"{question}. {encouragement}"
            
            url = "https://api.camb.ai/tts"
            headers = {
                "Authorization": f"Bearer {config.camb_ai_key}",
                "Content-Type": "application/json"
            }
            data = {
                "text": full_text,
                "voice_id": "en-US-Wavenet-D",
                "speed": 1.0,
                "pitch": 0.0
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            audio_data = response.content
            audio_path = os.path.join(AUDIO_DIR, f"question_{os.urandom(4).hex()}.mp3")
            
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            
            if validate_file_exists(audio_path):
                logger.info(f"Generated audio with Camb AI: {audio_path}")
                return audio_path
        
        except Exception as e:
            logger.error(f"Camb AI generation failed: {e}")
        
        return None
    
    def _generate_with_google_tts(self, question: str, encouragement: str) -> Optional[str]:
        """التوليد باستخدام Google TTS"""
        try:
            import gtts
            from gtts import gTTS
            
            full_text = f"{question}. {encouragement}"
            
            tts = gTTS(text=full_text, lang='en', slow=False)
            audio_path = os.path.join(AUDIO_DIR, f"question_{os.urandom(4).hex()}.mp3")
            tts.save(audio_path)
            
            if validate_file_exists(audio_path):
                logger.info(f"Generated audio with Google TTS: {audio_path}")
                return audio_path
        
        except Exception as e:
            logger.error(f"Google TTS generation failed: {e}")
        
        return None
    
    def _generate_with_system_tts(self, question: str, encouragement: str) -> Optional[str]:
        """التوليد باستخدام صوت النظام"""
        try:
            import pyttsx3
            
            full_text = f"{question}. {encouragement}"
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'english' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            audio_path = os.path.join(AUDIO_DIR, f"question_{os.urandom(4).hex()}.mp3")
            engine.save_to_file(full_text, audio_path)
            engine.runAndWait()
            
            if validate_file_exists(audio_path):
                logger.info(f"Generated audio with System TTS: {audio_path}")
                return audio_path
        
        except Exception as e:
            logger.error(f"System TTS generation failed: {e}")
        
        return None
    
    def generate_countdown_beep(self, duration: int = 10) -> Optional[str]:
        """توليد صوت عد تنازلي"""
        try:
            import numpy as np
            from scipy.io import wavfile
            import wave
            
            # إنشاء نغمات عد تنازلي
            sample_rate = 44100
            beep_duration = 0.1
            silence_duration = 0.9
            
            audio_data = np.array([], dtype=np.float32)
            
            for i in range(duration, 0, -1):
                # نغمة للرقم
                frequency = 800 if i <= 3 else 600  # نغمة أعلى للـ3 ثواني الأخيرة
                t = np.linspace(0, beep_duration, int(sample_rate * beep_duration), False)
                beep = 0.5 * np.sin(2 * np.pi * frequency * t)
                
                # إضافة النغمة
                audio_data = np.concatenate([audio_data, beep])
                
                # إضافة صمت بين النغمات
                silence = np.zeros(int(sample_rate * silence_duration), dtype=np.float32)
                audio_data = np.concatenate([audio_data, silence])
            
            # نغمة النهاية
            t = np.linspace(0, 0.5, int(sample_rate * 0.5), False)
            end_beep = 0.5 * np.sin(2 * np.pi * 1000 * t)
            audio_data = np.concatenate([audio_data, end_beep])
            
            # حفظ الصوت
            audio_path = os.path.join(AUDIO_DIR, f"countdown_{duration}.wav")
            wavfile.write(audio_path, sample_rate, (audio_data * 32767).astype(np.int16))
            
            logger.info(f"Generated countdown audio: {audio_path}")
            return audio_path
        
        except Exception as e:
            logger.error(f"Countdown generation failed: {e}")
            return None
