"""
نسخة مبسطة للتشغيل للتحقق من الإعدادات
"""

import os
import sys
import json
from datetime import datetime

def main():
    """الدالة الرئيسية للاختبار البسيط"""
    print("=" * 50)
    print("YouTube Shorts Automation - Simple Test")
    print(f"Time: {datetime.now()}")
    print("=" * 50)
    
    # التحقق من المجلدات
    folders = ['assets', 'output', 'temp']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created folder: {folder}")
    
    # التحقق من APIs المتاحة
    print("\n🔍 Checking available APIs...")
    
    apis_to_check = [
        'GEMINI_API_KEY',
        'GROQ_API_KEY', 
        'OPENAI_API_KEY',
        'ELEVEN_API_KEY',
        'YOUTUBE_API_KEY'
    ]
    
    available_apis = {}
    for api in apis_to_check:
        if os.getenv(api):
            available_apis[api] = "✅ Available"
        else:
            available_apis[api] = "❌ Missing"
    
    print("\nAPI Status:")
    for api, status in available_apis.items():
        print(f"  {api}: {status}")
    
    # إنشاء ملف اختبار
    test_data = {
        "project": "YouTube Shorts Automation",
        "status": "Test Run Successful",
        "timestamp": datetime.now().isoformat(),
        "apis_available": available_apis,
        "next_step": "Run main automation with: python run.py --mode=immediate"
    }
    
    with open('output/test_report.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print("\n" + "=" * 50)
    print("✅ Simple test completed successfully!")
    print(f"📄 Report saved to: output/test_report.json")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
