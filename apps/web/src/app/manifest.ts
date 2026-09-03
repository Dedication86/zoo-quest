import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Zoo Quest",
    short_name: "Zoo Quest",
    description: "Turn a day at the zoo into an adventure.",
    start_url: "/",
    display: "standalone",
    background_color: "#0b1a14",
    theme_color: "#0b1a14",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
  };
}
