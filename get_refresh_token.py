"""
الحصول على Refresh Token جديد لـ YouTube API
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

def get_refresh_token():
    """الحصول على refresh token جديد"""
    print("=" * 60)
    print("🔄 Getting YouTube API Refresh Token")
    print("=" * 60)
    
    # Scopes المطلوبة
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube"
    ]
    
    # مسار ملف credentials
    client_secrets_file = "client_secret.json"
    
    if not os.path.exists(client_secrets_file):
        print(f"❌ {client_secrets_file} not found!")
        print("\n📝 Please create client_secret.json with your OAuth 2.0 credentials:")
        print("""
        {
            "web": {
                "client_id": "YOUR_CLIENT_ID",
                "project_id": "YOUR_PROJECT_ID",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",
                "redirect_uris": ["http://localhost:8080/"]
            }
        }
        """)
        return False
    
    try:
        # إنشاء OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, 
            SCOPES
        )
        
        print("🌐 Opening browser for authentication...")
        print("Please authorize the app in your browser.")
        
        # تشغيل flow والحصول على credentials
        credentials = flow.run_local_server(port=8080)
        
        print("\n✅ Authentication successful!")
        print("\n📋 Credentials obtained:")
        print(f"   Client ID: {credentials.client_id[:20]}...")
        print(f"   Refresh Token: {credentials.refresh_token}")
        print(f"   Token Expiry: {credentials.expiry}")
        
        # حفظ refresh token
        refresh_token = credentials.refresh_token
        
        print("\n🔑 Add this to your GitHub Secrets:")
        print(f"   YT_REFRESH_TOKEN_1 = {refresh_token}")
        
        # حفظ token في ملف
        with open('refresh_token.txt', 'w') as f:
            f.write(refresh_token)
        
        print(f"\n📄 Refresh token saved to: refresh_token.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = get_refresh_token()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 REFRESH TOKEN OBTAINED SUCCESSFULLY!")
        print("Update your GitHub Secrets and run the automation again.")
    else:
        print("❌ FAILED TO GET REFRESH TOKEN")
    print("=" * 60)
