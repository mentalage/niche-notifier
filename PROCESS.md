# 로컬 테스트 프로세스

로컬 환경에서 Discord Webhook이 실제로 작동하는지 확인하는 전체 절차입니다.

## 📋 사전 준비

### 1. Discord Webhook URL 발급

1. Discord 서버의 **서버 설정** 열기
2. **연동** → **웹훅** 메뉴로 이동
3. **새 웹훅** 버튼 클릭
4. 웹훅 이름 설정 (예: "Notify Niche Bot")
5. 알림을 받을 채널 선택
6. **웹훅 URL 복사** 버튼 클릭하여 URL 복사

### 2. Supabase 프로젝트 설정

1. [Supabase](https://supabase.com)에서 프로젝트 생성
2. SQL 에디터에서 다음 쿼리 실행:

```sql
CREATE TABLE processed_articles (
  id SERIAL PRIMARY KEY,
  link TEXT UNIQUE NOT NULL,
  title TEXT,
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

3. **Settings** → **API** 메뉴에서 다음 정보 복사:
   - Project URL (SUPABASE_URL)
   - `anon` `public` key (SUPABASE_KEY)

## 🔧 로컬 환경 설정

### 1. 환경 변수 파일 생성

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env
```

### 2. `.env` 파일 편집

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Discord Webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
```

> ⚠️ **주의**: `.env` 파일은 `.gitignore`에 포함되어 있으므로 Git에 커밋되지 않습니다.

### 3. RSS 피드 설정

`src/config.py` 파일을 열어 `FEED_URLS` 리스트에 테스트할 RSS 피드 추가:

```python
FEED_URLS = [
    "https://news.ycombinator.com/rss",  # 예시: Hacker News
]
```

## ✅ 테스트 실행

### 방법 1: 전체 워크플로우 테스트 (권장)

전체 프로세스를 실행하여 RSS 파싱부터 Discord 알림까지 모두 테스트:

```bash
python -m src.main
```

**예상 출력**:

```
=== Notify Niche RSS Collector ===
Processing 1 feeds...
Total articles parsed: 30
Successfully sent notification for 5 articles
Saved 5/5 new articles to database
=== Execution complete ===
```

**확인 사항**:

- ✅ Discord 채널에 새 기사 알림이 도착했는지 확인
- ✅ Supabase 대시보드에서 `processed_articles` 테이블에 데이터가 저장되었는지 확인

### 방법 2: 단위 테스트로 검증

Mock을 사용한 단위 테스트로 코드 로직만 검증 (실제 알림은 전송되지 않음):

```bash
# 모든 테스트 실행
pytest

# Discord 알림 관련 테스트만 실행
pytest tests/test_notifier.py -v
```

### 방법 3: 간단한 Webhook 테스트 스크립트

Discord Webhook만 빠르게 테스트하려면 다음 스크립트 생성:

**`test_webhook.py`**:

```python
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
```

**실행**:
fe

```bash
python test_webhook.py
```

## 🐛 문제 해결

### Discord에 알림이 오지 않는 경우

1. **환경 변수 확인**:

   ```bash
   # Python REPL에서 확인
   python
   >>> from src.config import get_discord_webhook_url
   >>> print(get_discord_webhook_url())
   ```

2. **Webhook URL 형식 확인**:

   - 올바른 형식: `https://discord.com/api/webhooks/{webhook_id}/{webhook_token}`
   - URL에 불필요한 공백이나 줄바꿈이 없는지 확인

3. **Discord Webhook이 활성 상태인지 확인**:
   - Discord 서버 설정 → 연동 → 웹훅에서 해당 웹훅이 존재하는지 확인

### Supabase 연결 오류

1. **환경 변수 확인**:

   ```bash
   python
   >>> from src.config import get_supabase_url, get_supabase_key
   >>> print(get_supabase_url())
   >>> print(get_supabase_key()[:20] + "...")  # 일부만 출력
   ```

2. **네트워크 연결 확인**:

   - Supabase 대시보드에 접속 가능한지 확인

3. **테이블 존재 여부 확인**:
   - Supabase 대시보드 → Table Editor에서 `processed_articles` 테이블 확인

### RSS 피드 파싱 오류

1. **피드 URL 유효성 확인**:

   ```bash
   # 브라우저나 curl로 직접 접근
   curl https://your-rss-feed-url
   ```

2. **feedparser 설치 확인**:
   ```bash
   pip list | grep feedparser
   ```

## 📊 결과 확인

### Discord 채널에서 확인

알림 메시지 형식:

```
📰 **새로운 기사가 도착했습니다!**

• [기사 제목 1](링크)
• [기사 제목 2](링크)
• [기사 제목 3](링크)

총 3개의 새 기사
```

### Supabase 대시보드에서 확인

1. Supabase 프로젝트 대시보드 접속
2. **Table Editor** → `processed_articles` 선택
3. 저장된 기사 데이터 확인:
   - `link`: 기사 URL
   - `title`: 기사 제목
   - `created_at`: 저장 시간

### 재실행 테스트

중복 방지 기능 확인:

```bash
# 동일한 명령 다시 실행
python -m src.main
```

**예상 출력**:

```
=== Notify Niche RSS Collector ===
Processing 1 feeds...
Total articles parsed: 30
No new articles to process
=== Execution complete ===
```

이미 처리된 기사는 다시 알림이 가지 않아야 합니다.

## 🎯 체크리스트

로컬 테스트 완료를 위한 체크리스트:

- [ ] Discord Webhook URL 발급 완료
- [ ] Supabase 프로젝트 및 테이블 생성 완료
- [ ] `.env` 파일 생성 및 환경 변수 설정 완료
- [ ] RSS 피드 URL 설정 완료
- [ ] `python -m src.main` 실행 성공
- [ ] Discord 채널에 알림 도착 확인
- [ ] Supabase 테이블에 데이터 저장 확인
- [ ] 재실행 시 중복 방지 동작 확인
- [ ] pytest 테스트 전체 통과 (`pytest`)

모든 항목이 체크되면 로컬 환경 설정이 완료됩니다! 🎉
