"use client";

import type { SearchResultItem } from "@/lib/api";

export function InfluencerTable({
  items,
  selected,
  onToggle,
}: {
  items: SearchResultItem[];
  selected: string[];
  onToggle: (rawResultId: string, checked: boolean) => void;
}) {
  return (
    <div className="card">
      <h3>Candidates</h3>
      <table>
        <thead>
          <tr>
            <th>Select</th>
            <th>Name</th>
            <th>Platform</th>
            <th>Followers</th>
            <th>Email</th>
            <th>Profile</th>
            <th>Dedup</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const checked = selected.includes(item.raw_result_id);
            return (
              <tr key={item.deduped_id}>
                <td>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => onToggle(item.raw_result_id, e.target.checked)}
                    disabled={item.dedup_status !== "unique"}
                  />
                </td>
                <td>{item.display_name}</td>
                <td>{item.platform}</td>
                <td>{item.follower_count ?? "-"}</td>
                <td>{item.email ?? "-"}</td>
                <td>
                  <a href={item.profile_url} target="_blank" rel="noreferrer">
                    Open
                  </a>
                </td>
                <td>{item.dedup_status}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
