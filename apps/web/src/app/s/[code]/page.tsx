import { MarkerLanding } from "./MarkerLanding";

/** The QR entry point. Everything interesting happens client-side once storage is readable. */
export default async function Page({ params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;
  return <MarkerLanding code={code.toUpperCase()} />;
}
