-- Add summary column to processed_articles table
-- This column stores AI-generated article summaries

ALTER TABLE processed_articles ADD COLUMN IF NOT EXISTS summary TEXT;

-- Optional: Add index for faster queries on articles with summaries
-- CREATE INDEX IF NOT EXISTS idx_articles_summary ON processed_articles (summary) WHERE summary IS NOT NULL;
