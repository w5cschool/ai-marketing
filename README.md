# AI Email Marketing (for LinkerTube)

Language: English | [简体中文](./README.zh-CN.md)

## Overview
AI-powered growth platform: analyze your site, run SEO & GEO audits, generate social and ad creative, discover influencers, plan and execute a data-driven growth strategy—with an AI assistant and content scheduling.

## Feature List

### ① Website Analysis
* Input website URL
* Auto site scan
* Brand analysis
* Market positioning identification
* Competitor identification

---

### ② SEO & GEO Analysis
* Deep SEO audit
* 60+ on-page metrics
* AI search visibility (ChatGPT / Perplexity citations, etc.)
* SEO issue identification and recommendations

---

### ③ Social Content Generation
* LinkedIn content generation
* X (Twitter) content generation
* Reddit content generation
* Brand voice matching
* Target audience matching

---

### ④ Ad Creative Generation
* Competitor ad analysis
* Ad creative generation
* Meta Ads content generation
* Google Ads content generation

---

### ⑤ Influencer Discovery
* Find influencers that fit your brand
* Audience analysis
* Engagement metrics

---

### ⑥ Growth Strategy
* 12-week growth plan (Growth Calendar)
* Priority strategy ranking
* Actionable growth tasks

---

### ⑦ AI Growth Assistant
* Chat with growth data
* Real-time growth suggestions
* Execute workflows via natural language

---

### ⑧ Content Execution & Optimization
* Content scheduling
* Performance tracking
* Auto iteration and optimization

---

### ⑨ Data Engine
* LinkedIn analytics
* X/Twitter algorithm data
* Reddit analytics
* AI text humanization detection
* Directory database

---

### ⑩ Product Features
* “Analyze my site” (URL entry)
* 60-second result generation
* Credits system
* Free / Pro / Enterprise tiers
* Community support
* Slack support (Pro)
* Advanced Analytics
* Multi-account (Enterprise)
* Custom integrations

## Current Status
- Backend initialization: completed (FastAPI + Supabase + core APIs)
- Frontend base pages: completed (ready for further UI/UX iteration)
- DB migration method: SQL script (`Alembic` removed)

## Responsibility Split
- You (project owner): project bootstrap + backend implementation/integration
- Your friend: frontend implementation, UX polish, integration UI

## Project Structure
```text
ai-email-marketing/
├── backend/                 # FastAPI backend
├── frontend/                # Next.js frontend
├── sql/
│   └── init_schema.sql      # Supabase schema init SQL
├── start-dev.sh             # one-command local startup
└── README.md
```

## Implemented Backend APIs (MVP)
Base: `/api/v1`

- `POST /search-tasks`
- `GET /search-tasks`
- `GET /search-tasks/{task_id}`
- `GET /search-tasks/{task_id}/results`
- `POST /influencers/save`
- `GET /influencers`
- `POST /email-drafts/generate`
- `POST /campaigns/send`
- `GET /campaigns/{campaign_id}/events`
- `POST /webhooks/resend`

## Database Initialization (Supabase)
Run this SQL in Supabase SQL Editor:
- `sql/init_schema.sql`

## Local Startup
```bash
./start-dev.sh
```
Default endpoints:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:3000`

## API Docs
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Environment Variables (`backend/.env`)
- `DATABASE_URL` (Supabase + asyncpg)
- `OPENAI_API_KEY`
- `YOUTUBE_API_KEY`
- `RESEND_API_KEY`
- `RESEND_WEBHOOK_SECRET`
