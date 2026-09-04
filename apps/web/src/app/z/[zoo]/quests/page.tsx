import { Quests } from "./Quests";

export default async function Page({ params }: { params: Promise<{ zoo: string }> }) {
  const { zoo } = await params;
  return <Quests zoo={zoo} />;
}
