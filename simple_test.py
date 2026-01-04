"""
اختبار مبسط للتأكد من عمل النظام
"""

import os
import json
from datetime import datetime

def simple_test():
    """اختبار بسيط للتأكد من عمل النظام"""
    print("=" * 60)
    print("🧪 Simple System Test")
    print("=" * 60)
    
    tests = []
    
    # 1. اختبار النظام الأساسي
    print("1. Basic system test...")
    try:
        import sys
        tests.append(f"✅ Python {sys.version.split()[0]}")
    except:
        tests.append("❌ Python test failed")
    
    # 2. اختبار الاعتمادات الأساسية
    print("2. Testing core dependencies...")
    
    core_packages = [
        ('moviepy', 'moviepy'),
        ('PIL', 'Pillow'),
        ('requests', 'requests'),
        ('numpy', 'numpy'),
    ]
    
    for import_name, package_name in core_packages:
        try:
            __import__(import_name)
            tests.append(f"✅ {package_name}")
        except ImportError:
            tests.append(f"❌ {package_name} not found")
    
    # 3. اختبار APIs
    print("3. Testing API keys...")
    
    api_keys = [
        'GEMINI_API_KEY',
        'YOUTUBE_API_KEY',
        'YT_CHANNEL_ID',
        'YT_REFRESH_TOKEN_1'
    ]
    
    for key in api_keys:
        value = os.getenv(key)
        if value and len(value) > 10:
            tests.append(f"✅ {key} (present)")
        else:
            tests.append(f"⚠️ {key} (missing or short)")
    
    # 4. اختبار المجلدات
    print("4. Testing directories...")
    
    required_dirs = [
        'assets/backgrounds',
        'output/shorts',
        'temp/audio'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            tests.append(f"✅ {directory}")
        else:
            tests.append(f"❌ {directory} missing")
    
    # 5. إنشاء تقرير
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS:")
    print("=" * 60)
    
    for test in tests:
        print(test)
    
    # حساب النسبة المئوية للنجاح
    total = len(tests)
    passed = sum(1 for t in tests if t.startswith('✅'))
    percentage = (passed / total) * 100
    
    print(f"\n📊 Score: {passed}/{total} ({percentage:.1f}%)")
    
    # تحديد الحالة
    if percentage >= 80:
        print("🎉 System is READY for automation!")
        status = "READY"
    elif percentage >= 50:
        print("⚠️ System has some issues but may work with fallbacks")
        status = "WARNING"
    else:
        print("❌ System has critical issues")
        status = "FAILED"
    
    # حفظ النتائج
    results = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "score": f"{passed}/{total}",
        "percentage": percentage,
        "tests": tests,
        "next_action": "Run 'python run.py --mode=immediate' if ready"
    }
    
    with open('system_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: system_test_results.json")
    
    # اقتراح الخطوة التالية
    print("\n" + "=" * 60)
    print("🎯 NEXT STEP:")
    
    if status == "READY":
        print("Run the automation: python run.py --mode=immediate")
    elif status == "WARNING":
        print("Try running with debug: python run.py --mode=immediate --debug")
    else:
        print("Fix the issues above first, then run: python quick_fix.py")
    
    print("=" * 60)
    
    return status == "READY"

if __name__ == "__main__":
    success = simple_test()
    sys.exit(0 if success else 1)
