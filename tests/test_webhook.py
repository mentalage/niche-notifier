"""Discord Webhook 간단 테스트 스크립트"""
import requests
from src.config import get_discord_webhook_url

def test_webhook():
    webhook_url = get_discord_webhook_url()
    
    message = {
        "content": "🧪 **테스트 메시지**\n\nNotify Niche 로컬 테스트가 성공적으로 작동하고 있습니다!"
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
        print("✅ Discord 알림 전송 성공!")
        print(f"응답 코드: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Discord 알림 전송 실패: {e}")
        return False

if __name__ == "__main__":
    test_webhook()
