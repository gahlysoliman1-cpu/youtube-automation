"""
مولد الفيديوهات
"""

import os
from typing import Dict, Any, Optional, Tuple
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    TextClip, ColorClip, concatenate_videoclips
)
import numpy as np
from src.config import config
from src.utils import logger, validate_file_exists, get_timestamp
from src.constants import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_DURATION,
    QUESTION_DISPLAY_TIME, COUNTDOWN_START,
    ANSWER_DISPLAY_TIME, TEXT_COLOR, TEXT_SHADOW_COLOR,
    FONT_PATH, OUTPUT_DIR
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
            clips = []
            timestamp = get_timestamp()
            
            # 1. تحميل الخلفية
            background_clip = ImageClip(background_path, duration=VIDEO_DURATION)
            clips.append(background_clip)
            
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
            
            # 3. إعداد العد التنازلي
            countdown_clip = self._create_countdown_clip(
                start_number=COUNTDOWN_START,
                duration=QUESTION_DISPLAY_TIME,
                position=("center", VIDEO_HEIGHT * 0.7)
            )
            clips.append(countdown_clip)
            
            # 4. إضافة الصوت
            if audio_path and validate_file_exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                if audio_clip.duration > VIDEO_DURATION:
                    audio_clip = audio_clip.subclip(0, VIDEO_DURATION)
                background_clip = background_clip.set_audio(audio_clip)
            
            # 5. إضافة صوت العد التنازلي
            if countdown_audio_path and validate_file_exists(countdown_audio_path):
                countdown_audio = AudioFileClip(countdown_audio_path)
                # مزامنة صوت العد التنازلي مع المرئي
                background_clip.audio = CompositeAudioClip([
                    background_clip.audio,
                    countdown_audio.set_start(0)
                ])
            
            # 6. إضافة الإجابة في النهاية
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
            
            # 7. إنشاء الفيديو النهائي
            final_clip = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
            final_clip = final_clip.set_duration(VIDEO_DURATION)
            
            # 8. حفظ الفيديو
            output_path = os.path.join(OUTPUT_DIR, f"short_{timestamp}.mp4")
            final_clip.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=f"temp_audio_{timestamp}.m4a",
                remove_temp=True,
                logger=None
            )
            
            logger.info(f"Created short video: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            return None
    
    def _create_text_clip(self, text: str, duration: float, fontsize: int,
                         position: Tuple, start_time: float = 0,
                         color: Tuple = TEXT_COLOR, is_bold: bool = False) -> TextClip:
        """إنشاء مقطع نصي مع تأثيرات"""
        try:
            font = "Arial-Bold" if is_bold else "Arial"
            
            # إنشاء النص الأساسي
            txt_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font=font,
                stroke_color=TEXT_SHADOW_COLOR,
                stroke_width=2,
                method='caption',
                size=(VIDEO_WIDTH * 0.9, None),
                align='center'
            )
            
            # إضافة ظل للنص
            txt_clip = txt_clip.set_position(position).set_start(start_time).set_duration(duration)
            
            # إضافة تأثير ظهور
            txt_clip = txt_clip.crossfadein(0.5)
            
            return txt_clip
            
        except Exception as e:
            logger.error(f"Failed to create text clip: {e}")
            # نسخة احتياطية بدون تأثيرات
            return TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font="Arial",
                size=(VIDEO_WIDTH * 0.9, None),
                align='center'
            ).set_position(position).set_start(start_time).set_duration(duration)
    
    def _create_countdown_clip(self, start_number: int, duration: float,
                              position: Tuple) -> CompositeVideoClip:
        """إنشاء مقطع العد التنازلي"""
        clips = []
        number_duration = duration / start_number
        
        for i in range(start_number, 0, -1):
            number = str(i)
            
            # حجم الخط يتغير مع اقتراب النهاية
            fontsize = 100 if i > 3 else 120
            
            # لون الرقم يتغير مع اقتراب النهاية
            color = TEXT_COLOR if i > 3 else (255, 50, 50)  # أحمر للـ3 ثواني الأخيرة
            
            number_clip = TextClip(
                number,
                fontsize=fontsize,
                color=color,
                font="Arial-Bold",
                stroke_color=TEXT_SHADOW_COLOR,
                stroke_width=3
            ).set_position(position)
            
            # توقيت ظهور الرقم
            start_time = (start_number - i) * number_duration
            number_clip = number_clip.set_start(start_time).set_duration(number_duration)
            
            # تأثير النبض للثواني الأخيرة
            if i <= 3:
                number_clip = number_clip.resize(lambda t: 1 + 0.1 * np.sin(t * 10))
            
            clips.append(number_clip)
        
        return CompositeVideoClip(clips)
    
    def create_long_compilation(self, short_paths: list, output_name: str) -> Optional[str]:
        """إنشاء فيديو طويل يجمع الشورتات"""
        try:
            if len(short_paths) < 2:
                logger.warning("Need at least 2 shorts for compilation")
                return None
            
            clips = []
            
            for i, short_path in enumerate(short_paths):
                if validate_file_exists(short_path):
                    clip = VideoFileClip(short_path)
                    
                    # إضافة عنوان لكل مقطع
                    title_text = f"Quiz {i + 1}"
                    title_clip = TextClip(
                        title_text,
                        fontsize=60,
                        color=TEXT_COLOR,
                        font="Arial-Bold",
                        size=(VIDEO_WIDTH, 100)
                    ).set_position(("center", 50)).set_duration(1)
                    
                    # دمج العنوان مع المقطع
                    combined_clip = CompositeVideoClip([clip, title_clip])
                    clips.append(combined_clip)
                    
                    # إضافة انتقال بين المقاطع
                    if i < len(short_paths) - 1:
                        transition = ColorClip((VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=1)
                        clips.append(transition)
            
            # تجميع كل المقاطع
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # إضافة مقدمة ونهاية
            intro_duration = 3
            intro_text = "Daily Quiz Compilation\nTest Your Knowledge!"
            intro_clip = self._create_text_clip(
                text=intro_text,
                duration=intro_duration,
                fontsize=80,
                position=("center", "center"),
                is_bold=True
            )
            
            outro_duration = 3
            outro_text = "Thanks for Watching!\nSubscribe for Daily Quizzes!"
            outro_clip = self._create_text_clip(
                text=outro_text,
                duration=outro_duration,
                fontsize=80,
                position=("center", "center"),
                is_bold=True
            )
            
            # إنشاء الفيديو النهائي
            final_with_intro = concatenate_videoclips(
                [intro_clip, final_clip, outro_clip],
                method="compose"
            )
            
            # حفظ الفيديو
            output_path = os.path.join(OUTPUT_DIR, f"compilation_{output_name}.mp4")
            final_with_intro.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=f"temp_compilation_audio.m4a",
                remove_temp=True,
                logger=None
            )
            
            logger.info(f"Created compilation video: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create compilation: {e}")
            return None
