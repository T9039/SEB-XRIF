import type { StorybookConfig } from "@storybook/react-vite";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  addons: ["@storybook/addon-docs", "@storybook/addon-a11y", "@storybook/addon-themes"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  core: {
    disableTelemetry: true,
  },
  viteFinal: async (viteConfig) => {
    const aliasModule = path.resolve(process.cwd(), "src");
    viteConfig.resolve ??= {};
    const existing = viteConfig.resolve.alias;
    viteConfig.resolve.alias = Array.isArray(existing)
      ? [...existing, { find: "@", replacement: aliasModule }]
      : Object.assign({}, existing, { "@": aliasModule });
    viteConfig.plugins = [...(viteConfig.plugins ?? []), tailwindcss()];
    return viteConfig;
  },
};

export default config;
