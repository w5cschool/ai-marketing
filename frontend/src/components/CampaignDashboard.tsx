"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function CampaignDashboard({ campaignId }: { campaignId: string }) {
  const eventsQuery = useQuery({
    queryKey: ["campaign-events", campaignId],
    queryFn: () => api.getCampaignEvents(campaignId),
    refetchInterval: 4000,
  });

  return (
    <div className="card">
      <h3>Campaign {campaignId}</h3>
      {eventsQuery.isLoading ? <p>Loading events...</p> : null}
      {eventsQuery.isError ? <p>Failed to load events.</p> : null}
      <ul>
        {(eventsQuery.data ?? []).map((event, idx) => (
          <li key={`${event.event_id}-${idx}`}>
            {event.event_type} at {new Date(event.occurred_at).toLocaleString()}
          </li>
        ))}
      </ul>
    </div>
  );
}
