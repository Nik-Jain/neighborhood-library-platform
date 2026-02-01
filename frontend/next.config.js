/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone', // Enable standalone output for Docker
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Optimize for production
  compress: true,
  poweredByHeader: false,
}

module.exports = nextConfig
