export const brandTokens = {
  colors: {
    bg: {
      base: "hsl(222 28% 7%)",
      surface: "hsl(222 25% 10%)",
      elevated: "hsl(222 22% 13%)",
      hover: "hsl(222 22% 16%)",
      muted: "hsl(222 18% 20%)",
    },
    fg: {
      primary: "hsl(210 35% 96%)",
      secondary: "hsl(215 18% 72%)",
      tertiary: "hsl(215 14% 58%)",
      muted: "hsl(215 12% 44%)",
    },
    border: {
      base: "hsl(222 18% 18%)",
      strong: "hsl(222 16% 26%)",
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
  radii: {
    sm: "4px",
    md: "8px",
    lg: "12px",
    xl: "16px",
    pill: "9999px",
  },
  spacing: {
    xs: "4px",
    sm: "8px",
    md: "12px",
    lg: "16px",
    xl: "24px",
    "2xl": "32px",
  },
  fontFamily: {
    sans: `"Inter var", "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`,
    mono: `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace`,
  },
} as const;

export type BrandTokens = typeof brandTokens;
