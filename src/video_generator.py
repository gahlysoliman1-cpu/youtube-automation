"""
مولد الفيديوهات - نسخة مبسطة بدون OpenCV
"""

import os
from typing import Dict, Any, Optional, Tuple
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    TextClip, ColorClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from src.config import config
from src.utils import logger, validate_file_exists, get_timestamp
from src.constants import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_DURATION,
    QUESTION_DISPLAY_TIME, COUNTDOWN_START,
    ANSWER_DISPLAY_TIME, TEXT_COLOR, TEXT_SHADOW_COLOR,
    OUTPUT_DIR
)

class VideoGenerator:
    """مولد فيديوهات YouTube Shorts"""
    
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def create_short_video(self, content_data: Dict[str, Any], 
                          background_path: str, 
                          audio_path: str,
                          countdown_audio_path: str) -> Optional[str]:
        """إنشاء فيديو Short كامل"""
        try:
            # 1. تحميل الخلفية وتحويلها
            if validate_file_exists(background_path):
                background_clip = ImageClip(background_path, duration=VIDEO_DURATION)
            else:
                # خلفية افتراضية إذا لم توجد
                background_clip = self._create_default_background()
            
            clips = [background_clip]
            timestamp = get_timestamp()
            
            # 2. إضافة نص السؤال
            question_text = content_data["question"]
            question_clip = self._create_text_clip(
                text=question_text,
                duration=QUESTION_DISPLAY_TIME,
                fontsize=70,
                position=("center", "center"),
                is_bold=True
            )
            clips.append(question_clip)
            
            # 3. إعداد العد التنازلي (بدون تأثيرات متقدمة)
            countdown_clip = self._create_simple_countdown(
                start_number=COUNTDOWN_START,
                duration=QUESTION_DISPLAY_TIME,
                position=("center", VIDEO_HEIGHT * 0.7)
            )
            clips.append(countdown_clip)
            
            # 4. إضافة الصوت
            if audio_path and validate_file_exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    if audio_clip.duration > VIDEO_DURATION:
                        audio_clip = audio_clip.subclip(0, VIDEO_DURATION)
                    background_clip = background_clip.set_audio(audio_clip)
                except Exception as e:
                    logger.warning(f"Could not add audio: {e}")
            
            # 5. إضافة الإجابة في النهاية
            if QUESTION_DISPLAY_TIME < VIDEO_DURATION:
                answer_text = content_data["answer"]
                answer_clip = self._create_text_clip(
                    text=f"Answer: {answer_text}",
                    duration=ANSWER_DISPLAY_TIME,
                    fontsize=60,
                    position=("center", "center"),
                    start_time=QUESTION_DISPLAY_TIME,
                    color=(255, 215, 0)  # لون ذهبي للإجابة
                )
                clips.append(answer_clip)
            
            # 6. إنشاء الفيديو النهائي
            final_clip = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
            final_clip = final_clip.set_duration(VIDEO_DURATION)
            
            # 7. حفظ الفيديو
            output_path = os.path.join(OUTPUT_DIR, f"short_{timestamp}.mp4")
            final_clip.write_videofile(
                output_path,
                fps=24,  # تقليل fps لتقليل الحجم
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=f"temp_audio_{timestamp}.m4a",
                remove_temp=True,
                logger=None,
                ffmpeg_params=['-crf', '28']  # ضغط أعلى
            )
            
            logger.info(f"✅ Created short video: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create video: {e}")
            # محاولة نسخة أبسط
            return self._create_simple_video(content_data, timestamp)
    
    def _create_default_background(self):
        """إنشاء خلفية افتراضية"""
        # إنشاء خلفية بلون أزرق متدرج
        from moviepy.editor import ColorClip
        return ColorClip(
            size=(VIDEO_WIDTH, VIDEO_HEIGHT),
            color=(30, 60, 120),
            duration=VIDEO_DURATION
        )
    
    def _create_text_clip(self, text: str, duration: float, fontsize: int,
                         position: Tuple, start_time: float = 0,
                         color: Tuple = TEXT_COLOR, is_bold: bool = False) -> TextClip:
        """إنشاء مقطع نصي بسيط"""
        try:
            # استخدام خط افتراضي
            txt_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font='Arial',
                stroke_color=TEXT_SHADOW_COLOR,
                stroke_width=2,
                method='caption',
                size=(VIDEO_WIDTH * 0.9, None),
                align='center'
            )
            
            txt_clip = txt_clip.set_position(position).set_start(start_time).set_duration(duration)
            return txt_clip
            
        except Exception as e:
            logger.error(f"Failed to create text clip: {e}")
            # بديل بسيط
            return TextClip(
                text,
                fontsize=fontsize,
                color=color,
                size=(VIDEO_WIDTH * 0.9, None),
                align='center'
            ).set_position(position).set_start(start_time).set_duration(duration)
    
    def _create_simple_countdown(self, start_number: int, duration: float,
                               position: Tuple):
        """إنشاء عد تنازلي بسيط"""
        from moviepy.editor import CompositeVideoClip
        
        clips = []
        number_duration = duration / start_number
        
        for i in range(start_number, 0, -1):
            number = str(i)
            fontsize = 100
            
            # تغيير اللون للثواني الأخيرة
            color = TEXT_COLOR if i > 3 else (255, 50, 50)
            
            number_clip = TextClip(
                number,
                fontsize=fontsize,
                color=color,
                font='Arial-Bold'
            ).set_position(position)
            
            start_time = (start_number - i) * number_duration
            number_clip = number_clip.set_start(start_time).set_duration(number_duration)
            clips.append(number_clip)
        
        return CompositeVideoClip(clips)
    
    def _create_simple_video(self, content_data: Dict[str, Any], timestamp: str) -> Optional[str]:
        """إنشاء فيديو بسيط جداً (طوارئ)"""
        try:
            from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
            
            # خلفية ثابتة
            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=(41, 128, 185),
                duration=VIDEO_DURATION
            )
            
            # نص السؤال
            question = TextClip(
                content_data["question"],
                fontsize=60,
                color='white',
                size=(VIDEO_WIDTH * 0.9, None),
                align='center',
                method='caption'
            ).set_position('center').set_duration(QUESTION_DISPLAY_TIME)
            
            # نص الإجابة
            answer = TextClip(
                f"Answer: {content_data['answer']}",
                fontsize=50,
                color='yellow',
                size=(VIDEO_WIDTH * 0.9, None),
                align='center'
            ).set_position('center').set_start(QUESTION_DISPLAY_TIME).set_duration(ANSWER_DISPLAY_TIME)
            
            # دمج
            final = CompositeVideoClip([background, question, answer])
            
            output_path = os.path.join(OUTPUT_DIR, f"emergency_short_{timestamp}.mp4")
            final.write_videofile(
                output_path,
                fps=15,
                codec="libx264",
                audio_codec="aac",
                logger=None
            )
            
            logger.info(f"✅ Emergency video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Emergency video also failed: {e}")
            return None
