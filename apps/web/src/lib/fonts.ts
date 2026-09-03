/**
 * Self-hosted fonts (no request to Google at build or run time).
 * Files come from the @fontsource packages; copy new weights from
 * node_modules/@fontsource/<family>/files/ into src/fonts/ as needed.
 */
import localFont from "next/font/local";

export const barlow = localFont({
  variable: "--font-barlow",
  display: "swap",
  src: [
    { path: "../fonts/barlow-condensed-latin-500-normal.woff2", weight: "500" },
    { path: "../fonts/barlow-condensed-latin-600-normal.woff2", weight: "600" },
    { path: "../fonts/barlow-condensed-latin-700-normal.woff2", weight: "700" },
  ],
});

export const source = localFont({
  variable: "--font-source",
  display: "swap",
  src: [
    { path: "../fonts/source-sans-3-latin-400-normal.woff2", weight: "400" },
    { path: "../fonts/source-sans-3-latin-600-normal.woff2", weight: "600" },
  ],
});
