"""
مولد الفيديوهات - نسخة مُصلحة
"""

import os
from typing import Dict, Any, Optional, Tuple
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    TextClip, ColorClip, concatenate_videoclips
)
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
        self.font_path = self._get_font_path()
    
    def _get_font_path(self):
        """الحصول على مسار الخط"""
        # محاولة العثور على خط Arial أو استخدام خط افتراضي
        possible_fonts = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "arial.ttf",
            "Arial.ttf"
        ]
        
        for font in possible_fonts:
            if os.path.exists(font):
                return font
        
        # إذا لم يتم العثور على أي خط، استخدم None (سيستخدم MoviePy الخط الافتراضي)
        return None
    
    def create_short_video(self, content_data: Dict[str, Any], 
                          background_path: str, 
                          audio_path: str,
                          countdown_audio_path: str) -> Optional[str]:
        """إنشاء فيديو Short كامل"""
        try:
            timestamp = get_timestamp()
            
            # 1. تحميل الخلفية
            if validate_file_exists(background_path):
                background_clip = ImageClip(background_path, duration=VIDEO_DURATION)
            else:
                # خلفية افتراضية
                background_clip = ColorClip(
                    size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                    color=(30, 60, 120),
                    duration=VIDEO_DURATION
                )
            
            clips = [background_clip]
            
            # 2. إضافة نص السؤال
            question_text = content_data["question"]
            question_clip = self._create_text_clip_simple(
                text=question_text,
                duration=QUESTION_DISPLAY_TIME,
                fontsize=70,
                position=("center", "center"),
                is_bold=True
            )
            if question_clip:
                clips.append(question_clip)
            
            # 3. إعداد العد التنازلي البسيط
            countdown_clip = self._create_simple_countdown(
                start_number=COUNTDOWN_START,
                duration=QUESTION_DISPLAY_TIME,
                position=("center", VIDEO_HEIGHT * 0.7)
            )
            if countdown_clip:
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
                answer_clip = self._create_text_clip_simple(
                    text=f"Answer: {answer_text}",
                    duration=ANSWER_DISPLAY_TIME,
                    fontsize=60,
                    position=("center", "center"),
                    start_time=QUESTION_DISPLAY_TIME,
                    color=(255, 215, 0)  # لون ذهبي للإجابة
                )
                if answer_clip:
                    clips.append(answer_clip)
            
            # 6. إنشاء الفيديو النهائي
            final_clip = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
            final_clip = final_clip.set_duration(VIDEO_DURATION)
            
            # 7. حفظ الفيديو
            output_path = os.path.join(OUTPUT_DIR, f"short_{timestamp}.mp4")
            
            # إعدادات تصدير بسيطة
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=f"temp_audio_{timestamp}.m4a",
                remove_temp=True,
                logger=None,
                ffmpeg_params=['-crf', '28', '-preset', 'fast']
            )
            
            logger.info(f"✅ Created short video: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create video: {e}")
            # محاولة نسخة أبسط
            return self._create_emergency_video(content_data)
    
    def _create_text_clip_simple(self, text: str, duration: float, fontsize: int,
                               position: Tuple, start_time: float = 0,
                               color: Tuple = TEXT_COLOR, is_bold: bool = False) -> Optional[TextClip]:
        """إنشاء مقطع نصي بسيط"""
        try:
            # استخدام اسم الخط بدلاً من المسار لتجنب المشاكل
            font_name = "Arial-Bold" if is_bold else "Arial"
            
            txt_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font=font_name,  # استخدام اسم الخط بدلاً من المسار
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
            try:
                # محاولة بدون تحديد الخط
                txt_clip = TextClip(
                    text,
                    fontsize=fontsize,
                    color=color,
                    stroke_color=TEXT_SHADOW_COLOR,
                    stroke_width=2,
                    method='caption',
                    size=(VIDEO_WIDTH * 0.9, None),
                    align='center'
                )
                
                txt_clip = txt_clip.set_position(position).set_start(start_time).set_duration(duration)
                return txt_clip
            except Exception as e2:
                logger.error(f"Failed to create text clip without font: {e2}")
                return None
    
    def _create_simple_countdown(self, start_number: int, duration: float,
                               position: Tuple) -> Optional[CompositeVideoClip]:
        """إنشاء عد تنازلي بسيط"""
        try:
            from moviepy.editor import CompositeVideoClip, TextClip
            
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
                    font='Arial-Bold' if self.font_path else None
                ).set_position(position)
                
                start_time = (start_number - i) * number_duration
                number_clip = number_clip.set_start(start_time).set_duration(number_duration)
                clips.append(number_clip)
            
            return CompositeVideoClip(clips)
            
        except Exception as e:
            logger.error(f"Failed to create countdown: {e}")
            return None
    
    def _create_emergency_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """إنشاء فيديو طوارئ بسيط جداً"""
        try:
            timestamp = get_timestamp()
            
            # استخدام PIL لإنشاء إطار ثابت
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # إنشاء صورة ثابتة
            img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color=(41, 128, 185))
            draw = ImageDraw.Draw(img)
            
            # محاولة إضافة نص
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            # تقسيم النص للسؤال
            question = content_data["question"]
            answer = content_data["answer"]
            
            # رسم السؤال
            question_lines = self._split_text(question, 30)
            for i, line in enumerate(question_lines):
                draw.text(
                    (VIDEO_WIDTH//2, VIDEO_HEIGHT//2 - 100 + i*70),
                    line,
                    fill='white',
                    font=font,
                    anchor='mm'
                )
            
            # رسم الإجابة
            draw.text(
                (VIDEO_WIDTH//2, VIDEO_HEIGHT//2 + 100),
                f"Answer: {answer}",
                fill=(255, 215, 0),
                font=font,
                anchor='mm'
            )
            
            # حفظ الصورة
            temp_image = f"temp/emergency_{timestamp}.jpg"
            img.save(temp_image)
            
            # إنشاء فيديو من الصورة
            from moviepy.editor import ImageClip, concatenate_videoclips
            
            # إطار للسؤال (8 ثواني)
            question_clip = ImageClip(temp_image, duration=8)
            
            # إطار للإجابة (2 ثواني)
            answer_img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color=(41, 128, 185))
            draw = ImageDraw.Draw(answer_img)
            draw.text(
                (VIDEO_WIDTH//2, VIDEO_HEIGHT//2),
                f"Answer: {answer}",
                fill=(255, 215, 0),
                font=font,
                anchor='mm'
            )
            answer_image_path = f"temp/answer_{timestamp}.jpg"
            answer_img.save(answer_image_path)
            answer_clip = ImageClip(answer_image_path, duration=2)
            
            # دمج المقاطع
            final_clip = concatenate_videoclips([question_clip, answer_clip])
            
            output_path = os.path.join(OUTPUT_DIR, f"emergency_{timestamp}.mp4")
            final_clip.write_videofile(
                output_path,
                fps=15,
                codec="libx264",
                audio_codec="aac",
                logger=None
            )
            
            # تنظيف الملفات المؤقتة
            if os.path.exists(temp_image):
                os.remove(temp_image)
            if os.path.exists(answer_image_path):
                os.remove(answer_image_path)
            
            logger.info(f"✅ Emergency video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Emergency video failed: {e}")
            return None
    
    def _split_text(self, text: str, max_chars: int) -> list:
        """تقسيم النص إلى أسطر"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
