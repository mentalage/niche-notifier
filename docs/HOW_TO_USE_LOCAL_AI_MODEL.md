# 로컬 AI 모델로 요약 서비스 실행하기

이 문서는 Ollama를 사용하여 로컬 AI 모델로 기사 요약 서비스를 실행하는 방법을 설명합니다.

## 목차

1. [Ollama란?](#ollama란)
2. [Docker로 Ollama 실행](#docker로-ollama-실행)
3. [추천 모델](#추천-모델)
4. [프로젝트 설정](#프로젝트-설정)
5. [테스트](#테스트)
6. [장단점](#장단점)
7. [문제 해결](#문제-해결)

---

## Ollama란?

**Ollama**는 로컬 환경에서 대형 언어 모델(LLM)을 실행할 수 있는 오픈소스 도구입니다.

- 완전 로컬 실행 (인터넷 연결 불필요)
- 무료 API 호출
- 데이터 프라이버시 보장
- 다양한 모델 지원 (Llama, Mistral, Gemma, 등)

---

## Docker로 Ollama 실행

### 1. Docker Compose 파일 실행

Docker Compose 파일은 `docker/docker-compose.ollama.yml`에 이미 있습니다.

### 2. Ollama 컨테이너 실행

```bash
# Windows (Git Bash)
docker-compose -f docker/docker-compose.ollama.yml up -d

# Linux/Mac
docker compose -f docker/docker-compose.ollama.yml up -d
```

### 3. 모델 다운로드

컨테이너 내에서 모델을 다운로드합니다:

```bash
# 컨테이너에 접속
docker exec -it niche-notifier-ollama bash

# 모델 다운로드 (예: gemma2:9b)
ollama pull gemma2:9b

# 또는 llama3.1
ollama pull llama3.1

# 다른 모델 탐색
ollama list
```

### 4. Ollama 동작 테스트

```bash
# 로컬에서 테스트
curl http://localhost:11434/api/generate -d '{
  "model": "gemma2:9b",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

---

## 추천 모델

### 한국어 요약에 적합한 모델

| 모델           | 크기  | RAM   | 특징                   | 다운로드 명령어          |
| -------------- | ----- | ----- | ---------------------- | ------------------------ |
| **gemma2:9b**  | ~9GB  | 16GB  | 한국어 지원 우수, 빠름 | `ollama pull gemma2:9b`  |
| **llama3.1**   | ~8GB  | 16GB  | 다국어 지원, 균형잡힘  | `ollama pull llama3.1`   |
| **mistral**    | ~7GB  | 14GB  | 가벼움, 빠른 응답      | `ollama pull mistral`    |
| **gemma2:27b** | ~27GB | 32GB+ | 최고 품질, 느림        | `ollama pull gemma2:27b` |

### 추천: gemma2:9b

```bash
ollama pull gemma2:9b
```

- 한국어 성능이 우수함
- 16GB RAM 환경에서 적절히 작동
- 응답 속도가 빠름

---

## 프로젝트 설정

### 1. 환경 변수 추가

`.env` 파일에 Ollama 관련 설정을 추가합니다:

```bash
# .env 파일

# 기존 설정
SUPABASE_URL="your-supabase-url"
SUPABASE_KEY="your-supabase-key"
DISCORD_WEBHOOK_URL="your-discord-webhook-url"

# AI 요약 설정 (Ollama 로컬 모델 사용)
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="gemma2:9b"

# Gemini API는 비워둠 (Ollama 사용 시)
GEMINI_API_KEY=""
```

### 2. summarizer.py 수정

`src/summarizer.py` 파일에 Ollama API 호출 기능을 추가합니다.

기존 `generate_summary_gemini()` 함수 아래에 다음 함수를 추가:

```python
# ============================================
# Ollama Local Model Integration
# ============================================

def get_ollama_base_url() -> str:
    """Get Ollama base URL from environment (default: http://localhost:11434)."""
    return get_env_var("OLLAMA_BASE_URL", required=False) or "http://localhost:11434"


def get_ollama_model() -> str:
    """Get Ollama model name from environment (default: gemma2:9b)."""
    return get_env_var("OLLAMA_MODEL", required=False) or "gemma2:9b"


def generate_summary_ollama(title: str, content: str) -> Optional[str]:
    """Generate summary using local Ollama model.

    Args:
        title: Article title
        content: Article content

    Returns:
        Generated summary or None if failed
    """
    base_url = get_ollama_base_url()
    model = get_ollama_model()
    prompt = build_summary_prompt(title, content)

    url = f"{base_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 300,
            "temperature": 0.7,
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()

            # Extract summary from response
            try:
                summary = data.get("response", "").strip()

                # Clean up common prefixes
                summary = re.sub(r'^(Summary:|요약:|요약\s*)', '', summary).strip()

                # Limit length
                if len(summary) > 300:
                    summary = summary[:297] + "..."

                return summary
            except Exception as e:
                print(f"Error parsing Ollama response: {e}")
                print(f"Response data: {data}")
                return None
        else:
            print(f"Ollama API returned status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        return None
```

### 3. ArticleSummarizer 클래스 수정

`ArticleSummarizer` 클래스의 `__init__` 메서드와 `summarize_article` 메서드를 수정:

```python
class ArticleSummarizer:
    """Main class for article summarization."""

    def __init__(self, enable_content_extraction: bool = True):
        """Initialize summarizer.

        Args:
            enable_content_extraction: If False, only summarize title/description
        """
        self.enable_content_extraction = enable_content_extraction
        self.api_key = get_gemini_api_key()
        self.ollama_base_url = get_ollama_base_url()

    def summarize_article(
        self,
        title: str,
        url: str,
        description: str = ""
    ) -> Optional[str]:
        """Generate summary for an article.

        Args:
            title: Article title
            url: Article URL
            description: Article description (from RSS feed)

        Returns:
            Generated summary or None if failed
        """
        # Try to extract full content if enabled
        content = ""

        if self.enable_content_extraction and url:
            content = extract_article_content(url)

        # Fall back to description if content extraction failed
        if not content:
            content = description or title

        # If we only have title, use it as content
        if not content:
            content = title

        # Generate summary: Try Ollama first, then Gemini
        summary = None

        # 1. Try Ollama (local model)
        if self.ollama_base_url:
            summary = generate_summary_ollama(title, content)
            if summary:
                print(f"Generated summary with Ollama for: {title}")
                return summary

        # 2. Fall back to Gemini API
        if self.api_key:
            summary = generate_summary_gemini(title, content)
            if summary:
                print(f"Generated summary with Gemini for: {title}")
                return summary

        return None
```

---

## 테스트

### 1. 수동 테스트

```bash
# Poetry 사용
poetry run python -c "
from src.summarizer import ArticleSummarizer

summarizer = ArticleSummarizer()
result = summarizer.summarize_article(
    title='Ollama 로컬 모델 테스트',
    url='https://example.com/test',
    description='이것은 테스트 기사입니다.'
)
print('Summary:', result)
"

# pip 사용
python -c "
from src.summarizer import ArticleSummarizer

summarizer = ArticleSummarizer()
result = summarizer.summarize_article(
    title='Ollama 로컬 모델 테스트',
    url='https://example.com/test',
    description='이것은 테스트 기사입니다.'
)
print('Summary:', result)
"
```

### 2. 전체 파이프라인 테스트

```bash
# 전체 RSS 수집 및 요약 테스트
poetry run python -m src.main
```

### 3. Ollama 로그 확인

```bash
# Ollama 컨테이너 로그 확인
docker logs niche-notifier-ollama -f

# 또는 docker-compose 사용
docker-compose -f docker-compose.ollama.yml logs -f
```

---

## 장단점

### 장점

- **비용 절감**: API 호출 비용 0원
- **프라이버시**: 기사 내용이 외부로 전송되지 않음
- **무제한 호출**: Rate limiting 없음
- **오프라인 작동**: 인터넷 연결 없이도 사용 가능
- **커스터마이징**: 모델 파인튜닝 가능

### 단점

- **하드웨어 요구사항**: 최소 16GB RAM 권장
- **응답 속도**: 클라우드 API보다 느릴 수 있음
- **모델 관리**: 모델 다운로드 및 업데이트 필요
- **품질 차이**: 최신 클라우드 모델보다 성능이 낮을 수 있음

---

## 문제 해결

### Ollama 연결 실패

```bash
# Ollama 컨테이너가 실행 중인지 확인
docker ps | grep ollama

# 컨테이너 재시작
docker restart niche-notifier-ollama
```

### 메모리 부족

```bash
# 더 작은 모델 사용
ollama pull gemma2:2b

# .env 파일에서 모델 변경
OLLAMA_MODEL="gemma2:2b"
```

### 응답 속도가 느린 경우

```python
# Ollama API 호출 시 파라미터 조정
payload = {
    "model": model,
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_predict": 150,  # 출력 토큰 수 줄이기
        "temperature": 0.5,  # 낮추어 더 결정적인 응답
        "num_ctx": 2048,     # 컨텍스트 크기 줄이기
    }
}
```

### Docker GPU 설정 (NVIDIA)

```yaml
# docker-compose.ollama.yml
services:
  ollama:
    image: ollama/ollama:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 추가 리소스

- [Ollama 공식 문서](https://github.com/ollama/ollama)
- [지원되는 모델 목록](https://ollama.com/library)
- [Ollama API 문서](https://github.com/ollama/ollama/blob/main/docs/api.md)

---

## 요약

1. Docker로 Ollama 컨테이너 실행
2. `ollama pull gemma2:9b`로 모델 다운로드
3. `.env` 파일에 `OLLAMA_BASE_URL`과 `OLLAMA_MODEL` 설정
4. `summarizer.py`에 Ollama API 호출 코드 추가
5. `poetry run python -m src.main`로 테스트
