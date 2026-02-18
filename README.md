# AI Email Marketing — Influencer Discovery & Outreach

## English

### Overview

A platform for **finding and contacting influencers (KOLs)**. You describe what you need in natural language; AI finds matching creators across major social platforms, deduplicates against existing data, and helps you reach out at scale.

### What We Build

1. **Influencer discovery by instruction**  
   You give the AI a task (e.g. “find fitness YouTubers in the US with 50k–500k subs”). The system searches and returns creators from **YouTube, TikTok, Instagram, Facebook, Twitter/X**, etc., with:
   - Platform profiles and links  
   - Contact email (when available)  
   - Follower/subscriber counts  
   - Other relevant metadata  

2. **Deduplication**  
   For each run, results are checked against the database. Duplicates from earlier tasks or saves are filtered out so you only see new leads.

3. **Save or discard**  
   After reviewing the list, you choose whether to save the influencers to your database for future campaigns.

4. **AI-written outreach emails**  
   Based on your goal (e.g. collaboration, sponsorship), the AI drafts a personalized outreach email that you can edit before sending.

5. **Batch email sending**  
   Send the outreach email in bulk to the selected influencers to start partnerships or campaigns.

### Tech Stack

| Layer   | Technology        |
|--------|--------------------|
| Backend | **FastAPI**       |
| Database | **Supabase**     |
| Frontend | **Next.js** (latest) |
| AI / APIs | **OpenAI**      |

---

## 中文

### 项目概述

面向**寻找与联系达人（KOL）**的平台。用户用自然语言描述需求，由 AI 在各大社交平台上查找符合条件的创作者，与已有数据去重，并支持批量建联。

### 我们要做什么

1. **按指令发现达人**  
   用户给 AI 一条指令（例如：“找美国地区、5 万–50 万订阅的健身类 YouTube 博主”），系统在 **YouTube、TikTok、Instagram、Facebook、Twitter/X** 等平台搜索，并返回：
   - 平台主页与链接  
   - 联系邮箱（如有）  
   - 粉丝/订阅数  
   - 其他相关元数据  

2. **去重**  
   同一任务或历史任务的结果会与数据库比对，重复的达人会被过滤，只展示新增的候选人。

3. **是否保存**  
   用户查看结果后，可选择是否将这批达人保存到数据库中，供后续活动使用。

4. **AI 撰写建联邮件**  
   根据用户需求（如合作、赞助），由 AI 生成一封可编辑的建联邮件。

5. **批量发送邮件**  
   将建联邮件批量发送给选中的达人，完成初次联系与建联。

### 技术栈

| 层级   | 技术                |
|--------|---------------------|
| 后端   | **FastAPI**         |
| 数据库 | **Supabase**        |
| 前端   | **Next.js**（最新版） |
| AI/接口 | **OpenAI**         |
