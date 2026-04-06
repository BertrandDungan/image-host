import { defineConfig } from "vitest/config";
import react, { reactCompilerPreset } from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import babel from "@rolldown/plugin-babel";
import path from "path";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    babel({ presets: [reactCompilerPreset()] }),
  ],
  base: "/dist/",
  build: {
    outDir: path.resolve(__dirname, "./dist"),
    emptyOutDir: false,
    manifest: "manifest.json",
    rolldownOptions: {
      input: {
        index: path.resolve(__dirname, "./frontend/index.tsx"),
        style: path.resolve(__dirname, "./frontend/style.css"),
      },
      output: {
        entryFileNames: `js/[name]-bundle.js`,
        assetFileNames: `css/[name].css`,
      },
    },
  },
  test: {
    environment: "happy-dom",
    globals: true,
    setupFiles: ["./frontend/tests/setup.ts"],
    include: ["frontend/tests/**/*.test.tsx"],
    clearMocks: true,
  },
});
