"""
Video Generator Module - REAL PRODUCTION
Creates engaging YouTube Shorts with animations
"""

import os
import json
import logging
import subprocess
import tempfile
import random
from typing import Dict, List, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.config import *

class VideoGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_short_video(self, question_data: Dict, output_path: str) -> bool:
        """Create a complete YouTube Short video"""
        try:
            self.logger.info("🎬 Creating YouTube Short video...")
            
            # إنشاء ملف نصي للـ FFmpeg
            ffmpeg_script = self.generate_ffmpeg_script(question_data, output_path)
            
            if not ffmpeg_script:
                self.logger.error("❌ Failed to generate FFmpeg script")
                return False
            
            # حفظ السكريبت وتنفيذه
            script_file = os.path.join(SHORTS_DIR, "generate_video.sh")
            with open(script_file, 'w') as f:
                f.write(ffmpeg_script)
            
            # جعل السكريبت قابلاً للتنفيذ
            os.chmod(script_file, 0o755)
            
            self.logger.info(f"📝 Running FFmpeg script...")
            
            # تنفيذ السكريبت
            result = subprocess.run(
                ['bash', script_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    self.logger.info(f"✅ Video created: {output_path} ({file_size:.1f} MB)")
                    return True
                else:
                    self.logger.error("❌ Video file not created")
                    return False
            else:
                self.logger.error(f"❌ FFmpeg error: {result.stderr}")
                return self.create_simple_video(question_data, output_path)
                
        except Exception as e:
            self.logger.error(f"❌ Error creating video: {e}")
            return self.create_simple_video(question_data, output_path)
    
    def generate_ffmpeg_script(self, question_data: Dict, output_path: str) -> str:
        """Generate FFmpeg script for creating the Short"""
        try:
            # استخراج بيانات السؤال
            question = question_data.get('question', 'Can you answer this?')
            options = question_data.get('options', ['A', 'B', 'C', 'D'])
            correct = question_data.get('correct_answer', 'A')
            explanation = question_data.get('explanation', 'Good job!')
            
            # تنظيف النصوص
            question = self.clean_text(question)
            explanation = self.clean_text(explanation)
            
            # ألوان
            bg_color = VIDEO_CONFIG["short"]["background_color"]
            text_color = VIDEO_CONFIG["short"]["text_color"]
            accent_color = VIDEO_CONFIG["short"]["accent_color"]
            
            # توليد سكريبت FFmpeg معقد
            script = f'''#!/bin/bash
echo "🎬 Generating YouTube Short..."

# إعدادات الفيديو
RESOLUTION="1080x1920"
FPS=30
DURATION=22
BG_COLOR="0x{self.rgb_to_hex(bg_color)}"
TEXT_COLOR="0x{self.rgb_to_hex(text_color)}"
ACCENT_COLOR="0x{self.rgb_to_hex(accent_color)}"
FONT_SIZE=72
SMALL_FONT=48

# إنشاء الفيديو الرئيسي
ffmpeg -f lavfi -i color=c=$BG_COLOR:s=$RESOLUTION:d=$DURATION \\
       -filter_complex "
        
        # === الجزء 1: السؤال (0-10 ثواني) ===
        [0:v]drawtext=text='{question}':fontcolor=$TEXT_COLOR:fontsize=$FONT_SIZE: \\
               fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: \\
               x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,0,10)'[v1];
        
        # === الجزء 2: العد التنازلي (10-20 ثواني) ===
        [v1]drawtext=text='%{{eif\\\\:10 - floor(t-10)}}':fontcolor=$ACCENT_COLOR:fontsize=120: \\
               fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: \\
               x=(w-text_w)/2:y=(h-text_h)*2/3:enable='between(t,10,20)'[v2];
        
        # === العد التنازلي النصي ===
        [v2]drawtext=text='Write answer in comments!':fontcolor=white:fontsize=36: \\
               x=(w-text_w)/2:y=(h-text_h)*3/4:enable='between(t,10,20)'[v3];
        
        # === الجزء 3: الإجابة (20-22 ثواني) ===
        [v3]drawtext=text='Answer: {correct}':fontcolor=0x00FF00:fontsize=96: \\
               fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: \\
               x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,20,22)'[v4];
        
        [v4]drawtext=text='{explanation}':fontcolor=0xFFD700:fontsize=48: \\
               x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,20,22)'[v5];
        
        # === إضافة تأثيرات ===
        [v5]boxblur=5:enable='between(t,0,10)'[v6];
        [v6]fade=t=in:st=0:d=1:alpha=1[v7];
        [v7]fade=t=out:st=21:d=1:alpha=1[vout]
        
        " \\
       -map "[vout]" \\
       -c:v libx264 \\
       -preset fast \\
       -crf 23 \\
       -pix_fmt yuv420p \\
       -r $FPS \\
       -y "{output_path}"

# التحقق من الملف الناتج
if [ -f "{output_path}" ]; then
    FILESIZE=$(du -h "{output_path}" | cut -f1)
    echo "✅ Video created successfully! Size: $FILESIZE"
    exit 0
else
    echo "❌ Video creation failed!"
    exit 1
fi
'''
            return script
            
        except Exception as e:
            self.logger.error(f"❌ Error generating FFmpeg script: {e}")
            return None
    
    def create_simple_video(self, question_data: Dict, output_path: str) -> bool:
        """Create simple fallback video"""
        try:
            self.logger.info("🔄 Creating simple fallback video...")
            
            question = question_data.get('question', 'Can you answer this?')
            options = question_data.get('options', ['A', 'B', 'C', 'D'])
            correct = question_data.get('correct_answer', 'A')
            
            # تنظيف النصوص
            question = self.clean_text(question[:100])  # تقليل الطول
            
            # سكريبت FFmpeg مبسط
            script = f'''#!/bin/bash
# إنشاء فيديو بسيط
ffmpeg -f lavfi -i color=c=0x1a1a2e:s=1080x1920:d=22 \\
       -vf "
            drawtext=text='{question}':fontcolor=white:fontsize=60: \\
                    x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,0,10)',
            drawtext=text='10 9 8 7 6 5 4 3 2 1':fontcolor=0x00aaff:fontsize=80: \\
                    x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,10,20)',
            drawtext=text='Answer: {correct}':fontcolor=0x00ff00:fontsize=70: \\
                    x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,20,22)'
       " \\
       -c:v libx264 \\
       -preset ultrafast \\
       -t 22 \\
       -pix_fmt yuv420p \\
       -y "{output_path}"
'''
            
            script_file = os.path.join(SHORTS_DIR, "simple_video.sh")
            with open(script_file, 'w') as f:
                f.write(script)
            
            os.chmod(script_file, 0o755)
            
            result = subprocess.run(['bash', script_file], capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"✅ Simple video created: {output_path}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error creating simple video: {e}")
            return False
    
    def create_video_with_options(self, question_data: Dict, output_path: str) -> bool:
        """Create video with multiple choice options"""
        try:
            self.logger.info("📊 Creating video with options display...")
            
            question = question_data.get('question', 'Question?')
            options = question_data.get('options', ['A', 'B', 'C', 'D'])
            correct = question_data.get('correct_answer', 'A')
            
            # تنظيف النصوص
            question = self.clean_text(question)
            options = [self.clean_text(opt) for opt in options]
            
            # بناء سكريبت معقد
            script_lines = [
                '#!/bin/bash',
                'echo "🎥 Creating option-based video..."',
                '',
                '# الألوان',
                'BG="0x1a1a2e"',
                'TEXT="white"',
                'CORRECT="0x00ff00"',
                'WRONG="0xff5555"',
                '',
                '# بداية سكريبت FFmpeg'
            ]
            
            ffmpeg_cmd = [
                'ffmpeg -f lavfi -i color=c=$BG:s=1080x1920:d=22 \\',
                '       -filter_complex "'
            ]
            
            # إضافة السؤال (0-8 ثواني)
            ffmpeg_cmd.append(f'[0:v]drawtext=text=\\'{question}\\':fontcolor=$TEXT:fontsize=64:')
            ffmpeg_cmd.append('       x=(w-text_w)/2:y=300:enable=\'between(t,0,8)\'[v1];')
            
            # إضافة الخيارات (8-18 ثواني)
            y_positions = [700, 850, 1000, 1150]
            for i, (opt, y) in enumerate(zip(options, y_positions)):
                letter = chr(65 + i)  # A, B, C, D
                color = '$CORRECT' if letter == correct else '$TEXT'
                ffmpeg_cmd.append(f'[v{i+1}]drawtext=text=\\'{letter}) {opt}\\':fontcolor={color}:fontsize=48:')
                ffmpeg_cmd.append(f'       x=100:y={y}:enable=\'between(t,8,18)\'[v{i+2}];')
            
            # العد التنازلي (18-20 ثواني)
            ffmpeg_cmd.append('[v5]drawtext=text=\\'Time\\'s up!\\':fontcolor=0xffaa00:fontsize=72:')
            ffmpeg_cmd.append('       x=(w-text_w)/2:y=1400:enable=\'between(t,18,20)\'[v6];')
            
            # الإجابة الصحيحة (20-22 ثواني)
            ffmpeg_cmd.append('[v6]drawtext=text=\\'Correct: {correct}\\':fontcolor=$CORRECT:fontsize=96:')
            ffmpeg_cmd.append('       x=(w-text_w)/2:y=800:enable=\'between(t,20,22)\'[vout]"')
            
            ffmpeg_cmd.append('       -map "[vout]" \\')
            ffmpeg_cmd.append('       -c:v libx264 \\')
            ffmpeg_cmd.append('       -preset fast \\')
            ffmpeg_cmd.append('       -crf 23 \\')
            ffmpeg_cmd.append('       -pix_fmt yuv420p \\')
            ffmpeg_cmd.append(f'       -y "{output_path}"')
            
            script_lines.extend(ffmpeg_cmd)
            
            # إضافة التحقق
            script_lines.extend([
                '',
                '# التحقق',
                f'if [ -f "{output_path}" ]; then',
                '    echo "✅ Video created successfully!"',
                '    exit 0',
                'else',
                '    echo "❌ Video creation failed"',
                '    exit 1',
                'fi'
            ])
            
            script = '\n'.join(script_lines)
            
            # حفظ وتنفيذ السكريبت
            script_file = os.path.join(SHORTS_DIR, "options_video.sh")
            with open(script_file, 'w') as f:
                f.write(script)
            
            os.chmod(script_file, 0o755)
            
            result = subprocess.run(['bash', script_file], capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"✅ Options video created: {output_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error creating options video: {e}")
            return False
    
    def clean_text(self, text: str) -> str:
        """Clean text for FFmpeg"""
        if not text:
            return ""
        
        # استبدال الأحرف الخاصة
        replacements = {
            "'": "\\'",
            '"': '\\"',
            ':': '\\:',
            '`': '\\`',
            '$': '\\$'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB tuple to hex"""
        return f'{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def compile_shorts(self, shorts_paths: List[str], output_path: str) -> bool:
        """Compile multiple shorts into one video"""
        try:
            if len(shorts_paths) < 2:
                return False
            
            # إنشاء قائمة ملفات
            list_file = os.path.join(SHORTS_DIR, "concat_list.txt")
            with open(list_file, 'w') as f:
                for path in shorts_paths:
                    if os.path.exists(path):
                        f.write(f"file '{os.path.abspath(path)}'\n")
            
            # دمج الفيديوهات
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"✅ Compiled {len(shorts_paths)} shorts into {output_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error compiling shorts: {e}")
            return False
