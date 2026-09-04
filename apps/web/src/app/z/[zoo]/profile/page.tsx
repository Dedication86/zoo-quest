import { Profile } from "./Profile";

export default async function Page({ params }: { params: Promise<{ zoo: string }> }) {
  const { zoo } = await params;
  return <Profile zoo={zoo} />;
}
