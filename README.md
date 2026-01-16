# Notify Niche - RSS Collector

Python + Supabase + Discord Webhook 기반의 RSS 수집 및 알림 시스템입니다.
GitHub Actions를 통해 서버 없이 자동으로 운영됩니다.

## 🚀 Features

- RSS 피드 자동 수집 (매일 오전 9시, 오후 6시 KST)
- Supabase를 통한 중복 방지
- Discord Webhook 알림
- 서버리스 운영 (GitHub Actions)

## 📦 Setup

### 1. Supabase 설정

[Supabase](https://supabase.com)에서 프로젝트를 생성하고 아래 SQL을 실행하세요:

```sql
CREATE TABLE processed_articles (
  id SERIAL PRIMARY KEY,
  link TEXT UNIQUE NOT NULL,
  title TEXT,
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Discord Webhook 생성

Discord 서버 설정 → 연동 → 웹훅에서 새 웹훅을 생성하세요.

### 3. GitHub Secrets 설정

Repository Settings → Secrets and variables → Actions에서 추가:

| Secret                | Description           |
| --------------------- | --------------------- |
| `SUPABASE_URL`        | Supabase 프로젝트 URL |
| `SUPABASE_KEY`        | Supabase anon key     |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL   |

### 4. RSS 피드 설정

`src/config.py`의 `FEED_URLS` 리스트에 수집할 RSS 피드 URL을 추가하세요.

## 🛠️ Local Development

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 실행
python -m src.main
```

## 🧪 Local Testing

### 테스트 환경 설정

```bash
# 의존성 설치 (테스트 도구 포함)
pip install -r requirements.txt

# pytest 설치 확인
pytest --version
```

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 상세한 출력과 함께 실행
pytest -v

# 특정 테스트 파일만 실행
pytest tests/test_parser.py

# 특정 테스트 클래스나 함수만 실행
pytest tests/test_notifier.py::TestSendDiscordNotification
pytest tests/test_notifier.py::TestSendDiscordNotification::test_send_notification_success

# 실패한 테스트만 다시 실행
pytest --lf

# 코드 커버리지 확인 (pytest-cov 설치 필요)
pytest --cov=src --cov-report=term-missing
```

### 테스트 구조

```
tests/
├── test_parser.py    # RSS 파싱 기능 테스트
├── test_db.py        # Supabase DB 연동 테스트
└── test_notifier.py  # Discord 알림 기능 테스트
```

### 주의사항

- 테스트는 외부 서비스 호출을 Mock으로 대체하므로 실제 API 키가 필요하지 않습니다
- `.env` 파일이 없어도 테스트 실행이 가능합니다
- 모든 테스트는 독립적으로 실행되며 서로 영향을 주지 않습니다

## 📁 Project Structure

```
notify-niche/
├── src/
│   ├── config.py    # 환경 변수 및 설정
│   ├── parser.py    # RSS 피드 파싱
│   ├── db.py        # Supabase 연동
│   ├── notifier.py  # Discord 알림
│   └── main.py      # 메인 실행
├── .github/workflows/
│   └── main.yml     # GitHub Actions
├── requirements.txt
└── pyproject.toml
```

## 📄 License

MIT
