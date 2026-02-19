import { CampaignDashboard } from "@/components/CampaignDashboard";

export default async function CampaignPage({ params }: { params: Promise<{ campaignId: string }> }) {
  const { campaignId } = await params;

  return (
    <main>
      <h1>Campaign</h1>
      <CampaignDashboard campaignId={campaignId} />
    </main>
  );
}
