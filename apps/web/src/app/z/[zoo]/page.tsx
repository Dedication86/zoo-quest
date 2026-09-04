import { Welcome } from "./Welcome";

export default async function Page({ params }: { params: Promise<{ zoo: string }> }) {
  const { zoo } = await params;
  return <Welcome zoo={zoo} />;
}
