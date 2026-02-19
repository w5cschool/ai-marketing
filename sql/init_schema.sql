-- AI Email Marketing - Initial Schema (PostgreSQL / Supabase)

BEGIN;

-- Optional in Supabase (usually enabled by default), required for gen_random_uuid().
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'search_status') THEN
    CREATE TYPE search_status AS ENUM ('pending', 'running', 'done', 'failed');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'dedup_status') THEN
    CREATE TYPE dedup_status AS ENUM ('unique', 'duplicate_platform', 'duplicate_url', 'duplicate_email', 'weak_match');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaign_status') THEN
    CREATE TYPE campaign_status AS ENUM ('draft', 'sending', 'done', 'failed');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_status') THEN
    CREATE TYPE message_status AS ENUM ('pending', 'sent', 'failed');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'email_event_type') THEN
    CREATE TYPE email_event_type AS ENUM ('delivered', 'bounced', 'opened', 'replied', 'unsubscribed', 'unknown');
  END IF;
END
$$;

CREATE TABLE IF NOT EXISTS search_tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  query_raw text NOT NULL,
  query_parsed jsonb NOT NULL DEFAULT '{}'::jsonb,
  status search_status NOT NULL DEFAULT 'pending',
  result_count integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS search_results_raw (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id uuid NOT NULL REFERENCES search_tasks(id) ON DELETE CASCADE,
  platform text NOT NULL,
  platform_user_id text NOT NULL,
  display_name text NOT NULL,
  profile_url text NOT NULL,
  follower_count bigint,
  email text,
  extra jsonb NOT NULL DEFAULT '{}'::jsonb,
  fetched_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS influencers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  platform text NOT NULL,
  platform_user_id text NOT NULL,
  display_name text NOT NULL,
  profile_url text NOT NULL,
  follower_count bigint,
  email text,
  saved_by text NOT NULL,
  saved_at timestamptz NOT NULL DEFAULT now(),
  unsubscribed_at timestamptz,
  CONSTRAINT uq_influencers_platform_user UNIQUE (platform, platform_user_id)
);

CREATE TABLE IF NOT EXISTS search_results_deduped (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id uuid NOT NULL REFERENCES search_tasks(id) ON DELETE CASCADE,
  raw_result_id uuid NOT NULL REFERENCES search_results_raw(id) ON DELETE CASCADE,
  dedup_status dedup_status NOT NULL,
  matched_influencer_id uuid REFERENCES influencers(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_dedup_task_raw UNIQUE (task_id, raw_result_id)
);

CREATE TABLE IF NOT EXISTS email_drafts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  goal text NOT NULL,
  tone text NOT NULL,
  language text NOT NULL,
  subject text NOT NULL,
  body text NOT NULL,
  variables jsonb NOT NULL DEFAULT '{}'::jsonb,
  influencer_ids uuid[] NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS email_campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id uuid NOT NULL REFERENCES email_drafts(id) ON DELETE CASCADE,
  status campaign_status NOT NULL DEFAULT 'draft',
  send_rate_limit integer NOT NULL,
  accepted_count integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS email_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid NOT NULL REFERENCES email_campaigns(id) ON DELETE CASCADE,
  influencer_id uuid NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
  to_email text NOT NULL,
  subject text NOT NULL,
  body text NOT NULL,
  status message_status NOT NULL DEFAULT 'pending',
  provider_message_id text,
  sent_at timestamptz
);

CREATE TABLE IF NOT EXISTS email_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id uuid NOT NULL REFERENCES email_messages(id) ON DELETE CASCADE,
  provider_event_id text UNIQUE,
  event_type email_event_type NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  raw_payload jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id uuid NOT NULL,
  detail jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_search_results_raw_task_id ON search_results_raw(task_id);
CREATE INDEX IF NOT EXISTS ix_search_results_raw_email ON search_results_raw(email);

CREATE INDEX IF NOT EXISTS ix_search_results_deduped_task_id ON search_results_deduped(task_id);
CREATE INDEX IF NOT EXISTS ix_search_results_deduped_raw_result_id ON search_results_deduped(raw_result_id);
CREATE INDEX IF NOT EXISTS ix_search_results_deduped_matched_influencer_id ON search_results_deduped(matched_influencer_id);

CREATE INDEX IF NOT EXISTS ix_influencers_email ON influencers(email);

CREATE INDEX IF NOT EXISTS ix_email_campaigns_draft_id ON email_campaigns(draft_id);

CREATE INDEX IF NOT EXISTS ix_email_messages_campaign_id ON email_messages(campaign_id);
CREATE INDEX IF NOT EXISTS ix_email_messages_influencer_id ON email_messages(influencer_id);

CREATE INDEX IF NOT EXISTS ix_email_events_message_id ON email_events(message_id);
CREATE INDEX IF NOT EXISTS ix_email_events_occurred_at ON email_events(occurred_at);

CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_id ON audit_logs(entity_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at ON audit_logs(created_at);

CREATE OR REPLACE FUNCTION set_updated_at_timestamp()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_search_tasks_updated_at ON search_tasks;
CREATE TRIGGER trg_search_tasks_updated_at
BEFORE UPDATE ON search_tasks
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_timestamp();

COMMIT;
