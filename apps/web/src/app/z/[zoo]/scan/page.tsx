import { Placeholder } from "@/components/Placeholder";

export default async function Page({ params }: { params: Promise<Record<string, string>> }) {
  const p = await params;
  return (
    <Placeholder eyebrow="Scanner" title="Scan the quest marker" milestone="M2">
      <pre className="rounded-card bg-canopy p-4 text-xs text-sand-dim">{JSON.stringify(p, null, 2)}</pre>
    </Placeholder>
  );
}
