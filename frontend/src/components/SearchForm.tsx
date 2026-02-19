"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

import { InfluencerTable } from "./InfluencerTable";

export function SearchForm() {
  const [query, setQuery] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [selectedResultIds, setSelectedResultIds] = useState<string[]>([]);

  const createTaskMutation = useMutation({
    mutationFn: (payload: { query: string }) =>
      api.createSearchTask({
        query: payload.query,
        platforms: ["youtube"],
      }),
    onSuccess: (data) => {
      setTaskId(data.task_id);
      setSelectedResultIds([]);
    },
  });

  const taskListQuery = useQuery({
    queryKey: ["search-task-list", 20, 0],
    queryFn: () => api.listSearchTasks({ limit: 20, offset: 0 }),
  });

  const taskQuery = useQuery({
    queryKey: ["search-task", taskId],
    queryFn: () => api.getSearchTask(taskId as string),
    enabled: Boolean(taskId),
    refetchInterval: (queryState) => {
      const status = queryState.state.data?.status;
      return status === "done" || status === "failed" ? false : 2000;
    },
  });

  const resultsQuery = useQuery({
    queryKey: ["search-results", taskId],
    queryFn: () => api.getSearchResults(taskId as string),
    enabled: Boolean(taskId) && taskQuery.data?.status === "done",
  });

  const saveMutation = useMutation({
    mutationFn: () => api.saveInfluencers({ task_id: taskId as string, selected_result_ids: selectedResultIds }),
  });

  const uniqueCount = useMemo(
    () => (resultsQuery.data ?? []).filter((item) => item.dedup_status === "unique").length,
    [resultsQuery.data],
  );
  const selectableIds = useMemo(
    () => (resultsQuery.data ?? []).filter((item) => item.dedup_status === "unique").map((item) => item.raw_result_id),
    [resultsQuery.data],
  );

  function toggleSelection(rawResultId: string, checked: boolean) {
    setSelectedResultIds((prev) => {
      if (checked) return [...new Set([...prev, rawResultId])];
      return prev.filter((id) => id !== rawResultId);
    });
  }

  return (
    <div className="grid">
      <div className="card">
        <h3>Create Search Task</h3>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. US tech youtubers 10k+"
          style={{ width: "100%", marginBottom: 8 }}
        />
        <button type="button" disabled={!query || createTaskMutation.isPending} onClick={() => createTaskMutation.mutate({ query })}>
          {createTaskMutation.isPending ? "Creating..." : "Run Search"}
        </button>
        {taskId ? (
          <p>
            Task ID: {taskId} | <Link href={`/search/${taskId}`}>Open result page</Link>
          </p>
        ) : null}
        {taskQuery.data ? (
          <p>
            Status: <strong>{taskQuery.data.status}</strong> | Results: {taskQuery.data.result_count}
          </p>
        ) : null}
      </div>

      <div className="card">
        <h3>Task History</h3>
        <div className="task-list">
          {(taskListQuery.data ?? []).map((task) => (
            <Link key={task.task_id} href={`/search/${task.task_id}`} className="task-row">
              <span className={`chip chip-${task.status}`}>{task.status}</span>
              <span>{task.query_raw.slice(0, 64)}</span>
              <span>{task.result_count} results</span>
            </Link>
          ))}
        </div>
      </div>

      {resultsQuery.data ? (
        <>
          <p>Unique candidates: {uniqueCount}</p>
          <div className="card">
            <button
              type="button"
              disabled={selectableIds.length === 0}
              onClick={() => setSelectedResultIds(selectableIds)}
            >
              Select All Unique ({selectableIds.length})
            </button>
            <button
              type="button"
              style={{ marginLeft: 8 }}
              disabled={selectedResultIds.length === 0}
              onClick={() => setSelectedResultIds([])}
            >
              Clear Selection
            </button>
          </div>
          <InfluencerTable items={resultsQuery.data} selected={selectedResultIds} onToggle={toggleSelection} />
          <div className="card">
            <button
              type="button"
              disabled={!taskId || selectedResultIds.length === 0 || saveMutation.isPending}
              onClick={() => saveMutation.mutate()}
            >
              {saveMutation.isPending ? "Saving..." : `Save Selected (${selectedResultIds.length})`}
            </button>
            {saveMutation.data ? (
              <p>
                Saved {saveMutation.data.saved_count}, skipped {saveMutation.data.skipped_count}
              </p>
            ) : null}
          </div>
        </>
      ) : null}

      {createTaskMutation.isError ? <p>Failed to create task.</p> : null}
      {taskQuery.isError ? <p>Failed to query task status.</p> : null}
      {taskListQuery.isError ? <p>Failed to load task list.</p> : null}
      {resultsQuery.isError ? <p>Failed to load results.</p> : null}
      {saveMutation.isError ? <p>Failed to save influencers.</p> : null}
    </div>
  );
}
