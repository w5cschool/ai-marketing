"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function TopNav() {
  const router = useRouter();
  const [taskIdInput, setTaskIdInput] = useState("");
  const [campaignIdInput, setCampaignIdInput] = useState("");

  const tasksQuery = useQuery({
    queryKey: ["search-task-list", 20, 0],
    queryFn: () => api.listSearchTasks({ limit: 20, offset: 0 }),
  });

  return (
    <header className="top-nav-wrap">
      <div className="top-nav">
        <nav className="top-nav-links">
          <Link href="/">Dashboard</Link>
          <Link href="/search">Search</Link>
          <Link href="/influencers">Influencers</Link>
          <Link href="/drafts">Drafts</Link>
        </nav>

        <div className="top-nav-actions">
          <div className="inline-form">
            <input
              value={taskIdInput}
              onChange={(e) => setTaskIdInput(e.target.value)}
              placeholder="Task ID"
              aria-label="Task ID"
            />
            <button type="button" onClick={() => taskIdInput && router.push(`/search/${taskIdInput}`)}>
              Open Task
            </button>
          </div>

          <div className="inline-form">
            <input
              value={campaignIdInput}
              onChange={(e) => setCampaignIdInput(e.target.value)}
              placeholder="Campaign ID"
              aria-label="Campaign ID"
            />
            <button type="button" onClick={() => campaignIdInput && router.push(`/campaigns/${campaignIdInput}`)}>
              Open Campaign
            </button>
          </div>
        </div>
      </div>

      <div className="top-nav-sub">
        <strong>Recent Tasks:</strong>
        {tasksQuery.isLoading ? <span> loading...</span> : null}
        {(tasksQuery.data ?? []).slice(0, 10).map((task) => (
          <Link key={task.task_id} href={`/search/${task.task_id}`} className={`chip chip-${task.status}`}>
            {task.status} | {task.query_raw.slice(0, 40)}
          </Link>
        ))}
      </div>
    </header>
  );
}
