# Notify Niche - RSS Collector

Python + Supabase + Discord Webhook 기반의 **카테고리별 RSS 수집 및 알림 시스템**입니다.
GitHub Actions를 통해 서버 없이 자동으로 운영됩니다.

## 🚀 Features

- **카테고리 기반 수집**: 개발, 블로그 등 카테고리별로 피드 관리
- **키워드 필터링**: 우선순위(High/Medium/Low) 및 제외 키워드 설정 가능
- **중복 방지**: Supabase를 통해 이미 처리된 기사 제외
- **Discord 알림**: 카테고리별로 그룹화된 깔끔한 마크다운 알림
- **서버리스 운영**: GitHub Actions를 통한 자동 스케줄링

## 📦 Setup

### 1. Supabase 설정

[Supabase](https://supabase.com)에서 프로젝트를 생성하고 `migrations/` 폴더의 SQL 파일들을 순서대로 실행하거나 아래 통합 SQL을 실행하세요:

```sql
CREATE TABLE processed_articles (
  id SERIAL PRIMARY KEY,
  link TEXT UNIQUE NOT NULL,
  title TEXT,
  category TEXT,
  priority TEXT,
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

### 4. RSS 피드 및 필터 설정

`src/config.py`의 `FEED_CATEGORIES` 딕셔너리를 수정하여 카테고리, 피드 URL, 키워드 필터를 설정하세요.

```python
FEED_CATEGORIES = {
    "개발": {
        "enabled": True,
        "emoji": "💻",
        "feeds": ["https://hnrss.org/show"],
        "keyword_filters": {
            "enabled": True,
            "high_priority": ["AI", "GPT"],
            "exclude": ["광고"]
        }
    }
}
```

## 🛠️ Local Development

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (SUPABASE_URL, SUPABASE_KEY, DISCORD_WEBHOOK_URL)

# 실행
python -m src.main
```

## 🧪 Local Testing

```bash
# 모든 테스트 실행
pytest

# 상세한 출력과 함께 실행
pytest -v
```

### 테스트 구조

- `tests/test_parser.py`: RSS 파싱 및 키워드 필터링 테스트
- `tests/test_db.py`: Supabase DB 연동 테스트
- `tests/test_notifier.py`: Discord 알림 형식 테스트

## 📁 Project Structure

```
notify-niche/
├── src/
│   ├── config.py      # 카테고리 및 키워드 설정
│   ├── parser.py      # RSS 파싱 및 필터링 로직
│   ├── db.py          # Supabase 연동 (중복 방지)
│   ├── notifier.py    # Discord 알림 (카테고리 그룹화)
│   └── main.py        # 메인 워크플로우 오케스트레이션
├── api/               # FastAPI Backend (Web UI용)
│   ├── main.py        # FastAPI 앱 진입점
│   ├── schemas.py     # Pydantic 모델
│   └── routers/       # API 라우터
├── web/               # React Frontend
│   ├── src/
│   │   ├── App.jsx    # 메인 앱 컴포넌트
│   │   └── components/ # UI 컴포넌트
│   └── package.json
├── .github/workflows/
│   └── main.yml       # GitHub Actions 자동화 설정
├── migrations/        # DB 스키마 변경 이력
├── tests/             # 테스트 코드
├── plans/             # 기능 구현 설계 문서
├── requirements.txt
└── pyproject.toml
```

## 🖥️ Web Client (Optional)

피드 관리를 위한 웹 UI를 제공합니다.

### Backend 실행

```bash
# FastAPI 서버 시작
uvicorn api.main:app --reload
```

- API 서버: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Frontend 실행

```bash
cd web
npm install
npm run dev
```

- 웹 앱: http://localhost:5173

### 주요 기능

- **피드 관리**: CRUD 작업 (추가, 수정, 삭제, 활성화 토글)
- **최근 기사**: 수집된 기사 목록 확인
- **Discord 미리보기**: 알림이 어떻게 표시될지 미리 확인

## 📄 License

MIT
