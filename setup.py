"""
ملف الإعداد للمشروع
"""

import os
import sys

def setup_project():
    """إعداد المشروع"""
    print("Setting up YouTube Shorts Automation Project...")
    
    # إنشاء المجلدات المطلوبة
    directories = [
        'assets/backgrounds',
        'assets/fonts',
        'temp/audio',
        'temp/video',
        'temp/images',
        'output/shorts',
        'output/long_videos',
        'output/metadata'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # إنشاء ملفات أساسية
    default_files = {
        'assets/fonts/README.txt': 'Add custom fonts here if needed',
        'assets/backgrounds/README.txt': 'Custom backgrounds can be placed here',
    }
    
    for file_path, content in default_files.items():
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")
    
    print("\n" + "="*50)
    print("✅ Project setup completed successfully!")
    print("Next steps:")
    print("1. Add API keys to GitHub Secrets")
    print("2. Run: python run.py --mode=immediate")
    print("="*50)

if __name__ == "__main__":
    setup_project()
