import path from "node:path";

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Minimal self-contained server for the Cloud Run image (frontend/Dockerfile).
  output: "standalone",
  // This folder is the project root (there is a stray lockfile in a parent directory).
  turbopack: { root: path.join(__dirname) },
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
