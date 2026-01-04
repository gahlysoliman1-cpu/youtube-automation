#!/usr/bin/env python3
"""
Main Runner Script - UPDATED
"""

import os
import sys
import argparse
from src.main import YouTubeShortsAutomation

def main():
    """Main entry point"""
    # Add src to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation")
    parser.add_argument("--mode", choices=["daily", "single", "test"], default="single")
    parser.add_argument("--count", type=int, default=1, help="Number of shorts to upload")
    args = parser.parse_args()
    
    automation = YouTubeShortsAutomation()
    
    if args.mode == "daily":
        print("=" * 60)
        print("🚀 STARTING DAILY AUTOMATION (4 shorts)")
        print("=" * 60)
        success = automation.run_daily_automation()
    elif args.mode == "single":
        print("=" * 60)
        print("🎬 STARTING SINGLE UPLOAD")
        print("=" * 60)
        success = automation.run_single_upload()
    else:
        print("Test mode not implemented")
        success = False
    
    if success:
        print("\n" + "=" * 60)
        print("✅ AUTOMATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ AUTOMATION FAILED!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
