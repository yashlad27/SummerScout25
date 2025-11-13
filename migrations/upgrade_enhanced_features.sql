-- Database migration for enhanced job tracker features
-- Run this after building the Docker image with new dependencies

-- Add enhanced job metadata columns
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS tech_stack JSONB;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS required_skills VARCHAR(255)[];
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS compensation_min INTEGER;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS compensation_max INTEGER;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS visa_sponsorship BOOLEAN;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS application_deadline VARCHAR(100);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS duration VARCHAR(100);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS start_date VARCHAR(100);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS seniority_level VARCHAR(50);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS ai_confidence INTEGER;

-- Add application tracking columns
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS application_status VARCHAR(50);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS applied_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS notes TEXT;

-- Create URL health monitoring table
CREATE TABLE IF NOT EXISTS url_health (
    company VARCHAR(255) NOT NULL,
    ats_type VARCHAR(50) NOT NULL,
    url TEXT,
    last_success TIMESTAMP WITH TIME ZONE,
    last_failure TIMESTAMP WITH TIME ZONE,
    failure_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_error TEXT,
    status VARCHAR(50) DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (company, ats_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_tech_stack ON jobs USING GIN (tech_stack);
CREATE INDEX IF NOT EXISTS idx_jobs_required_skills ON jobs USING GIN (required_skills);
CREATE INDEX IF NOT EXISTS idx_jobs_visa_sponsorship ON jobs (visa_sponsorship) WHERE visa_sponsorship IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_application_status ON jobs (application_status);
CREATE INDEX IF NOT EXISTS idx_jobs_seniority_level ON jobs (seniority_level);

CREATE INDEX IF NOT EXISTS idx_url_health_status ON url_health (status);
CREATE INDEX IF NOT EXISTS idx_url_health_failure_count ON url_health (failure_count);

-- Update existing jobs with default application status
UPDATE jobs SET application_status = 'not_applied' WHERE application_status IS NULL AND is_active = TRUE;

COMMENT ON COLUMN jobs.tech_stack IS 'JSON object with languages, frameworks, and tools mentioned in job description';
COMMENT ON COLUMN jobs.required_skills IS 'Array of extracted skills from job description';
COMMENT ON COLUMN jobs.ai_confidence IS 'AI classification confidence score 0-100';
COMMENT ON COLUMN jobs.application_status IS 'Tracking: not_applied, applied, interviewing, offer, rejected';
COMMENT ON TABLE url_health IS 'Health monitoring for job source URLs';
