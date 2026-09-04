import { Success } from "./Success";

export default async function Page({ params }: { params: Promise<{ zoo: string }> }) {
  const { zoo } = await params;
  return <Success zoo={zoo} />;
}
