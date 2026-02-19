import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <h1>AI Email Marketing Dashboard</h1>
      <div className="grid grid-2">
        <div className="card">
          <h2>Search Tasks</h2>
          <p>Create natural-language influencer search tasks.</p>
          <Link href="/search">Open Search</Link>
        </div>
        <div className="card">
          <h2>Saved Influencers</h2>
          <p>Review saved YouTubers and open their profile links.</p>
          <Link href="/influencers">Open Influencers</Link>
        </div>
        <div className="card">
          <h2>Email Drafts</h2>
          <p>Generate outreach drafts and tune variables.</p>
          <Link href="/drafts">Open Drafts</Link>
        </div>
      </div>
    </main>
  );
}
