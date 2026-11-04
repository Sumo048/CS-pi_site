import { defineConfig, fontProviders } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import icon from "astro-icon";
import mdx from "@astrojs/mdx";

import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeCitation from "rehype-citation";

import react from "@astrojs/react";

import astroExpressiveCode from "astro-expressive-code";

// https://astro.build/config
export default defineConfig({
  // GitHub Pages project site. The deploy workflow passes the same values via
  // --site/--base; these make a local `npm run build` match production.
  site: "https://sumo048.github.io",
  base: "/CS-pi_site",
  vite: {
    plugins: [tailwindcss()],
  },
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [
      rehypeKatex,
      [
        rehypeCitation,
        {
          bibliography: "bibliography.bib",
          linkCitations: true,
        },
      ],
    ],
  },
  integrations: [
    icon(),
    astroExpressiveCode({
      styleOverrides: {
        borderRadius: "4px",
        borderWidth: "1px",
        borderColor: "var(--rule)",
        codeBackground: "var(--code-bg)",
        codeFontFamily: "var(--font-plex-mono), ui-monospace, monospace",
        uiFontFamily: "var(--font-plex-sans), system-ui, sans-serif",
        frames: {
          shadowColor: "transparent",
        },
      },
      themeCssSelector: (theme) =>
        theme.type === "dark" ? `[data-theme="dark"]` : `[data-theme="light"]`,
    }),
    mdx(),
    react(),
  ],
  fonts: [
    {
      provider: fontProviders.google(),
      name: "Source Serif 4",
      cssVariable: "--font-source-serif",
      weights: ["400 700"],
      styles: ["normal", "italic"],
    },
    {
      provider: fontProviders.google(),
      name: "IBM Plex Sans",
      cssVariable: "--font-plex-sans",
      weights: [400, 500, 600],
      styles: ["normal"],
    },
    {
      provider: fontProviders.google(),
      name: "IBM Plex Mono",
      cssVariable: "--font-plex-mono",
      weights: [400, 500],
      styles: ["normal"],
    },
  ],
  image: {
    responsiveStyles: true,
  },
});
