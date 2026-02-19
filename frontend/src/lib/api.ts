export type SearchTaskStatus = {
  task_id: string;
  status: "pending" | "running" | "done" | "failed";
  result_count: number;
  created_at: string;
  updated_at: string;
};

export type SearchTaskListItem = {
  task_id: string;
  query_raw: string;
  status: "pending" | "running" | "done" | "failed";
  result_count: number;
  created_at: string;
  updated_at: string;
};

export type SearchResultItem = {
  deduped_id: string;
  raw_result_id: string;
  dedup_status: string;
  matched_influencer_id: string | null;
  platform: string;
  platform_user_id: string;
  display_name: string;
  profile_url: string;
  follower_count: number | null;
  email: string | null;
};

export type CampaignEvent = {
  event_id: string;
  message_id: string;
  event_type: string;
  occurred_at: string;
  raw_payload: Record<string, unknown>;
};

export type InfluencerListItem = {
  id: string;
  platform: string;
  platform_user_id: string;
  display_name: string;
  profile_url: string;
  follower_count: number | null;
  email: string | null;
  saved_by: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {};
  if (init?.body) {
    headers["Content-Type"] = "application/json";
  }

  const resp = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...headers, ...(init?.headers || {}) },
    cache: "no-store",
  });

  if (!resp.ok) {
    throw new Error(await resp.text());
  }
  return resp.json() as Promise<T>;
}

export const api = {
  createSearchTask: (body: Record<string, unknown>) =>
    request<{ task_id: string; status: string }>("/search-tasks", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listSearchTasks: (params?: { limit?: number; offset?: number }) => {
    const limit = params?.limit ?? 20;
    const offset = params?.offset ?? 0;
    return request<SearchTaskListItem[]>(`/search-tasks?limit=${limit}&offset=${offset}`);
  },
  getSearchTask: (taskId: string) => request<SearchTaskStatus>(`/search-tasks/${taskId}`),
  getSearchResults: (taskId: string) => request<SearchResultItem[]>(`/search-tasks/${taskId}/results`),
  listInfluencers: (params?: { limit?: number; offset?: number }) => {
    const limit = params?.limit ?? 100;
    const offset = params?.offset ?? 0;
    return request<InfluencerListItem[]>(`/influencers?limit=${limit}&offset=${offset}`);
  },
  saveInfluencers: (body: { task_id: string; selected_result_ids: string[] }) =>
    request<{ saved_count: number; skipped_count: number }>("/influencers/save", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  generateDraft: (body: Record<string, unknown>) =>
    request<{ id: string; subject: string; body: string; variables: Record<string, string>; created_at: string }>(
      "/email-drafts/generate",
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),
  sendCampaign: (body: Record<string, unknown>) =>
    request<{ campaign_id: string; accepted_count: number }>("/campaigns/send", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getCampaignEvents: (campaignId: string) => request<CampaignEvent[]>(`/campaigns/${campaignId}/events`),
};
