# Embed Content Improvement Plan

🔥 Show HN: Headroom (OSS): Cuts LLM costs by 85%
Article URL: https://github.com/chopratejas/headroom Comments URL: https://news.ycombinator.com/item?id=46663757 Points: 1 # Comments: 1
💻 개발

이런 구조로 embed가 되는데, 이제 어떤 뉴스에서 왔는지 저장할 필요가 있어.

`FEED_CATEGORIES`에서 각 `name`을 추가해줘

## 주의 사항

- db와 synk가 되어야 함(upsert 기능으로 기존 데이터 유지 및 이름만 update)
- description은 1000자 제한
- 하단에 `카테고리` - `이름` 으로 등록
