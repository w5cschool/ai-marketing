# AI Email Marketing（for LinkerTube）

语言: [English](./README.md) | 简体中文

## 项目简介
`ai-email-marketing` 是服务于 LinkerTube 的子系统，目标是实现：
- 达人发现（YouTube 优先）
- 去重与保存
- AI 邮件草稿生成
- 批量发送与事件追踪

## 当前状态
- 后端初始化：已完成（FastAPI + Supabase + 主要 API）
- 前端基础页面：已完成（可继续优化 UI/交互）
- 数据库初始化方式：使用 SQL 脚本（不再使用 Alembic）

## 分工
- 你（项目 owner）：项目初始化 + 后端实现与联调
- 你朋友：前端页面开发、交互完善、联调展示

## 目录结构
```text
ai-email-marketing/
├── backend/                 # FastAPI 后端
├── frontend/                # Next.js 前端
├── sql/
│   └── init_schema.sql      # Supabase 初始化 SQL
├── start-dev.sh             # 前后端一键启动脚本
└── README.md
```

## 已实现后端 API（MVP）
Base: `/api/v1`

- `POST /search-tasks` 创建搜索任务
- `GET /search-tasks` 查询任务列表（含状态）
- `GET /search-tasks/{task_id}` 查询任务状态
- `GET /search-tasks/{task_id}/results` 查询去重结果
- `POST /influencers/save` 保存勾选达人
- `GET /influencers` 查询已保存达人
- `POST /email-drafts/generate` 生成邮件草稿
- `POST /campaigns/send` 发送 campaign
- `GET /campaigns/{campaign_id}/events` 查询事件
- `POST /webhooks/resend` 接收邮件回调

## 数据库初始化（Supabase）
在 Supabase SQL Editor 执行：
- `sql/init_schema.sql`

## 本地启动
```bash
./start-dev.sh
```
默认地址：
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:3000`

## API 文档
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## 环境变量（`backend/.env`）
- `DATABASE_URL`（Supabase, asyncpg）
- `OPENAI_API_KEY`
- `YOUTUBE_API_KEY`
- `RESEND_API_KEY`
- `RESEND_WEBHOOK_SECRET`
