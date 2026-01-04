#!/usr/bin/env python3
"""
Main Runner Script for YouTube Shorts Automation
"""

import os
import sys
import logging
from src.main import YouTubeShortsAutomation

def main():
    """Main entry point"""
    # Add src to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    automation = YouTubeShortsAutomation()
    
    # Check command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation")
    parser.add_argument("--mode", choices=["daily", "test", "single"], default="daily")
    parser.add_argument("--category", help="Specific category for single mode")
    parser.add_argument("--count", type=int, default=4, help="Number of shorts to generate")
    args = parser.parse_args()
    
    if args.mode == "daily":
        print("=" * 60)
        print("🚀 STARTING DAILY YOUTUBE SHORTS AUTOMATION")
        print("=" * 60)
        
        success = automation.run_daily_automation()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ DAILY AUTOMATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ DAILY AUTOMATION FAILED!")
            print("=" * 60)
            sys.exit(1)
            
    elif args.mode == "test":
        print("Test mode not implemented yet")
        sys.exit(0)
        
    elif args.mode == "single":
        print("Single mode not implemented yet")
        sys.exit(0)

if __name__ == "__main__":
    main()
