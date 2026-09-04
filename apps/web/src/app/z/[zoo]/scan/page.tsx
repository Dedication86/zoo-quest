import { Scanner } from "./Scanner";

export default async function Page({ params }: { params: Promise<{ zoo: string }> }) {
  const { zoo } = await params;
  return <Scanner zoo={zoo} />;
}
