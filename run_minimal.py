"""
نسخة مبسطة للتشغيل الفوري بدون تعقيدات
"""

import os
import sys
import json
from datetime import datetime

def main():
    """الدالة الرئيسية للتشغيل المبسط"""
    print("=" * 60)
    print("🎬 YouTube Shorts Automation - Minimal Test")
    print(f"📅 Time: {datetime.now()}")
    print("=" * 60)
    
    # إنشاء المجلدات الأساسية
    folders = [
        'assets/backgrounds',
        'assets/fonts',
        'temp/audio',
        'temp/video',
        'output/shorts',
        'output/metadata'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created: {folder}")
    
    # التحقق من الاعتمادات
    print("\n🔍 Checking Python packages...")
    
    packages = [
        'google.generativeai',
        'groq',
        'openai',
        'moviepy',
        'PIL',
        'requests',
        'gtts'
    ]
    
    available = []
    missing = []
    
    for package in packages:
        try:
            __import__(package.replace('.', '_'))
            available.append(package)
        except ImportError:
            missing.append(package)
    
    print(f"✅ Available: {', '.join(available)}")
    if missing:
        print(f"⚠️ Missing: {', '.join(missing)}")
    
    # إنشاء ملف اختبار
    test_data = {
        "status": "READY",
        "timestamp": datetime.now().isoformat(),
        "available_packages": available,
        "missing_packages": missing,
        "instructions": "Run 'python run.py --mode=immediate' to start"
    }
    
    with open('output/test_status.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print("\n📁 Directory structure created:")
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:3]:  # أول 3 ملفات فقط
            print(f'{subindent}{file}')
        if len(files) > 3:
            print(f'{subindent}... and {len(files)-3} more')
    
    print("\n" + "=" * 60)
    print("✅ Minimal setup completed successfully!")
    print("=" * 60)
    
    # سؤال المستخدم إذا كان يريد تشغيل النسخة الكاملة
    response = input("\n🚀 Run full automation now? (y/n): ").lower().strip()
    if response == 'y':
        print("\n⚡ Starting full automation...")
        os.system("python run.py --mode=immediate")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
