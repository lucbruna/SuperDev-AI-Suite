/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["localhost", "avatars.githubusercontent.com"],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
  experimental: {
    scrollRestoration: true,
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
};

export default nextConfig;
