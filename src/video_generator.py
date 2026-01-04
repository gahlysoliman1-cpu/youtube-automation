"""
Video Generator Module - FINAL WORKING VERSION
"""

import os
import json
import logging
import subprocess
import random
from typing import Dict, List, Optional
from datetime import datetime
from src.config import *

class VideoGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_short_video(self, question_data: Dict, output_path: str) -> bool:
        """Create a YouTube Short video"""
        try:
            self.logger.info("🎬 Creating YouTube Short video...")
            
            # استخراج البيانات
            question = question_data.get('question', 'Can you answer this?')
            options = question_data.get('options', ['A', 'B', 'C', 'D'])
            correct = question_data.get('correct_answer', 'A')
            explanation = question_data.get('explanation', 'Good job!')
            
            # تنظيف النصوص
            question_clean = question.replace("'", "").replace('"', '').replace('`', '')
            explanation_clean = explanation.replace("'", "").replace('"', '').replace('`', '')
            
            # قص النصوص الطويلة
            if len(question_clean) > 80:
                question_clean = question_clean[:77] + "..."
            
            if len(explanation_clean) > 50:
                explanation_clean = explanation_clean[:47] + "..."
            
            # إنشاء فيديو باستخدام FFmpeg مباشرة
            return self.create_video_directly(
                question_clean, options, correct, explanation_clean, output_path
            )
                
        except Exception as e:
            self.logger.error(f"❌ Error in create_short_video: {e}")
            return self.create_simple_video(question_data, output_path)
    
    def create_video_directly(self, question, options, correct, explanation, output_path):
        """Create video using direct FFmpeg command"""
        try:
            # بناء أمر FFmpeg
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', 'color=c=0x1a1a2e:s=1080x1920:d=22',
                '-filter_complex',
                self.build_filter_complex(question, options, correct, explanation),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                '-y', output_path
            ]
            
            self.logger.info("📝 Running FFmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
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
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in create_video_directly: {e}")
            return False
    
    def build_filter_complex(self, question, options, correct, explanation):
        """Build filter_complex string for FFmpeg"""
        # الجزء 1: السؤال (0-10 ثواني)
        filter_parts = [
            f"drawtext=text='{question}':fontcolor=white:fontsize=60:"
            f"x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,0,10)'"
        ]
        
        # الجزء 2: العد التنازلي (10-20 ثواني)
        filter_parts.append(
            f"drawtext=text='10 9 8 7 6 5 4 3 2 1':fontcolor=0x00aaff:fontsize=90:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,10,20)'"
        )
        
        # الجزء 3: الإجابة (20-22 ثواني)
        filter_parts.append(
            f"drawtext=text='Answer: {correct}':fontcolor=0x00ff00:fontsize=80:"
            f"x=(w-text_w)/2:y=(h-text_h)/3:enable='between(t,20,22)'"
        )
        
        # الجزء 4: الشرح (20-22 ثواني)
        filter_parts.append(
            f"drawtext=text='{explanation}':fontcolor=0xffd700:fontsize=40:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,20,22)'"
        )
        
        # دمج جميع الأجزاء
        filter_complex = ','.join(filter_parts)
        return filter_complex
    
    def create_simple_video(self, question_data: Dict, output_path: str) -> bool:
        """Create simple fallback video"""
        try:
            self.logger.info("🔄 Creating simple video...")
            
            question = question_data.get('question', 'Can you answer this?')
            correct = question_data.get('correct_answer', 'A')
            
            # تنظيف النص
            question = question.replace("'", "").replace('"', '').replace('`', '')
            if len(question) > 60:
                question = question[:57] + "..."
            
            # أمر FFmpeg مبسط
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', 'color=c=blue:s=1080x1920:d=15',
                '-vf', f"drawtext=text='{question}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/3,"
                       f"drawtext=text='Time\\\\\\'s up!':fontcolor=yellow:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,10,15)',"
                       f"drawtext=text='Correct: {correct}':fontcolor=green:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,15,22)'",
                '-c:v', 'libx264',
                '-t', '22',
                '-pix_fmt', 'yuv420p',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"✅ Simple video created: {output_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error in create_simple_video: {e}")
            return False
    
    def compile_shorts(self, shorts_paths: List[str], output_path: str) -> bool:
        """Compile multiple shorts into one video"""
        try:
            if len(shorts_paths) < 2:
                return False
            
            # إنشاء قائمة الملفات
            list_file = "concat_list.txt"
            with open(list_file, 'w') as f:
                for path in shorts_paths:
                    if os.path.exists(path):
                        f.write(f"file '{path}'\n")
            
            # دمج الفيديوهات
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # تنظيف ملف القائمة
            if os.path.exists(list_file):
                os.remove(list_file)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"✅ Compiled {len(shorts_paths)} shorts")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error compiling shorts: {e}")
            return False
