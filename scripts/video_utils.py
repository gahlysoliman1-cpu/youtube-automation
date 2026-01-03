import os
import subprocess
import logging
import json
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def run_ffmpeg(command):
    try:
        logger.debug(f"Executing FFmpeg: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stderr:
            logger.debug(f"FFmpeg stderr: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed with exit code {e.returncode}")
        logger.error(f"FFmpeg stderr: {e.stderr}")
        raise

def create_short_video(question, answer, audio_path, output_path, background_image):
    temp_files = []
    
    try:
        # Validate paths
        if not os.path.exists(background_image):
            raise FileNotFoundError(f"Background image not found: {background_image}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Get audio duration
        audio_info = subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'json', audio_path
        ]).decode('utf-8')
        audio_duration = float(json.loads(audio_info)['format']['duration'])
        video_duration = max(10.0, min(12.0, audio_duration + 0.5))  # Ensure at least 10s
        
        # Create question frame with countdown
        question_frame = f"temp_question_{int(time.time())}.png"
        temp_files.append(question_frame)
        
        run_ffmpeg([
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', background_image,
            '-vf', f"drawtext=text='{question}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-100:box=1:boxcolor=black@0.5:boxborderw=10,"
                   f"drawtext=text='%{{n}}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=64:fontcolor=yellow:x=(w-text_w)/2:y=h-th-50:box=1:boxcolor=black@0.7:boxborderw=10,"
                   f"fps=1",
            '-t', '1',
            '-frames:v', '1',
            question_frame
        ])
        
        # Create answer frame
        answer_frame = f"temp_answer_{int(time.time())}.png"
        temp_files.append(answer_frame)
        
        run_ffmpeg([
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', background_image,
            '-vf', f"drawtext=text='Answer: {answer}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=56:fontcolor=lime:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.7:boxborderw=10",
            '-t', '1',
            '-frames:v', '1',
            answer_frame
        ])
        
        # Create silent audio for answer part
        silent_audio = f"temp_silent_{int(time.time())}.aac"
        temp_files.append(silent_audio)
        
        run_ffmpeg([
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'anullsrc=r=44100:cl=stereo',
            '-t', '2',
            silent_audio
        ])
        
        # Create final video
        temp_video1 = f"temp_video1_{int(time.time())}.mp4"
        temp_video2 = f"temp_video2_{int(time.time())}.mp4"
        temp_files.extend([temp_video1, temp_video2])
        
        # First part: question with audio
        run_ffmpeg([
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', question_frame,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-t', str(video_duration),
            '-vf', f"fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black",
            temp_video1
        ])
        
        # Second part: answer with silent audio
        run_ffmpeg([
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', answer_frame,
            '-i', silent_audio,
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-t', '2',
            '-vf', f"fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black",
            temp_video2
        ])
        
        # Concatenate parts
        concat_list = f"concat_list_{int(time.time())}.txt"
        temp_files.append(concat_list)
        
        with open(concat_list, 'w') as f:
            f.write(f"file '{temp_video1}'\n")
            f.write(f"file '{temp_video2}'\n")
        
        run_ffmpeg([
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-movflags', '+faststart',
            '-vf', 'fps=30',
            output_path
        ])
        
        logger.info(f"Successfully created short video: {output_path}")
        return output_path
        
    finally:
        # Cleanup temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {str(e)}")

def create_compilation_video(short_paths, output_path):
    if not short_paths:
        raise ValueError("No shorts provided for compilation")
    
    temp_files = []
    
    try:
        # Create concat list
        concat_list = f"concat_list_{int(time.time())}.txt"
        temp_files.append(concat_list)
        
        with open(concat_list, 'w') as f:
            for path in short_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")
        
        # Add transitions between videos
        filter_complex = f"concat=n={len(short_paths)}:v=1:a=1"
        
        run_ffmpeg([
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list,
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:v', '4M',
            '-b:a', '192k',
            '-movflags', '+faststart',
            '-pix_fmt', 'yuv420p',
            output_path
        ])
        
        logger.info(f"Successfully created compilation video: {output_path}")
        return output_path
        
    finally:
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {str(e)}")
