import type { NextConfig } from "next";

const config: NextConfig = {
  async redirects() {
    return [
      { source: "/insights", destination: "/findings", permanent: false },
      { source: "/habitat", destination: "/atmosphere", permanent: false },
      { source: "/mission", destination: "/", permanent: false },
      { source: "/compare", destination: "/gaps", permanent: false },
    ];
  },
};

export default config;
