"""
نقطة الدخول الرئيسية للتشغيل
"""

import os
import sys
import argparse
from datetime import datetime
from src.main import YouTubeShortsAutomation
from src.utils import logger

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
    
    return parser.parse_args()

def main():
    """الدالة الرئيسية"""
    args = parse_arguments()
    
    # إعداد متغيرات البيئة
    os.environ['RUN_DATE'] = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Starting YouTube Shorts Automation in {args.mode} mode")
    
    # إنشاء نسخة من الأتمتة
    automation = YouTubeShortsAutomation()
    
    # تعديل الإعدادات بناءً على الوسائط
    from src.config import config
    if args.no_upload:
        config.upload_to_youtube = False
    if args.debug:
        config.debug_mode = True
    
    # التشغيل حسب الوضع
    success = False
    
    if args.mode == 'immediate':
        success = automation.run_immediate_short()
    elif args.mode == 'daily':
        success = automation.run_daily_cycle(args.count)
    elif args.mode == 'test':
        logger.info("Test mode - No actual generation will occur")
        success = True
    
    # الخروج مع الكود المناسب
    if success:
        logger.info("✨ Automation completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Automation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
