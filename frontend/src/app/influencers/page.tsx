"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export default function InfluencersPage() {
  const query = useQuery({
    queryKey: ["influencers", 100, 0],
    queryFn: () => api.listInfluencers({ limit: 100, offset: 0 }),
  });

  return (
    <main>
      <h1>Saved Influencers</h1>
      <div className="card">
        {query.isLoading ? <p>Loading...</p> : null}
        {query.isError ? <p>Failed to load influencers.</p> : null}
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Platform</th>
              <th>Followers</th>
              <th>Email</th>
              <th>Profile</th>
            </tr>
          </thead>
          <tbody>
            {(query.data ?? []).map((item) => (
              <tr key={item.id}>
                <td>{item.display_name}</td>
                <td>{item.platform}</td>
                <td>{item.follower_count ?? "-"}</td>
                <td>{item.email ?? "-"}</td>
                <td>
                  <a href={item.profile_url} target="_blank" rel="noreferrer">
                    Open
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
