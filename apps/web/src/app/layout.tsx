import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";
import { barlow, source } from "@/lib/fonts";

export const metadata: Metadata = {
  title: "Zoo Quest",
  description: "Turn a day at the zoo into an adventure.",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, title: "Zoo Quest", statusBarStyle: "black-translucent" },
};

export const viewport: Viewport = {
  themeColor: "#0b1a14",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1, // no pinch-zoom surprises while walking; text stays large by design
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${barlow.variable} ${source.variable}`}>
      <body className="antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
