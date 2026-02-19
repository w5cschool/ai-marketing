# AI Email Marketing (for LinkerTube)

用于 `linkertube` 的独立子项目：做「达人发现 + 建联邮件 + 批量触达」能力，并可回流数据给主系统。

## 1) 项目定位

- 这是一个服务于 `linkertube` 的独立服务，不是完全独立业务线。
- 核心价值：给 linkertube 持续提供高质量达人线索，并提升商务建联效率。
- 拆分原因：前后端可并行开发、部署独立、方便后续作为内部增长工具复用。

## 2) MVP 范围（先做小，再做大）

### In Scope

1. 自然语言创建达人搜索任务（先支持 YouTube，可预留 TikTok）。
2. 返回候选达人列表（含主页链接、粉丝量、邮箱字段）。
3. 与历史数据去重（跨任务去重）。
4. 用户选择保存候选达人。
5. AI 生成可编辑建联邮件模板。
6. 批量发送邮件（带基础限速与失败重试）。

### Out of Scope（MVP 不做）

1. 全平台一次性打通（IG/Facebook/X 后续再加）。
2. 全自动无人审核发送（MVP 保留人工确认）。
3. 复杂 CRM 自动化流程（先不做多轮自动跟进）。

## 3) 与 LinkerTube 的关系

### 数据关系

- `ai-email-marketing` 维护自己的任务、候选人、发送日志。
- `linkertube` 可按需拉取已保存达人与触达状态（API 或共享 DB schema）。

### 边界建议

- `ai-email-marketing`: 发现、去重、邮件生成、发送编排。
- `linkertube`: 业务主流程、账号体系、内容/课程等核心业务。

## 4) 系统架构（MVP）

```text
[Next.js Frontend]
    |
    v
[FastAPI Backend]
    |-- OpenAI (query parse + email draft)
    |-- Platform Connectors (YouTube first)
    |-- Email Provider (Resend/SendGrid/Postmark)
    |
    v
[Supabase(Postgres + Storage)]
```

## 5) 核心流程

1. 用户输入查询条件（自然语言）。
2. 后端解析为结构化过滤条件，创建 `search_task`。
3. Connector 拉取候选达人，写入 `search_results_raw`。
4. 去重服务按规则过滤，产出 `search_results_deduped`。
5. 前端展示候选列表，用户勾选保存为 `influencers`。
6. 用户输入建联目标，AI 生成 `email_draft`。
7. 用户确认后批量发送，记录 `email_campaign` 与 `email_events`。

## 6) 去重规则（必须明确）

按优先级匹配：

1. 同平台 `platform_user_id` 完全一致。
2. 规范化后的 `profile_url` 一致（去 query、尾斜杠、utm）。
3. 有邮箱时按 `email` 一致。
4. 弱匹配：`display_name + platform + follower_bucket`（仅提示，不自动合并）。

## 7) API 草案（前后端契约）

Base: `/api/v1`

1. `POST /search-tasks`
   - 入参：`query`, `platforms`, `region`, `follower_min`, `follower_max`
   - 出参：`task_id`, `status`
2. `GET /search-tasks/{task_id}`
   - 出参：任务状态、进度、统计信息
3. `GET /search-tasks/{task_id}/results`
   - 出参：去重后候选列表
4. `POST /influencers/save`
   - 入参：`task_id`, `selected_result_ids[]`
   - 出参：`saved_count`, `skipped_count`
5. `POST /email-drafts/generate`
   - 入参：`goal`, `tone`, `language`, `influencer_ids[]`
   - 出参：`subject`, `body`, `variables`
6. `POST /campaigns/send`
   - 入参：`draft_id`, `influencer_ids[]`, `send_rate_limit`
   - 出参：`campaign_id`, `accepted_count`
7. `GET /campaigns/{campaign_id}/events`
   - 出参：发送、投递、退信、打开、回复事件

## 8) 建议数据表（最小集合）

1. `search_tasks`
2. `search_results_raw`
3. `search_results_deduped`
4. `influencers`
5. `email_drafts`
6. `email_campaigns`
7. `email_messages`
8. `email_events`
9. `audit_logs`

## 9) 前后端分工

### 后端（你）

1. 完成任务流转：创建任务 -> 抓取 -> 去重 -> 保存。
2. 设计并实现上述 API，产出 OpenAPI 文档。
3. 邮件发送队列、限速、重试与日志落库。
4. 合规能力：退订、黑名单、发送频率控制。

### 前端（你朋友）

1. 任务创建页：自然语言 + 高级筛选参数。
2. 结果页：列表、去重标记、勾选保存。
3. 邮件编辑页：AI 草稿 + 人工编辑 + 变量预览。
4. Campaign 面板：发送进度与事件状态展示。

## 10) 里程碑（2-3 周 MVP）

1. Week 1
   - 定稿 API 契约、建表、打通 YouTube connector、完成去重 v1
2. Week 2
   - 完成保存流程、邮件草稿生成、基础批量发送
3. Week 3
   - 完成发送事件回流、限速/重试、联调与灰度上线

## 11) 合规与可达率（上线前检查）

1. 域名与发信配置：SPF、DKIM、DMARC。
2. 必须支持退订与黑名单。
3. 每日发送上限、每分钟发送速率、失败重试上限。
4. 敏感操作保留审计日志。
5. 平台数据获取遵守对应 ToS 与 API 政策。

## 12) Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI |
| Database | Supabase (Postgres) |
| Frontend | Next.js |
| AI | OpenAI |
| Email | Resend / SendGrid / Postmark (choose one in MVP) |
