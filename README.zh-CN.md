# AI Email Marketing（for LinkerTube）

语言: [English](./README.md) | 简体中文

## 项目简介
AI 驱动的增长平台：分析网站、做 SEO/GEO 审核、生成社媒与广告创意、发现达人、规划并执行数据驱动的增长策略，配合 AI 助手与内容排程。

## 功能点清单

### ① 网站分析（Website Analysis）
* 输入网站 URL
* 自动扫描网站
* 品牌分析
* 市场定位识别
* 竞品识别

---

### ② SEO & GEO 分析
* SEO 深度审核
* 60+ On-page 指标检测
* AI 搜索可见度检测（ChatGPT / Perplexity 等引用情况）
* SEO 问题识别与建议

---

### ③ 社交媒体内容生成
* LinkedIn 内容生成
* X（Twitter）内容生成
* Reddit 内容生成
* 品牌语气匹配
* 目标受众匹配

---

### ④ 广告创意生成
* 竞品广告分析
* 广告创意生成
* Meta Ads 内容生成
* Google Ads 内容生成

---

### ⑤ Influencer Discovery
* 找适合品牌的 Influencer
* 受众分析
* Engagement 数据分析

---

### ⑥ Growth Strategy
* 12 周增长计划（Growth Calendar）
* 优先级策略排序
* 可执行增长任务

---

### ⑦ AI Growth Assistant
* 与增长数据聊天
* 实时增长建议
* 自然语言执行 workflow

---

### ⑧ 内容执行与优化
* 内容排程（Schedule）
* 性能追踪（Performance Tracking）
* 自动迭代优化

---

### ⑨ 数据驱动系统（Data Engine）
* LinkedIn 数据分析
* X/Twitter 算法数据
* Reddit 数据分析
* AI 文本人类化检测
* Directory 数据库

---

### ⑩ 产品层功能
* Analyze my site（URL 输入入口）
* 60 秒生成结果
* Credits 系统
* 免费版 / Pro / Enterprise
* 社区支持
* Slack 支持（Pro）
* 高级分析（Advanced Analytics）
* 多账户（Enterprise）
* 自定义集成

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
