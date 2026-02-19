# AI Email Marketing (for LinkerTube)

Language: English | [简体中文](./README.zh-CN.md)

## Overview
`ai-email-marketing` is a LinkerTube sub-project focused on:
- creator discovery (YouTube first)
- dedup + save workflow
- AI email draft generation
- batch sending + delivery event tracking

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
