"""
Video Generator Module
Creates YouTube Shorts with text, audio, countdown timer, and answer reveal
"""

import os
import json
import logging
import subprocess
import tempfile
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import *
from src.config import *

class VideoGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(SHORTS_DIR, exist_ok=True)
        os.makedirs(LONG_VIDEOS_DIR, exist_ok=True)
    
    def get_background_image(self) -> Optional[str]:
        """Get or create background image with blur effect"""
        try:
            # Create a simple gradient background
            img = Image.new('RGB', VIDEO_CONFIG["short"]["resolution"], color=(41, 128, 185))
            
            # Add some visual interest
            draw = ImageDraw.Draw(img)
            
            # Draw some abstract circles
            width, height = VIDEO_CONFIG["short"]["resolution"]
            for i in range(10):
                x = random.randint(0, width)
                y = random.randint(0, height)
                radius = random.randint(50, 200)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 30)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
            
            # Apply blur effect
            img = img.filter(ImageFilter.GaussianBlur(
                VIDEO_CONFIG["short"]["background_blur"]
            ))
            
            # Save background
            bg_path = os.path.join(SHORTS_DIR, "background.png")
            img.save(bg_path, "PNG")
            
            return bg_path
            
        except Exception as e:
            self.logger.error(f"❌ Error creating background: {e}")
            return None
    
    def create_text_overlay(self, text: str, font_size: int = 60, 
                           color: str = "white", max_width: int = 800) -> Optional[str]:
        """Create text overlay image"""
        try:
            # Create transparent image
            img = Image.new('RGBA', VIDEO_CONFIG["short"]["resolution"], (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Try to load font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Wrap text
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Calculate position
            total_height = len(lines) * (font_size + 10)
            y = (VIDEO_CONFIG["short"]["resolution"][1] - total_height) // 2
            
            # Draw each line
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (VIDEO_CONFIG["short"]["resolution"][0] - text_width) // 2
                
                # Add text shadow
                draw.text((x+2, y+2), line, font=font, fill="black")
                draw.text((x, y), line, font=font, fill=color)
                
                y += font_size + 10
            
            # Save overlay
            overlay_path = os.path.join(SHORTS_DIR, "text_overlay.png")
            img.save(overlay_path, "PNG")
            
            return overlay_path
            
        except Exception as e:
            self.logger.error(f"❌ Error creating text overlay: {e}")
            return None
    
    def create_countdown_overlay(self, duration: int = 10) -> List[str]:
        """Create countdown timer overlay images"""
        countdown_images = []
        
        try:
            for second in range(duration, 0, -1):
                img = Image.new('RGBA', (200, 100), (0, 0, 0, 150))
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 60)
                except:
                    font = ImageFont.load_default()
                
                # Draw countdown number
                draw.text((70, 20), str(second), font=font, fill="white")
                
                # Save image
                countdown_path = os.path.join(SHORTS_DIR, f"countdown_{second}.png")
                img.save(countdown_path, "PNG")
                countdown_images.append(countdown_path)
            
            return countdown_images
            
        except Exception as e:
            self.logger.error(f"❌ Error creating countdown: {e}")
            return []
    
    def create_answer_reveal(self, correct_answer: str, explanation: str) -> Optional[str]:
        """Create answer reveal overlay"""
        try:
            img = Image.new('RGBA', VIDEO_CONFIG["short"]["resolution"], (0, 0, 0, 200))
            draw = ImageDraw.Draw(img)
            
            # Title
            try:
                title_font = ImageFont.truetype("arial.ttf", 70)
                text_font = ImageFont.truetype("arial.ttf", 40)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Draw answer
            title = f"Answer: {correct_answer}"
            bbox = draw.textbbox((0, 0), title, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (VIDEO_CONFIG["short"]["resolution"][0] - text_width) // 2
            y = VIDEO_CONFIG["short"]["resolution"][1] // 3
            
            draw.text((x, y), title, font=title_font, fill="white")
            
            # Draw explanation (wrapped)
            words = explanation.split()
            lines = []
            current_line = []
            max_width = VIDEO_CONFIG["short"]["resolution"][0] - 100
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=text_font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw explanation lines
            y += 100
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=text_font)
                text_width = bbox[2] - bbox[0]
                x = (VIDEO_CONFIG["short"]["resolution"][0] - text_width) // 2
                draw.text((x, y), line, font=text_font, fill="#FFD700")  # Gold color
                y += 50
            
            # Save reveal image
            reveal_path = os.path.join(SHORTS_DIR, "answer_reveal.png")
            img.save(reveal_path, "PNG")
            
            return reveal_path
            
        except Exception as e:
            self.logger.error(f"❌ Error creating answer reveal: {e}")
            return None
    
    def create_short_video(self, question_data: Dict, 
                          question_audio_path: str,
                          countdown_audio_path: str,
                          output_path: str) -> bool:
        """Create complete Short video"""
        try:
            self.logger.info("🎬 Creating Short video...")
            
            # 1. Get background
            background_path = self.get_background_image()
            if not background_path:
                return False
            
            # 2. Create question overlay
            question_text = question_data["question"]
            question_overlay = self.create_text_overlay(
                question_text, 
                font_size=70,
                color="white",
                max_width=900
            )
            
            if not question_overlay:
                return False
            
            # 3. Create countdown images
            countdown_images = self.create_countdown_overlay(
                VIDEO_CONFIG["short"]["countdown_duration"]
            )
            
            # 4. Create answer reveal
            answer_reveal = self.create_answer_reveal(
                question_data["correct_answer"],
                question_data["explanation"]
            )
            
            # 5. Calculate durations
            question_duration = self.get_audio_duration(question_audio_path)
            countdown_duration = VIDEO_CONFIG["short"]["countdown_duration"]
            answer_duration = VIDEO_CONFIG["short"]["answer_duration"]
            
            total_duration = question_duration + countdown_duration + answer_duration
            
            # 6. Create video using moviepy
            clips = []
            
            # Part 1: Question with audio
            background_clip = ImageClip(background_path).set_duration(total_duration)
            question_overlay_clip = ImageClip(question_overlay).set_duration(question_duration)
            question_audio_clip = AudioFileClip(question_audio_path)
            
            question_composite = CompositeVideoClip([
                background_clip.subclip(0, question_duration),
                question_overlay_clip
            ]).set_audio(question_audio_clip)
            
            clips.append(question_composite)
            
            # Part 2: Countdown timer
            if countdown_images and os.path.exists(countdown_audio_path):
                # Create countdown clip
                countdown_duration_per_image = countdown_duration / len(countdown_images)
                countdown_clips = []
                
                for i, img_path in enumerate(countdown_images):
                    img_clip = ImageClip(img_path).set_duration(countdown_duration_per_image)
                    countdown_clips.append(img_clip)
                
                countdown_video = concatenate_videoclips(countdown_clips, method="compose")
                
                # Position countdown at bottom
                countdown_video = countdown_video.set_position(("center", "bottom"))
                
                # Add countdown audio
                countdown_audio = AudioFileClip(countdown_audio_path)
                countdown_composite = CompositeVideoClip([
                    background_clip.subclip(question_duration, question_duration + countdown_duration),
                    countdown_video
                ]).set_audio(countdown_audio)
                
                clips.append(countdown_composite)
            
            # Part 3: Answer reveal (silent)
            if answer_reveal:
                answer_clip = ImageClip(answer_reveal).set_duration(answer_duration)
                answer_composite = CompositeVideoClip([
                    background_clip.subclip(total_duration - answer_duration, total_duration),
                    answer_clip
                ])
                
                clips.append(answer_composite)
            
            # 7. Concatenate all parts
            final_video = concatenate_videoclips(clips, method="compose")
            
            # 8. Set video properties for Shorts
            final_video = final_video.resize(VIDEO_CONFIG["short"]["resolution"])
            final_video = final_video.set_fps(VIDEO_CONFIG["short"]["fps"])
            
            # 9. Export video
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                logger=None
            )
            
            self.logger.info(f"✅ Video created successfully: {output_path}")
            
            # Cleanup temporary files
            self.cleanup_temp_files([
                background_path, question_overlay, answer_reveal
            ] + countdown_images)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating video: {e}")
            return False
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file"""
        try:
            if os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                audio_clip.close()
                return duration
            return 5.0  # Default duration
        except:
            return 5.0
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary files"""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
    
    def compile_shorts(self, shorts_paths: List[str], output_path: str) -> bool:
        """Compile multiple shorts into one long video"""
        try:
            if len(shorts_paths) < 2:
                return False
            
            clips = []
            
            for short_path in shorts_paths:
                if os.path.exists(short_path):
                    clip = VideoFileClip(short_path)
                    clips.append(clip)
            
            if not clips:
                return False
            
            # Concatenate all shorts
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add intro and outro
            intro_duration = 3
            outro_duration = 5
            
            # Create intro
            intro_text = "Daily Trivia Compilation\nCan you answer all?"
            intro_overlay = self.create_text_overlay(intro_text, font_size=80, color="white")
            
            if intro_overlay:
                intro_clip = ImageClip(intro_overlay).set_duration(intro_duration)
                intro_bg = self.get_background_image()
                if intro_bg:
                    intro_bg_clip = ImageClip(intro_bg).set_duration(intro_duration)
                    intro = CompositeVideoClip([intro_bg_clip, intro_clip])
                    clips.insert(0, intro)
            
            # Create outro
            outro_text = "Thanks for watching!\nSubscribe for daily quizzes!"
            outro_overlay = self.create_text_overlay(outro_text, font_size=80, color="white")
            
            if outro_overlay:
                outro_clip = ImageClip(outro_overlay).set_duration(outro_duration)
                outro_bg = self.get_background_image()
                if outro_bg:
                    outro_bg_clip = ImageClip(outro_bg).set_duration(outro_duration)
                    outro = CompositeVideoClip([outro_bg_clip, outro_clip])
                    clips.append(outro)
            
            # Final compilation
            if len(clips) > 2:  # Has intro and outro
                final_video = concatenate_videoclips(clips, method="compose")
            
            # Export
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=VIDEO_CONFIG["long"]["fps"],
                logger=None
            )
            
            self.logger.info(f"✅ Compilation created: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error compiling shorts: {e}")
            return False
