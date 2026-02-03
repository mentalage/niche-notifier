-- Supabase 마이그레이션: GICS 하위 카테고리 및 AI 요약 필드 추가
-- 실행 날짜: 2026-02-03
-- 설명: 주식/경제 카테고리를 GICS 섹터별로 분류하고, 향후 AI 요약 기능을 위한 필드 추가

-- ============================================
-- processed_articles 테이블 컬럼 추가
-- ============================================

-- subcategory: GICS 섹터 또는 사용자 정의 하위 카테고리
-- 예: "Information Technology", "Financials", "Health Care" 등
ALTER TABLE processed_articles
ADD COLUMN IF NOT EXISTS subcategory TEXT;

-- summary: AI 생성 요약 텍스트 (향후 AI 요약 기능 대비)
ALTER TABLE processed_articles
ADD COLUMN IF NOT EXISTS summary TEXT;

-- summary_status: 요약 생성 상태
-- 가능한 값: NULL (시작 전), 'pending' (대기 중), 'completed' (완료), 'failed' (실패)
ALTER TABLE processed_articles
ADD COLUMN IF NOT EXISTS summary_status TEXT
CHECK (summary_status IS NULL OR summary_status IN ('pending', 'completed', 'failed'));

-- ============================================
-- 인덱스 생성 (성능 최적화)
-- ============================================

-- subcategory 인덱스 (GICS 섹터별 필터링 성능 향상)
CREATE INDEX IF NOT EXISTS idx_subcategory ON processed_articles(subcategory);

-- summary_status 인덱스 (요약 대기 중인 기사 조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_summary_status ON processed_articles(summary_status);

-- summary 인덱스 (요약이 있는 기사 조회)
CREATE INDEX IF NOT EXISTS idx_summary ON processed_articles(summary)
WHERE summary IS NOT NULL;

-- ============================================
-- 복합 인덱스 (자주 사용되는 조합)
-- ============================================

-- category + subcategory 조합 인덱스
CREATE INDEX IF NOT EXISTS idx_category_subcategory ON processed_articles(category, subcategory);

-- summary_status + created_at 조합 인덱스 (요약 대기열 처리용)
CREATE INDEX IF NOT EXISTS idx_summary_status_created_at ON processed_articles(summary_status, created_at DESC)
WHERE summary_status = 'pending';

-- ============================================
-- GICS 섹터 기존 데이터 마이그레이션 (선택사항)
-- ============================================

-- 기존 "주식/경제" 카테고리 데이터를 적절한 GICS 섹터로 분류
-- 참고: 실제 키워드 분석 기반 분류는 별도 스크립트가 필요할 수 있음

-- Information Technology 관련 기사
UPDATE processed_articles
SET subcategory = 'Information Technology'
WHERE category IN ('정보기술', '주식/경제')
  AND (
    title ILIKE '%NVIDIA%' OR title ILIKE '%엔비디아%'
    OR title ILIKE '%Apple%' OR title ILIKE '%애플%'
    OR title ILIKE '%Microsoft%' OR title ILIKE '%마이크로소프트%'
    OR title ILIKE '%Google%' OR title ILIKE '%구글%'
    OR title ILIKE '%반도체%' OR title ILIKE '%Semiconductor%'
    OR title ILIKE '%AI주%' OR title ILIKE '%Chip%'
    OR title ILIKE '%TSMC%' OR title ILIKE '%AMD%' OR title ILIKE '%Intel%'
    OR title ILIKE '%소프트웨어%' OR title ILIKE '%Software%'
    OR title ILIKE '%클라우드%' OR title ILIKE '%Cloud%'
  );

-- Financials 관련 기사
UPDATE processed_articles
SET subcategory = 'Financials'
WHERE category IN ('금융', '주식/경제')
  AND (
    title ILIKE '%JPMorgan%' OR title ILIKE '%Bank of America%'
    OR title ILIKE '%비자%' OR title ILIKE '%Visa%'
    OR title ILIKE '%마스터카드%' OR title ILIKE '%Mastercard%'
    OR title ILIKE '%은행%' OR title ILIKE '%Bank%'
    OR title ILIKE '%금리%' OR title ILIKE '%Fed%'
    OR title ILIKE '%ETF%'
  );

-- Health Care 관련 기사
UPDATE processed_articles
SET subcategory = 'Health Care'
WHERE category IN ('헬스케어', '주식/경제')
  AND (
    title ILIKE '%Johnson & Johnson%' OR title ILIKE '%Pfizer%' OR title ILIKE '%화이자%'
    OR title ILIKE '%Moderna%' OR title ILIKE '%모더나%'
    OR title ILIKE '%바이오%' OR title ILIKE '%Bio%'
    OR title ILIKE '%제약%' OR title ILIKE '%Pharma%'
  );

-- Energy 관련 기사
UPDATE processed_articles
SET subcategory = 'Energy'
WHERE category IN ('에너지', '주식/경제')
  AND (
    title ILIKE '%Exxon%' OR title ILIKE '%Chevron%'
    OR title ILIKE '%원유%' OR title ILIKE '%Crude Oil%'
    OR title ILIKE '%천연가스%' OR title ILIKE '%Natural Gas%'
    OR title ILIKE '%석유%' OR title ILIKE '%Oil%'
  );

-- ============================================
-- 확인용 쿼리 (선택사항)
-- ============================================

-- 테이블 스키마 확인
-- \d processed_articles

-- 추가된 컬럼 확인
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'processed_articles'
--   AND column_name IN ('subcategory', 'summary', 'summary_status')
-- ORDER BY ordinal_position;

-- GICS 섹터별 기사 수 확인
-- SELECT subcategory, COUNT(*) as count
-- FROM processed_articles
-- WHERE subcategory IS NOT NULL
-- GROUP BY subcategory
-- ORDER BY count DESC;

-- 요약 상태별 기사 수 확인
-- SELECT summary_status, COUNT(*) as count
-- FROM processed_articles
-- GROUP BY summary_status
-- ORDER BY summary_status;
