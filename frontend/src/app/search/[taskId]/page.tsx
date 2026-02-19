"use client";

import { use } from "react";
import { useMemo, useState } from "react";

import { useMutation, useQuery } from "@tanstack/react-query";

import { InfluencerTable } from "@/components/InfluencerTable";
import { api } from "@/lib/api";

export default function SearchResultPage({ params }: { params: Promise<{ taskId: string }> }) {
  const { taskId } = use(params);
  const [selected, setSelected] = useState<string[]>([]);

  const resultsQuery = useQuery({
    queryKey: ["search-results-page", taskId],
    queryFn: () => api.getSearchResults(taskId),
  });

  const saveMutation = useMutation({
    mutationFn: () => api.saveInfluencers({ task_id: taskId, selected_result_ids: selected }),
  });

  const selectableIds = useMemo(
    () => (resultsQuery.data ?? []).filter((item) => item.dedup_status === "unique").map((item) => item.raw_result_id),
    [resultsQuery.data],
  );

  function toggleSelection(rawResultId: string, checked: boolean) {
    setSelected((prev) => {
      if (checked) return [...new Set([...prev, rawResultId])];
      return prev.filter((id) => id !== rawResultId);
    });
  }

  return (
    <main>
      <h1>Search Result: {taskId}</h1>
      {resultsQuery.data ? (
        <>
          <div className="card">
            <button type="button" disabled={selectableIds.length === 0} onClick={() => setSelected(selectableIds)}>
              Select All Unique ({selectableIds.length})
            </button>
            <button
              type="button"
              style={{ marginLeft: 8 }}
              disabled={selected.length === 0}
              onClick={() => setSelected([])}
            >
              Clear Selection
            </button>
            <button
              type="button"
              style={{ marginLeft: 8 }}
              disabled={selected.length === 0 || saveMutation.isPending}
              onClick={() => saveMutation.mutate()}
            >
              {saveMutation.isPending ? "Saving..." : `Save Selected (${selected.length})`}
            </button>
            {saveMutation.data ? (
              <p>
                Saved {saveMutation.data.saved_count}, skipped {saveMutation.data.skipped_count}
              </p>
            ) : null}
          </div>
          <InfluencerTable items={resultsQuery.data} selected={selected} onToggle={toggleSelection} />
        </>
      ) : (
        <p>Loading...</p>
      )}
    </main>
  );
}
