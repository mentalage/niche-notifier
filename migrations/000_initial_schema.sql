-- Supabase 초기 테이블 생성 (신규 사용자용)
-- 카테고리 기반 RSS 관리 시스템

CREATE TABLE processed_articles (
  id SERIAL PRIMARY KEY,
  link TEXT UNIQUE NOT NULL,
  title TEXT,
  published_at TIMESTAMP,
  category TEXT,
  priority TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성 (성능 향상)
CREATE INDEX idx_category ON processed_articles(category);
CREATE INDEX idx_priority ON processed_articles(priority);
CREATE INDEX idx_created_at ON processed_articles(created_at DESC);
CREATE INDEX idx_link ON processed_articles(link);

-- 확인용 쿼리 (선택사항)
-- SELECT * FROM processed_articles LIMIT 5;
