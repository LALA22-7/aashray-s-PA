/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
      {
        source: "/api/webhooks/:path*",
        destination: "http://localhost:8000/webhooks/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
