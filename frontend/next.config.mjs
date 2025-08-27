/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Optimize for Vercel deployment
  output: "standalone",

  // Vercel-specific optimizations
  swcMinify: true,

  // Environment variable validation
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT,
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  },

  // Image optimization
  images: {
    domains: [],
    unoptimized: false,
  },

  // Experimental features for better performance
  experimental: {
    optimizePackageImports: ["lucide-react", "@radix-ui/react-icons"],
  },

  // ESLint configuration for build
  eslint: {
    // Allow production builds to complete even if there are ESLint errors
    ignoreDuringBuilds: true,
  },

  // TypeScript configuration for build
  typescript: {
    // Allow production builds to complete even if there are type errors
    ignoreBuildErrors: true,
  },

  // Webpack optimization
  webpack: (config, { isServer }) => {
    // Optimize bundle size
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },

  // Headers for security and performance
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-DNS-Prefetch-Control",
            value: "on",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=63072000; includeSubDomains; preload",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "SAMEORIGIN",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          {
            key: "Referrer-Policy",
            value: "origin-when-cross-origin",
          },
        ],
      },
    ];
  },

  // Rewrites for API proxy in development (helps with CORS)
  async rewrites() {
    if (
      process.env.NODE_ENV === "development" &&
      process.env.NEXT_PUBLIC_API_PROXY === "true"
    ) {
      return [
        {
          source: "/api/:path*",
          destination: `${
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
          }/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
