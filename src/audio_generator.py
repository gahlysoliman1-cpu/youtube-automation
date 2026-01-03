"""
مولد الصوت والتسجيلات الصوتية - مُصلح
"""

import os
import tempfile
from typing import Optional
from src.config import config
from src.utils import logger, validate_file_exists
from src.constants import AUDIO_DIR
import requests

class AudioGenerator:
    """مولد الصوت والتسجيلات الصوتية"""
    
    def __init__(self):
        self.fallback_voices = ["google", "system"]
    
    def generate_question_audio(self, question: str, encouragement: str) -> Optional[str]:
        """توليد تسجيل صوتي للسؤال والعبارة التشجيعية"""
        audio_path = None
        
        # محاولة استخدام ElevenLabs أولاً (باستخدام نموذج مجاني)
        if config.eleven_api_key:
            audio_path = self._generate_with_elevenlabs_free(question, encouragement)
        
        # إذا فشل، حاول باستخدام Google TTS
        if not audio_path:
            audio_path = self._generate_with_google_tts(question, encouragement)
        
        return audio_path
    
    def _generate_with_elevenlabs_free(self, question: str, encouragement: str) -> Optional[str]:
        """التوليد باستخدام ElevenLabs (نموذج مجاني)"""
        try:
            from elevenlabs import generate, save, set_api_key
            
            set_api_key(config.eleven_api_key)
            
            full_text = f"{question}. {encouragement}"
            
            # استخدام نموذج مجاني
            audio = generate(
                text=full_text,
                voice="Rachel",
                model="eleven_multilingual_v2"  # نموذج مجاني
            )
            
            audio_path = os.path.join(AUDIO_DIR, f"question_{os.urandom(4).hex()}.mp3")
            save(audio, audio_path)
            
            if validate_file_exists(audio_path):
                logger.info(f"✅ Generated audio with ElevenLabs: {audio_path}")
                return audio_path
        
        except Exception as e:
            logger.error(f"❌ ElevenLabs generation failed: {e}")
        
        return None
    
    def _generate_with_google_tts(self, question: str, encouragement: str) -> Optional[str]:
        """التوليد باستخدام Google TTS"""
        try:
            from gtts import gTTS
            
            full_text = f"{question}. {encouragement}"
            
            tts = gTTS(text=full_text, lang='en', slow=False)
            audio_path = os.path.join(AUDIO_DIR, f"question_{os.urandom(4).hex()}.mp3")
            tts.save(audio_path)
            
            if validate_file_exists(audio_path):
                logger.info(f"✅ Generated audio with Google TTS: {audio_path}")
                return audio_path
        
        except Exception as e:
            logger.error(f"❌ Google TTS generation failed: {e}")
        
        return None
    
    def generate_countdown_beep(self, duration: int = 10) -> Optional[str]:
        """توليد صوت عد تنازلي باستخدام scipy"""
        try:
            import numpy as np
            from scipy.io import wavfile
            
            audio_path = os.path.join(AUDIO_DIR, f"countdown_{duration}.wav")
            
            # إذا كان الملف موجوداً بالفعل، نستخدمه
            if os.path.exists(audio_path):
                return audio_path
            
            sample_rate = 22050  # تقليل معدل العينة لتقليل الحجم
            beep_duration = 0.3
            silence_duration = 0.7
            
            audio_data = np.array([], dtype=np.float32)
            
            for i in range(duration, 0, -1):
                # تردد مختلف للثواني الأخيرة
                frequency = 800 if i <= 3 else 600
                
                # إنشاء نغمة
                t = np.linspace(0, beep_duration, int(sample_rate * beep_duration), False)
                beep = 0.3 * np.sin(2 * np.pi * frequency * t)
                
                # إضافة النغمة
                audio_data = np.concatenate([audio_data, beep])
                
                # إضافة صمت (إلا للثانية الأخيرة)
                if i > 1:
                    silence = np.zeros(int(sample_rate * silence_duration), dtype=np.float32)
                    audio_data = np.concatenate([audio_data, silence])
            
            # نغمة النهاية
            t = np.linspace(0, 0.5, int(sample_rate * 0.5), False)
            end_beep = 0.3 * np.sin(2 * np.pi * 1000 * t)
            audio_data = np.concatenate([audio_data, end_beep])
            
            # تحويل إلى 16-bit PCM
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            
            # حفظ كـ WAV
            wavfile.write(audio_path, sample_rate, audio_data_int16)
            
            logger.info(f"✅ Generated countdown audio: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ Countdown generation failed: {e}")
            # إنشاء ملف صوتي فارغ كبديل
            audio_path = os.path.join(AUDIO_DIR, f"silent_{duration}.wav")
            with open(audio_path, 'wb') as f:
                f.write(b'')  # ملف فارغ
            return audio_path
