#!/usr/bin/env node

/**
 * Vercel Deployment Script
 *
 * This script helps validate and deploy the frontend to Vercel
 * with proper environment configuration.
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

// Colors for console output
const colors = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
};

function log(message, color = "reset") {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function validateEnvironment() {
  log("🔍 Validating environment configuration...", "blue");

  const requiredEnvVars = [
    "NEXT_PUBLIC_API_URL",
    "NEXT_PUBLIC_ENVIRONMENT",
    "NEXT_PUBLIC_APP_NAME",
  ];

  const missing = [];

  requiredEnvVars.forEach((envVar) => {
    if (!process.env[envVar]) {
      missing.push(envVar);
    }
  });

  if (missing.length > 0) {
    log("❌ Missing required environment variables:", "red");
    missing.forEach((envVar) => {
      log(`   - ${envVar}`, "red");
    });
    log(
      "\nPlease set these variables in your Vercel dashboard or .env.local file.",
      "yellow"
    );
    return false;
  }

  // Validate API URL format
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl.startsWith("http://") && !apiUrl.startsWith("https://")) {
    log("❌ NEXT_PUBLIC_API_URL must start with http:// or https://", "red");
    return false;
  }

  if (
    process.env.NEXT_PUBLIC_ENVIRONMENT === "production" &&
    apiUrl.startsWith("http://")
  ) {
    log("⚠️  Warning: Using HTTP in production environment", "yellow");
  }

  log("✅ Environment validation passed", "green");
  return true;
}

function validateBuildConfiguration() {
  log("🔍 Validating build configuration...", "blue");

  // Check if required files exist
  const requiredFiles = [
    "package.json",
    "next.config.mjs",
    "vercel.json",
    "tsconfig.json",
  ];

  const missing = [];

  requiredFiles.forEach((file) => {
    if (!fs.existsSync(path.join(__dirname, "..", file))) {
      missing.push(file);
    }
  });

  if (missing.length > 0) {
    log("❌ Missing required configuration files:", "red");
    missing.forEach((file) => {
      log(`   - ${file}`, "red");
    });
    return false;
  }

  log("✅ Build configuration validation passed", "green");
  return true;
}

function testBuild() {
  log("🏗️  Testing local build...", "blue");

  try {
    execSync("npm run build", {
      stdio: "inherit",
      cwd: path.join(__dirname, ".."),
    });
    log("✅ Local build successful", "green");
    return true;
  } catch (error) {
    log("❌ Local build failed", "red");
    log("Please fix build errors before deploying to Vercel.", "yellow");
    return false;
  }
}

function testApiConnectivity() {
  log("🌐 Testing API connectivity...", "blue");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  return new Promise((resolve) => {
    const https = require(apiUrl.startsWith("https://") ? "https" : "http");

    const req = https.get(`${apiUrl}/healthz`, { timeout: 10000 }, (res) => {
      if (res.statusCode === 200) {
        log("✅ API connectivity test passed", "green");
        resolve(true);
      } else {
        log(`⚠️  API returned status ${res.statusCode}`, "yellow");
        resolve(true); // Continue deployment even if health check fails
      }
    });

    req.on("error", (error) => {
      log(`⚠️  API connectivity test failed: ${error.message}`, "yellow");
      log("Continuing with deployment - API might not be ready yet.", "yellow");
      resolve(true); // Continue deployment
    });

    req.on("timeout", () => {
      log("⚠️  API connectivity test timed out", "yellow");
      log("Continuing with deployment - API might not be ready yet.", "yellow");
      resolve(true); // Continue deployment
    });
  });
}

function deployToVercel() {
  log("🚀 Deploying to Vercel...", "blue");

  try {
    // Check if Vercel CLI is installed
    execSync("vercel --version", { stdio: "pipe" });
  } catch (error) {
    log("❌ Vercel CLI not found. Please install it:", "red");
    log("   npm install -g vercel", "cyan");
    log("   Or use the Vercel dashboard for deployment", "cyan");
    return false;
  }

  try {
    // Login check
    try {
      execSync("vercel whoami", { stdio: "pipe" });
    } catch (loginError) {
      log("⚠️  Not logged in to Vercel. Please run: vercel login", "yellow");
      return false;
    }

    // Deploy to Vercel
    log("   Deploying to production...", "cyan");
    execSync("vercel --prod --yes", {
      stdio: "inherit",
      cwd: path.join(__dirname, ".."),
    });
    log("✅ Deployment to Vercel successful!", "green");
    return true;
  } catch (error) {
    log("❌ Deployment to Vercel failed", "red");
    log(
      "   You can also deploy via Vercel dashboard or GitHub integration",
      "yellow"
    );
    return false;
  }
}

function setupVercelProject() {
  log("⚙️  Setting up Vercel project configuration...", "blue");

  try {
    // Check if project is already linked
    const vercelConfigPath = path.join(__dirname, "..", ".vercel");
    if (fs.existsSync(vercelConfigPath)) {
      log("✅ Vercel project already configured", "green");
      return true;
    }

    // Link project
    log("   Linking Vercel project...", "cyan");
    execSync("vercel link", {
      stdio: "inherit",
      cwd: path.join(__dirname, ".."),
    });

    log("✅ Vercel project setup complete", "green");
    return true;
  } catch (error) {
    log("⚠️  Could not setup Vercel project automatically", "yellow");
    log(
      '   Please run "vercel link" manually or use Vercel dashboard',
      "yellow"
    );
    return true; // Don't fail deployment for this
  }
}

async function main() {
  log("🎯 Healthcare Study Companion - Vercel Deployment", "magenta");
  log("================================================", "magenta");

  // Validation steps
  if (!validateEnvironment()) {
    process.exit(1);
  }

  if (!validateBuildConfiguration()) {
    process.exit(1);
  }

  if (!testBuild()) {
    process.exit(1);
  }

  await testApiConnectivity();

  // Setup and deploy
  setupVercelProject();
  const deploySuccess = deployToVercel();

  if (deploySuccess) {
    log("\n🎉 Deployment completed successfully!", "green");
    log("\nNext steps:", "blue");
    log("1. Verify the deployment at your Vercel URL", "cyan");
    log("2. Test frontend-backend connectivity", "cyan");
    log("3. Configure custom domain if needed", "cyan");
    log("4. Set up monitoring and analytics", "cyan");
  } else {
    log("\n❌ Deployment failed. Please check the errors above.", "red");
    process.exit(1);
  }
}

// Run the deployment script
if (require.main === module) {
  main().catch((error) => {
    log(`❌ Deployment script failed: ${error.message}`, "red");
    process.exit(1);
  });
}

module.exports = {
  validateEnvironment,
  validateBuildConfiguration,
  testBuild,
  testApiConnectivity,
  deployToVercel,
  setupVercelProject,
};
