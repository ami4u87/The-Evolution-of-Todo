import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  // This creates a minimal production build that can run without node_modules
  output: "standalone",

  // Optimize images for production
  images: {
    unoptimized: process.env.NODE_ENV === "development",
  },
};

export default nextConfig;
