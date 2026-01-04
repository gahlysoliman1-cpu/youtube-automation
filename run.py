#!/usr/bin/env python3
"""
Main Runner Script for YouTube Shorts Automation
Production-ready script for daily automation
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import YouTubeShortsAutomation
from src.utils import setup_logging, validate_environment
from src.config import LOGS_DIR, BASE_DIR

def main():
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation")
    parser.add_argument("--mode", choices=["daily", "single", "test"], default="daily",
                       help="Run mode: daily (4 shorts), single (1 short), test (no upload)")
    parser.add_argument("--category", type=str, 
                       help="Specific category for single mode")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    parser.add_argument("--no-upload", action="store_true",
                       help="Generate videos but don't upload")
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = os.path.join(LOGS_DIR, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger = setup_logging(log_file)
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("🚀 YouTube Shorts Automation - Starting")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Working Directory: {BASE_DIR}")
    logger.info(f"Log File: {log_file}")
    
    # Validate environment
    if not validate_environment():
        logger.error("❌ Environment validation failed")
        sys.exit(1)
    
    try:
        # Create automation instance
        automation = YouTubeShortsAutomation()
        
        if args.mode == "daily":
            logger.info("Running daily automation (4 shorts + compilation)")
            success = automation.run_daily_automation()
            
            if success:
                logger.info("✅ Daily automation completed successfully")
                sys.exit(0)
            else:
                logger.error("❌ Daily automation failed")
                sys.exit(1)
                
        elif args.mode == "single":
            logger.info("Single mode - Not fully implemented yet")
            # You can implement single video generation here
            sys.exit(0)
            
        elif args.mode == "test":
            logger.info("Test mode - Generating test content only")
            # Implement test mode here
            sys.exit(0)
    
    except KeyboardInterrupt:
        logger.info("⚠️ Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
