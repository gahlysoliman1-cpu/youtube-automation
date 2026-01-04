"""
إصلاح سريع للتشغيل الفوري
"""

import os
import sys
import subprocess
from datetime import datetime

def quick_fix():
    """إصلاح سريع للمشاكل الشائعة"""
    print("=" * 60)
    print("⚡ Quick Fix for YouTube Shorts Automation")
    print("=" * 60)
    
    fixes = []
    
    # 1. تثبيت الاعتمادات المفقودة
    print("\n1️⃣ Installing missing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "scipy==1.11.4"], check=True)
        fixes.append("✅ Installed scipy")
    except:
        fixes.append("❌ Failed to install scipy")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "imageio==2.34.0"], check=True)
        fixes.append("✅ Installed imageio")
    except:
        fixes.append("❌ Failed to install imageio")
    
    # 2. إنشاء المجلدات المفقودة
    print("\n2️⃣ Creating missing directories...")
    directories = [
        'assets/backgrounds',
        'assets/fonts',
        'temp/audio',
        'temp/video',
        'output/shorts',
        'output/metadata'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        fixes.append(f"✅ Created directory: {directory}")
    
    # 3. إنشاء ملفات افتراضية
    print("\n3️⃣ Creating default files...")
    
    # ملف خط افتراضي
    font_path = "assets/fonts/arial.ttf"
    if not os.path.exists(font_path):
        try:
            # محاولة نسخ خط نظام
            import shutil
            system_fonts = [
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
            
            for system_font in system_fonts:
                if os.path.exists(system_font):
                    shutil.copy(system_font, font_path)
                    fixes.append(f"✅ Copied font: {font_path}")
                    break
        except:
            fixes.append("⚠️ Could not copy system font")
    
    # 4. اختبار النظام
    print("\n4️⃣ Testing system components...")
    
    # اختبار MoviePy
    try:
        from moviepy.editor import ColorClip
        fixes.append("✅ MoviePy working")
    except Exception as e:
        fixes.append(f"❌ MoviePy error: {str(e)[:50]}")
    
    # اختبار Google APIs
    try:
        import google.auth
        fixes.append("✅ Google Auth working")
    except Exception as e:
        fixes.append(f"❌ Google Auth error: {str(e)[:50]}")
    
    # 5. إنشاء فيديو اختبار
    print("\n5️⃣ Creating test video...")
    try:
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
        
        # فيديو اختبار بسيط
        background = ColorClip(size=(1080, 1920), color=(41, 128, 185), duration=5)
        text = TextClip(
            f"Test Video\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            fontsize=60,
            color='white',
            size=(1000, 200),
            method='caption'
        ).set_position('center').set_duration(5)
        
        video = CompositeVideoClip([background, text])
        video.write_videofile(
            "output/test_video.mp4",
            fps=24,
            codec="libx264",
            audio_codec="aac",
            logger=None
        )
        
        fixes.append("✅ Test video created: output/test_video.mp4")
    except Exception as e:
        fixes.append(f"❌ Test video failed: {str(e)[:50]}")
    
    # عرض النتائج
    print("\n" + "=" * 60)
    print("📊 FIX RESULTS:")
    print("=" * 60)
    
    for fix in fixes:
        print(fix)
    
    # إنشاء تقرير
    with open('quick_fix_report.txt', 'w') as f:
        f.write("Quick Fix Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Python: {sys.version}\n\n")
        
        for fix in fixes:
            f.write(fix + "\n")
    
    print(f"\n📄 Report saved to: quick_fix_report.txt")
    
    # سؤال المستخدم
    print("\n" + "=" * 60)
    response = input("🚀 Run full automation now? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n⚡ Starting full automation...")
        os.system("python run.py --mode=immediate --debug")
    
    return True

if __name__ == "__main__":
    quick_fix()
