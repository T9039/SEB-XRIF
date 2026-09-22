import { defineConfig } from "vite-plus";
import path from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  pack: {
    dts: {
      tsgo: true,
    },
    exports: {
      customExports: {
        "./index.css": "./src/index.css",
      },
    },
  },
  lint: {
    options: {
      typeAware: true,
      typeCheck: true,
    },
  },
  fmt: {},
});
