-- RSS Feeds 관리 테이블
-- 향후 웹 UI를 통해 피드를 추가/삭제/수정할 수 있도록 구성

CREATE TABLE feeds (
  id SERIAL PRIMARY KEY,
  url TEXT UNIQUE NOT NULL,
  name TEXT,
  category TEXT NOT NULL,
  enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  last_fetched_at TIMESTAMP
);

-- 인덱스 생성 (성능 향상)
CREATE INDEX idx_feeds_category ON feeds(category);
CREATE INDEX idx_feeds_enabled ON feeds(enabled);

-- 초기 피드 데이터 삽입 (선택사항 - config.py에서 관리되는 피드들)
-- INSERT INTO feeds (url, name, category) VALUES
--   ('https://hnrss.org/show', 'Hacker News Show', '개발'),
--   ('https://hnrss.org/newest?q=AI', 'Hacker News AI', '개발'),
--   ('https://hnrss.org/best', 'Hacker News Best', '개발'),
--   ('https://feeds.feedburner.com/geeknews-feed', 'GeekNews', '개발'),
--   ('https://rss.blog.naver.com/ranto28.xml', '개인 블로그', '블로그');
