"use client";

import { useState } from "react";

import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function EmailEditor() {
  const [goal, setGoal] = useState("Invite influencer for product collaboration");
  const [tone, setTone] = useState("professional");
  const [language, setLanguage] = useState("en");
  const [influencerIdsRaw, setInfluencerIdsRaw] = useState("");

  const [draftId, setDraftId] = useState<string | null>(null);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [sendRateLimit, setSendRateLimit] = useState(60);
  const [campaignId, setCampaignId] = useState<string | null>(null);

  const influencerIds = influencerIdsRaw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const generateMutation = useMutation({
    mutationFn: () =>
      api.generateDraft({
        goal,
        tone,
        language,
        influencer_ids: influencerIds,
      }),
    onSuccess: (data) => {
      setDraftId(data.id);
      setSubject(data.subject);
      setBody(data.body);
    },
  });

  const sendMutation = useMutation({
    mutationFn: () =>
      api.sendCampaign({
        draft_id: draftId,
        influencer_ids: influencerIds,
        send_rate_limit: sendRateLimit,
      }),
    onSuccess: (data) => setCampaignId(data.campaign_id),
  });

  return (
    <div className="grid">
      <div className="card">
        <h3>Generate Draft</h3>
        <label>Goal</label>
        <input value={goal} onChange={(e) => setGoal(e.target.value)} style={{ width: "100%" }} />
        <label>Tone</label>
        <select value={tone} onChange={(e) => setTone(e.target.value)}>
          <option value="professional">professional</option>
          <option value="friendly">friendly</option>
          <option value="casual">casual</option>
        </select>
        <label>Language</label>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="zh">中文</option>
        </select>
        <label>Influencer IDs (comma separated UUIDs)</label>
        <textarea
          value={influencerIdsRaw}
          onChange={(e) => setInfluencerIdsRaw(e.target.value)}
          rows={4}
          style={{ width: "100%" }}
        />
        <button type="button" disabled={influencerIds.length === 0 || generateMutation.isPending} onClick={() => generateMutation.mutate()}>
          {generateMutation.isPending ? "Generating..." : "Generate Draft"}
        </button>
      </div>

      <div className="card">
        <h3>Draft Preview</h3>
        <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Subject" style={{ width: "100%" }} />
        <textarea value={body} onChange={(e) => setBody(e.target.value)} rows={10} placeholder="Body" style={{ width: "100%" }} />
        <label>Rate limit (emails/min)</label>
        <input
          type="number"
          value={sendRateLimit}
          min={1}
          onChange={(e) => setSendRateLimit(Number(e.target.value) || 1)}
        />
        <button type="button" disabled={!draftId || sendMutation.isPending} onClick={() => sendMutation.mutate()}>
          {sendMutation.isPending ? "Sending..." : "Send Campaign"}
        </button>
        {campaignId ? <p>Campaign created: {campaignId}</p> : null}
      </div>

      {generateMutation.isError ? <p>Failed to generate draft.</p> : null}
      {sendMutation.isError ? <p>Failed to send campaign.</p> : null}
    </div>
  );
}
