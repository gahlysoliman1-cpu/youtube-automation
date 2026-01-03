"""
نقطة الدخول الرئيسية للتشغيل - نسخة محسنة
"""

import os
import sys
import argparse
import traceback
from datetime import datetime
from src.main import YouTubeShortsAutomation
from src.utils import logger, create_directories

def parse_arguments():
    """تحليل وسائط سطر الأوامر"""
    parser = argparse.ArgumentParser(description='YouTube Shorts Automation')
    parser.add_argument('--mode', type=str, default='daily',
                       choices=['daily', 'immediate', 'test'],
                       help='Mode of operation')
    parser.add_argument('--count', type=int, default=4,
                       help='Number of shorts to generate')
    parser.add_argument('--no-upload', action='store_true',
                       help='Skip YouTube upload')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--simple', action='store_true',
                       help='Use simple mode only')
    
    return parser.parse_args()

def check_environment():
    """التحقق من البيئة والمتطلبات"""
    logger.info("🔍 Checking environment...")
    
    # التحقق من المجلدات
    create_directories()
    
    # التحقق من APIs الأساسية
    required_envs = ['GEMINI_API_KEY', 'YOUTUBE_API_KEY']
    missing = []
    
    for env in required_envs:
        if not os.getenv(env):
            missing.append(env)
    
    if missing:
        logger.warning(f"⚠️ Missing environment variables: {missing}")
        logger.warning("System will use fallback mode")
    
    return len(missing) == 0

def main():
    """الدالة الرئيسية"""
    args = parse_arguments()
    
    # إعداد متغيرات البيئة
    os.environ['RUN_DATE'] = datetime.now().strftime("%Y-%m-%d")
    
    logger.info("=" * 60)
    logger.info(f"🎬 Starting YouTube Shorts Automation")
    logger.info(f"📅 Date: {datetime.now()}")
    logger.info(f"🔧 Mode: {args.mode}")
    logger.info(f"📊 Count: {args.count}")
    logger.info("=" * 60)
    
    # التحقق من البيئة
    env_ok = check_environment()
    
    if not env_ok and args.mode != 'test':
        logger.warning("⚠️ Environment check failed, but continuing with fallbacks")
    
    try:
        # إنشاء نسخة من الأتمتة
        automation = YouTubeShortsAutomation()
        
        # تعديل الإعدادات بناءً على الوسائط
        from src.config import config
        if args.no_upload:
            config.upload_to_youtube = False
            logger.info("📤 YouTube upload disabled")
        
        if args.debug:
            config.debug_mode = True
            logger.info("🐛 Debug mode enabled")
        
        if args.simple:
            logger.info("🔸 Simple mode enabled")
        
        # التشغيل حسب الوضع
        success = False
        
        if args.mode == 'immediate':
            logger.info("⚡ Generating immediate short...")
            success = automation.run_immediate_short()
        elif args.mode == 'daily':
            logger.info("📅 Running daily cycle...")
            success = automation.run_daily_cycle(args.count)
        elif args.mode == 'test':
            logger.info("🧪 Test mode - Checking only")
            success = True
        
        # النتيجة النهائية
        if success:
            logger.info("")
            logger.info("✨" * 30)
            logger.info("✨ AUTOMATION COMPLETED SUCCESSFULLY! ✨")
            logger.info("✨" * 30)
            sys.exit(0)
        else:
            logger.error("")
            logger.error("❌" * 30)
            logger.error("❌ AUTOMATION FAILED! ❌")
            logger.error("❌" * 30)
            sys.exit(1)
            
    except Exception as e:
        logger.error("💥 CRITICAL ERROR:")
        logger.error(str(e))
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
