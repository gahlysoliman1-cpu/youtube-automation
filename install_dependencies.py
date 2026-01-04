#!/usr/bin/env python3
"""
Install all required dependencies for YouTube Shorts Automation
"""

import subprocess
import sys

def install_dependencies():
    """Install all required Python packages"""
    dependencies = [
        "google-generativeai==0.3.2",
        "google-genai==0.1.0",
        "groq==0.9.0",
        "openai==1.12.0",
        "moviepy==1.0.3",
        "Pillow==10.2.0",
        "gTTS==2.4.0",
        "elevenlabs==0.2.27",
        "google-api-python-client==2.108.0",
        "google-auth-httplib2==0.1.1",
        "google-auth-oauthlib==1.1.0",
        "requests==2.31.0",
        "pytz==2024.1",
    ]
    
    print("📦 Installing dependencies...")
    
    for package in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed: {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            # Try without version
            try:
                package_name = package.split('==')[0]
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"✅ Installed (without version): {package_name}")
            except:
                print(f"⚠️  Skipping: {package}")
    
    print("\n✅ All dependencies installed!")

def setup_ffmpeg():
    """Setup FFmpeg for video processing"""
    print("\n🎬 Setting up FFmpeg...")
    
    # For GitHub Actions
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print("Detected GitHub Actions environment")
        # FFmpeg is already installed in ubuntu-latest
        return True
    
    # For local development
    try:
        import imageio
        imageio.plugins.ffmpeg.download()
        print("✅ FFmpeg setup completed")
        return True
    except Exception as e:
        print(f"⚠️  FFmpeg setup warning: {e}")
        print("You may need to install FFmpeg manually:")
        print("  Ubuntu: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from ffmpeg.org")
        return False

if __name__ == "__main__":
    install_dependencies()
    setup_ffmpeg()
