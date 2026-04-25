import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
    "../../packages/foundry-ui/src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter var",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
      },
      colors: {
        bg: {
          base: "hsl(222 28% 7%)",
          surface: "hsl(222 25% 10%)",
          elevated: "hsl(222 22% 13%)",
        },
        surface: {
          DEFAULT: "hsl(222 25% 10%)",
          hover: "hsl(222 22% 16%)",
        },
        fg: {
          primary: "hsl(210 35% 96%)",
          secondary: "hsl(215 18% 72%)",
          tertiary: "hsl(215 14% 58%)",
          muted: "hsl(215 12% 44%)",
        },
        accent: {
          blue: "hsl(210 95% 62%)",
          cyan: "hsl(192 82% 52%)",
          violet: "hsl(262 72% 66%)",
        },
        state: {
          success: "hsl(152 60% 48%)",
          warn: "hsl(40 92% 58%)",
          danger: "hsl(354 78% 60%)",
          info: "hsl(210 92% 62%)",
        },
      },
      borderRadius: {
        pill: "9999px",
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(ellipse at top, hsl(222 28% 12%) 0%, hsl(222 28% 7%) 60%)",
      },
    },
  },
  plugins: [],
};

export default config;
