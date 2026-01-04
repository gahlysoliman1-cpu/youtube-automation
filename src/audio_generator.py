"""
Audio Generator Module
Generates TTS audio using multiple services with fallback
"""

import os
import logging
from typing import Optional
import requests
from gtts import gTTS
import elevenlabs
from src.config import *

class AudioGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_apis()
        
    def setup_apis(self):
        """Setup TTS API clients"""
        try:
            # ElevenLabs
            if TTS_CONFIG["primary"]["api_key"]:
                elevenlabs.set_api_key(TTS_CONFIG["primary"]["api_key"])
                self.elevenlabs = elevenlabs
            else:
                self.elevenlabs = None
                
            self.logger.info("✅ TTS APIs configured")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up TTS APIs: {e}")
    
    def generate_with_elevenlabs(self, text: str, output_path: str) -> bool:
        """Generate audio using ElevenLabs"""
        if not self.elevenlabs:
            return False
            
        try:
            audio = elevenlabs.generate(
                text=text,
                voice=TTS_CONFIG["primary"]["voice_id"],
                model="eleven_monolingual_v1"
            )
            
            elevenlabs.save(audio, output_path)
            
            if os.path.exists(output_path):
                self.logger.info(f"✅ ElevenLabs audio generated: {output_path}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ ElevenLabs error: {e}")
            return False
    
    def generate_with_gtts(self, text: str, output_path: str) -> bool:
        """Generate audio using gTTS (free)"""
        try:
            tts = gTTS(
                text=text,
                lang=TTS_CONFIG["secondary"]["language"],
                tld=TTS_CONFIG["secondary"]["tld"]
            )
            
            tts.save(output_path)
            
            if os.path.exists(output_path):
                self.logger.info(f"✅ gTTS audio generated: {output_path}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ gTTS error: {e}")
            return False
    
    def generate_silent_audio(self, duration: float, output_path: str) -> bool:
        """Generate silent audio as fallback"""
        try:
            # Using ffmpeg to generate silent audio
            import subprocess
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'anullsrc=r=44100:cl=stereo',
                '-t', str(duration),
                '-c:a', 'libmp3lame',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists(output_path):
                self.logger.info(f"✅ Silent audio generated: {output_path}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error generating silent audio: {e}")
            return False
    
    def generate_with_fallback(self, text: str, output_path: str) -> bool:
        """Generate audio with fallback system"""
        # Try ElevenLabs first
        if self.elevenlabs:
            if self.generate_with_elevenlabs(text, output_path):
                return True
        
        # Try gTTS second
        if self.generate_with_gtts(text, output_path):
            return True
        
        # Last resort: silent audio
        self.logger.warning("⚠️ All TTS failed, using silent audio")
        
        # Calculate approximate duration (words per second)
        word_count = len(text.split())
        estimated_duration = max(3.0, word_count * 0.4)  # ~2.5 words per second
        
        return self.generate_silent_audio(estimated_duration, output_path)
    
    def generate_countdown_audio(self, output_path: str) -> bool:
        """Generate countdown audio"""
        countdown_text = "10, 9, 8, 7, 6, 5, 4, 3, 2, 1"
        return self.generate_with_fallback(countdown_text, output_path)
    
    def validate_audio_file(self, file_path: str) -> bool:
        """Validate audio file exists and has proper format"""
        if not os.path.exists(file_path):
            return False
        
        # Check file size (at least 1KB)
        file_size = os.path.getsize(file_path)
        if file_size < 1024:
            return False
        
        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.m4a', '.ogg']
        if not any(file_path.endswith(ext) for ext in valid_extensions):
            return False
            
        return True
