---
trigger: always_on
---

프로젝트: Vibe-Based RSS Collector
목표: 서버 관리 없이 GitHub Actions와 AI 프롬프팅만으로 운영되는 개인용 RSS 수집 및 알림 시스템 구축

🛠️ 기술 스택 (Tech Stack)
언어: Python 3.x

패키지: feedparser (RSS 파싱), requests (Webhook/API 호출)

데이터베이스: Supabase (PostgreSQL) - 기사 중복 방지 저장소

자동화: GitHub Actions (Cron 스케줄러)

알림 채널: Discord Webhook (1차), Resend API (이메일 확장)

📜 바이브 코딩 원칙 (Prompting Rules)

1. 원자적 기능 구현 (Atomic Logic)
   프롬프트는 한 번에 하나의 기능만 구현하도록 지시한다. (예: "피드 읽기" 따로, "DB 저장" 따로)

모든 함수는 단일 책임 원칙을 지키며, 나중에 이메일이나 다른 알림 수단이 추가될 수 있도록 모듈화된 코드를 지향한다.

2. 상태 저장 및 중복 방지 (State Management)
   수집된 모든 기사의 link 또는 entry_id는 Supabase의 processed_articles 테이블에 저장되어야 한다.

이미 DB에 존재하는 https://www.google.com/search?q=%EB%A7%81%ED%81%AC는 알림을 보내지 않는 로직을 필수적으로 포함한다.

3. 무상태성 서버리스 (Stateless Execution)
   이 코드는 고정된 서버가 아닌 GitHub Actions 환경에서 실행됨을 전제로 한다.

로컬 파일 저장 방식이 아닌, 반드시 외부 DB(Supabase)를 통해 상태를 관리한다.

4. 보안 및 환경 변수 (Security)
   API Key, DB URL, Webhook URL 등은 절대 코드에 직접 노출하지 않는다.

os.environ.get()을 사용하여 환경 변수에서 불러오도록 작성하며, GitHub Secrets 설정을 항상 염두에 둔다.

🚀 구현 단계 (Step-by-Step Prompts)
Phase 1: 파서 및 DB 연동
"Python으로 RSS 피드 리스트(FEED_URLS)를 순회하며 제목과 https://www.google.com/search?q=%EB%A7%81%ED%81%AC를 가져오는 코드를 짜줘. 가져온 데이터는 Supabase의 articles 테이블과 비교해서 새로운 글일 때만 리스트에 담아야 해."

Phase 2: 알림 시스템 구축
"새로 발견된 기사 리스트를 Discord Webhook으로 전송하는 기능을 추가해줘. 메시지 형식은 기사 제목 형태의 마크다운으로 구성해줘."

Phase 3: 자동화 배포
"이 스크립트를 한국 시간 기준 매일 오전 9시와 오후 6시에 실행하는 GitHub Actions 워크플로우(.github/workflows/main.yml)를 만들어줘. 필요한 시크릿 변수는 SUPABASE_URL, SUPABASE_KEY, DISCORD_WEBHOOK_URL이야."

⚠️ 주의 사항
Rate Limit: RSS 피드 제공처의 차단을 방지하기 위해 너무 잦은 주기(예: 1분 단위)의 스케줄링은 피한다.

Error Handling: 피드가 일시적으로 응답하지 않더라도 스크립트 전체가 실패하지 않도록 try-except 예외 처리를 포함한다.
