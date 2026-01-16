-- Supabase 마이그레이션: 카테고리 및 우선순위 컬럼 추가
-- 실행 날짜: 2026-01-17

-- 기존 processed_articles 테이블에 새 컬럼 추가
ALTER TABLE processed_articles 
ADD COLUMN IF NOT EXISTS category TEXT,
ADD COLUMN IF NOT EXISTS priority TEXT;

-- 인덱스 추가 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_category ON processed_articles(category);
CREATE INDEX IF NOT EXISTS idx_priority ON processed_articles(priority);
CREATE INDEX IF NOT EXISTS idx_created_at ON processed_articles(created_at DESC);

-- 확인용 쿼리 (선택사항)
-- SELECT * FROM processed_articles LIMIT 5;
