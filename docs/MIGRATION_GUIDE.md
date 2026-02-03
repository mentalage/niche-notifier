# Database Migration Guide

이 문서는 Supabase 데이터베이스 migration을 실행하는 방법을 설명합니다.

## Migration 파일 목록

| 파일                                     | 설명                                  | 실행 날짜  |
| ---------------------------------------- | ------------------------------------- | ---------- |
| `000_initial_schema.sql`                 | 초기 테이블 생성 (processed_articles) | -          |
| `001_add_category_priority.sql`          | category, priority 컬럼 추가          | 2026-01-17 |
| `002_add_feeds_table.sql`                | feeds 테이블 생성                     | 2026-01-17 |
| `003_add_subcategory_summary_fields.sql` | GICS subcategory, AI 요약 필드 추가   | 2026-02-03 |

## Migration 실행 방법

### 방법 1: Supabase Dashboard (가장 간단)

1. [Supabase Dashboard](https://app.supabase.com)에 접속
2. 프로젝트 선택 → SQL Editor 클릭
3. `migrations/003_add_subcategory_summary_fields.sql` 내용을 복사하여 붙여넣기
4. `Run` 버튼 클릭

### 방법 2: Supabase CLI (권장)

```bash
# Supabase CLI 설치 (尚未 설치한 경우)
npm install -g supabase

# Supabase 프로젝트에 연결
supabase link --project-ref YOUR_PROJECT_REF

# Migration 실행
supabase db push

# 또는 특정 파일만 실행
psql "$(supabase status -o env | grep DB_URL)" -f migrations/003_add_subcategory_summary_fields.sql
```

### 방법 3: psql 명령줄

```bash
# 환경 변수 설정
export DB_HOST="your-project.supabase.co"
export DB_NAME="postgres"
export DB_USER="postgres"

# psql로 직접 실행
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f migrations/003_add_subcategory_summary_fields.sql
```

## Migration 003 상세 정보

### 추가되는 필드

#### `processed_articles` 테이블

| 컬럼             | 타입 | 설명                         | 예시                                   |
| ---------------- | ---- | ---------------------------- | -------------------------------------- |
| `subcategory`    | TEXT | GICS 섹터 또는 하위 카테고리 | "Information Technology", "Financials" |
| `summary`        | TEXT | AI 생성 요약 텍스트          | "이 기사는..."                         |
| `summary_status` | TEXT | 요약 생성 상태               | NULL, "pending", "completed", "failed" |

### 추가되는 인덱스

```sql
-- 단일 인덱스
idx_subcategory              -- subcategory 필터링용
idx_summary_status           -- 요약 상태 필터링용
idx_summary                  -- 요약이 있는 기사 조회용 (Partial Index)

-- 복합 인덱스
idx_category_subcategory                     -- category + subcategory 조합
idx_summary_status_created_at                -- 요약 대기열 처리용 (Partial Index)
```

### 기존 데이터 마이그레이션

이 migration은 기존 "주식/경제" 카테고리의 데이터를 키워드 기반으로 적절한 GICS 섹터로 분류합니다:

- **Information Technology**: NVIDIA, Apple, Microsoft, Google, 반도체, AI주, 소프트웨어, 클라우드 등
- **Financials**: JPMorgan, Visa, Mastercard, 은행, 금리, ETF 등
- **Health Care**: Johnson & Johnson, Pfizer, Moderna, 바이오, 제약 등
- **Energy**: Exxon, Chevron, 원유, 석유, 천연가스 등

## Migration 실행 후 확인

### 1. 테이블 스키마 확인

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'processed_articles'
  AND column_name IN ('subcategory', 'summary', 'summary_status')
ORDER BY ordinal_position;
```

### 2. 인덱스 확인

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'processed_articles'
  AND indexname LIKE 'idx_%';
```

### 3. GICS 섹터별 기사 수 확인

```sql
SELECT subcategory, COUNT(*) as count
FROM processed_articles
WHERE subcategory IS NOT NULL
GROUP BY subcategory
ORDER BY count DESC;
```

### 4. 요약 상태별 기사 수 확인

```sql
SELECT
    COALESCE(summary_status, 'NULL') as status,
    COUNT(*) as count
FROM processed_articles
GROUP BY summary_status
ORDER BY summary_status;
```

## 롤백 (Rollback)

Migration을 롤백해야 할 경우:

```sql
-- 컬럼 삭제
ALTER TABLE processed_articles DROP COLUMN IF EXISTS subcategory;
ALTER TABLE processed_articles DROP COLUMN IF EXISTS summary;
ALTER TABLE processed_articles DROP COLUMN IF EXISTS summary_status;

-- 인덱스 삭제
DROP INDEX IF EXISTS idx_subcategory;
DROP INDEX IF EXISTS idx_summary_status;
DROP INDEX IF EXISTS idx_summary;
DROP INDEX IF EXISTS idx_category_subcategory;
DROP INDEX IF EXISTS idx_summary_status_created_at;
```

## 다음 단계

Migration이 성공적으로 완료되면:

1. **API 테스트**: 새로운 필드가 포함된 API 응답 확인

   ```bash
   curl http://localhost:8000/api/articles?limit=5
   ```

2. **GICS 카테고리 확인**:

   ```bash
   curl http://localhost:8000/api/categories?parent=주식/경제
   ```

3. **AI 요약 기능 구현**: (향후 추가 예정)
   - `summary` 필드에 AI 생성 요약 저장
   - `summary_status`로 요약 진행 상태 관리

## 문제 해결

### Error: column already exists

이미 컬럼이 존재하는 경우, `IF NOT EXISTS` 구문으로 인해 무시됩니다.

### Error: permission denied

Supabase 프로젝트의 소유자 또는 적절한 권한이 있는 계정으로 실행하세요.

### Partial Index가 생성되지 않음

Partial Index는 조건에 맞는 데이터가 없어도 생성됩니다. 조건을 확인하세요:

```sql
-- summary partial index 확인
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'processed_articles'
  AND indexname = 'idx_summary';
```

## 추가 정보

- [Supabase Migration Guide](https://supabase.com/docs/guides/database/migrations)
- [PostgreSQL Partial Indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
- [GICS Official Site](https://www.msci.com/our-solutions/indexes/gics)
