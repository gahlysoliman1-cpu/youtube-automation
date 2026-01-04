#!/usr/bin/env python3
"""
Main Runner - FINAL VERSION
"""

import os
import sys
import argparse
from src.main import YouTubeShortsAutomation

def main():
    """Main function"""
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    parser = argparse.ArgumentParser(description="YouTube Shorts")
    parser.add_argument("--mode", choices=["daily", "single"], default="single")
    args = parser.parse_args()
    
    automation = YouTubeShortsAutomation()
    
    if args.mode == "daily":
        print("=" * 60)
        print("🚀 STARTING DAILY AUTOMATION")
        print("=" * 60)
        success = automation.run_daily_automation()
    else:
        print("=" * 60)
        print("🎬 STARTING SINGLE UPLOAD")
        print("=" * 60)
        success = automation.run_single_upload()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
