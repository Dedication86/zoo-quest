import { ZooFrame } from "./ZooFrame";

/** Every /z/[zoo]/* screen except Welcome and Success sits inside the app shell. */
export default async function Layout({
  params,
  children,
}: {
  params: Promise<{ zoo: string }>;
  children: React.ReactNode;
}) {
  const { zoo } = await params;
  return <ZooFrame zoo={zoo}>{children}</ZooFrame>;
}
