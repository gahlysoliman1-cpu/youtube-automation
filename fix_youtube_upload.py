"""
إصلاح مشكلة رفع YouTube
"""

import os
import sys

def fix_youtube_issues():
    """إصلاح مشاكل YouTube الشائعة"""
    print("=" * 60)
    print("🔧 Fixing YouTube Upload Issues")
    print("=" * 60)
    
    fixes = []
    
    # 1. التحقق من OAuth Scopes
    print("\n1️⃣ Checking OAuth Scopes...")
    required_scopes = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube"
    ]
    
    print("Required scopes for upload:")
    for scope in required_scopes:
        print(f"   - {scope}")
    
    fixes.append("""
    🔧 FIX 1: Verify OAuth Consent Screen
    ------------------------------------
    1. Go to Google Cloud Console
    2. Navigate to "APIs & Services" > "OAuth consent screen"
    3. Add these scopes to your OAuth 2.0 Scopes:
       - https://www.googleapis.com/auth/youtube.upload
       - https://www.googleapis.com/auth/youtube
    4. Make sure app is in "Testing" or "Production"
    """)
    
    # 2. التحقق من YouTube Data API v3
    print("\n2️⃣ Checking YouTube Data API v3...")
    print("YouTube Data API v3 must be enabled")
    
    fixes.append("""
    🔧 FIX 2: Enable YouTube Data API v3
    ------------------------------------
    1. Go to Google Cloud Console
    2. Navigate to "APIs & Services" > "Library"
    3. Search for "YouTube Data API v3"
    4. Click "Enable"
    5. Wait a few minutes for changes to propagate
    """)
    
    # 3. التحقق من Quota
    print("\n3️⃣ Checking API Quota...")
    print("Free tier has 10,000 units per day")
    print("Uploading a video costs ~1600 units")
    
    fixes.append("""
    🔧 FIX 3: Check Quota Usage
    ---------------------------
    1. Go to Google Cloud Console
    2. Navigate to "APIs & Services" > "Dashboard"
    3. Check "YouTube Data API v3" quota usage
    4. If quota exceeded:
       - Wait until quota resets (daily)
       - Or upgrade to paid plan
    """)
    
    # 4. التحقق من OAuth Credentials
    print("\n4️⃣ Checking OAuth Credentials...")
    
    credentials_needed = [
        'YT_CLIENT_ID_1',
        'YT_CLIENT_SECRET_1', 
        'YT_REFRESH_TOKEN_1'
    ]
    
    for cred in credentials_needed:
        if os.getenv(cred):
            print(f"   ✅ {cred}: Present")
        else:
            print(f"   ❌ {cred}: Missing")
    
    fixes.append("""
    🔧 FIX 4: Get OAuth Credentials
    -------------------------------
    1. Go to Google Cloud Console
    2. Navigate to "APIs & Services" > "Credentials"
    3. Click "Create Credentials" > "OAuth 2.0 Client IDs"
    4. Choose "Desktop app" or "Web application"
    5. Download the JSON file
    6. Extract:
       - client_id
       - client_secret
       - refresh_token (requires OAuth flow)
    7. Add to GitHub Secrets:
       - YT_CLIENT_ID_1
       - YT_CLIENT_SECRET_1
       - YT_REFRESH_TOKEN_1
    """)
    
    # 5. التحقق من OAuth Token Flow
    print("\n5️⃣ Checking OAuth Token Flow...")
    
    fixes.append("""
    🔧 FIX 5: Get Refresh Token (If Missing)
    ----------------------------------------
    1. Run this Python code to get authorization URL:
    
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    CLIENT_SECRETS_FILE = "client_secret.json"
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    
    credentials = flow.run_local_server(port=0)
    print(f"Refresh token: {credentials.refresh_token}")
    
    2. Copy the refresh token to YT_REFRESH_TOKEN_1
    """)
    
    # عرض جميع الإصلاحات
    print("\n" + "=" * 60)
    print("🔧 RECOMMENDED FIXES:")
    print("=" * 60)
    
    for i, fix in enumerate(fixes, 1):
        print(fix)
        if i < len(fixes):
            print("-" * 40)
    
    # إنشاء ملف تعليمات
    with open('youtube_fix_instructions.txt', 'w') as f:
        f.write("YouTube Upload Fix Instructions\n")
        f.write("=" * 50 + "\n\n")
        for fix in fixes:
            f.write(fix + "\n\n")
    
    print("\n📄 Instructions saved to: youtube_fix_instructions.txt")
    print("\n🎯 NEXT ACTIONS:")
    print("1. Run: python get_refresh_token.py (if needed)")
    print("2. Update GitHub Secrets with correct values")
    print("3. Run test_upload.py to verify")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    fix_youtube_issues()
