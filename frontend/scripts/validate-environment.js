#!/usr/bin/env node

/**
 * Environment Validation Script for Frontend
 * 
 * Validates that all required environment variables are set
 * and have valid values for the target environment.
 */

const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Environment variable definitions
const envVarDefinitions = {
  required: {
    'NEXT_PUBLIC_API_URL': {
      description: 'Backend API base URL',
      validation: (value) => {
        if (!value.startsWith('http://') && !value.startsWith('https://')) {
          return 'Must start with http:// or https://';
        }
        try {
          new URL(value);
          return null;
        } catch {
          return 'Must be a valid URL';
        }
      },
      examples: [
        'http://localhost:8000 (development)',
        'https://your-backend.railway.app (production)'
      ]
    },
    'NEXT_PUBLIC_ENVIRONMENT': {
      description: 'Application environment',
      validation: (value) => {
        const validEnvs = ['development', 'staging', 'production'];
        if (!validEnvs.includes(value)) {
          return `Must be one of: ${validEnvs.join(', ')}`;
        }
        return null;
      },
      examples: ['development', 'staging', 'production']
    },
    'NEXT_PUBLIC_APP_NAME': {
      description: 'Application display name',
      validation: (value) => {
        if (value.length < 1) {
          return 'Cannot be empty';
        }
        return null;
      },
      examples: ['Healthcare Study Companion']
    }
  },
  optional: {
    'NEXT_PUBLIC_ENABLE_DEBUG_MODE': {
      description: 'Enable debug mode (true/false)',
      validation: (value) => {
        if (value && !['true', 'false'].includes(value.toLowerCase())) {
          return 'Must be "true" or "false"';
        }
        return null;
      },
      examples: ['true', 'false']
    },
    'NEXT_PUBLIC_ENABLE_ANALYTICS': {
      description: 'Enable analytics (true/false)',
      validation: (value) => {
        if (value && !['true', 'false'].includes(value.toLowerCase())) {
          return 'Must be "true" or "false"';
        }
        return null;
      },
      examples: ['true', 'false']
    },
    'NEXT_PUBLIC_VERCEL_ANALYTICS_ID': {
      description: 'Vercel Analytics ID',
      validation: null,
      examples: ['your-vercel-analytics-id']
    },
    'NEXT_PUBLIC_SENTRY_DSN': {
      description: 'Sentry DSN for error tracking',
      validation: (value) => {
        if (value && !value.startsWith('https://')) {
          return 'Must start with https://';
        }
        return null;
      },
      examples: ['https://xxx@sentry.io/xxx']
    }
  }
};

function loadEnvironmentFile(envFile) {
  if (!fs.existsSync(envFile)) {
    return {};
  }
  
  const content = fs.readFileSync(envFile, 'utf8');
  const env = {};
  
  content.split('\n').forEach(line => {
    line = line.trim();
    if (line && !line.startsWith('#')) {
      const [key, ...valueParts] = line.split('=');
      if (key && valueParts.length > 0) {
        env[key.trim()] = valueParts.join('=').trim();
      }
    }
  });
  
  return env;
}

function validateEnvironment(environment = 'development', strict = false) {
  log(`🔍 Validating ${environment} environment configuration...`, 'blue');
  
  // Load environment variables from various sources
  const envSources = [
    { name: 'Process Environment', env: process.env },
    { name: '.env.local', env: loadEnvironmentFile('.env.local') },
    { name: `.env.${environment}`, env: loadEnvironmentFile(`.env.${environment}`) },
    { name: '.env', env: loadEnvironmentFile('.env') }
  ];
  
  // Merge environment variables (process.env takes precedence)
  const mergedEnv = {};
  envSources.reverse().forEach(source => {
    Object.assign(mergedEnv, source.env);
  });
  
  let hasErrors = false;
  let hasWarnings = false;
  
  // Validate required variables
  log('\n📋 Required Environment Variables:', 'cyan');
  Object.entries(envVarDefinitions.required).forEach(([key, config]) => {
    const value = mergedEnv[key];
    
    if (!value) {
      log(`❌ ${key}: MISSING`, 'red');
      log(`   Description: ${config.description}`, 'red');
      log(`   Examples: ${config.examples.join(', ')}`, 'red');
      hasErrors = true;
    } else {
      const validationError = config.validation ? config.validation(value) : null;
      if (validationError) {
        log(`❌ ${key}: ${validationError}`, 'red');
        log(`   Current value: ${value}`, 'red');
        log(`   Examples: ${config.examples.join(', ')}`, 'red');
        hasErrors = true;
      } else {
        log(`✅ ${key}: ${value}`, 'green');
      }
    }
  });
  
  // Validate optional variables
  log('\n📋 Optional Environment Variables:', 'cyan');
  Object.entries(envVarDefinitions.optional).forEach(([key, config]) => {
    const value = mergedEnv[key];
    
    if (!value) {
      if (strict) {
        log(`⚠️  ${key}: NOT SET`, 'yellow');
        log(`   Description: ${config.description}`, 'yellow');
        hasWarnings = true;
      } else {
        log(`➖ ${key}: Not set (optional)`, 'reset');
      }
    } else {
      const validationError = config.validation ? config.validation(value) : null;
      if (validationError) {
        log(`❌ ${key}: ${validationError}`, 'red');
        log(`   Current value: ${value}`, 'red');
        hasErrors = true;
      } else {
        log(`✅ ${key}: ${value}`, 'green');
      }
    }
  });
  
  // Environment-specific validations
  if (environment === 'production') {
    log('\n🔒 Production Environment Checks:', 'magenta');
    
    // Check for HTTPS in production
    const apiUrl = mergedEnv['NEXT_PUBLIC_API_URL'];
    if (apiUrl && !apiUrl.startsWith('https://')) {
      log('⚠️  API URL should use HTTPS in production', 'yellow');
      hasWarnings = true;
    }
    
    // Check debug mode is disabled
    const debugMode = mergedEnv['NEXT_PUBLIC_ENABLE_DEBUG_MODE'];
    if (debugMode && debugMode.toLowerCase() === 'true') {
      log('⚠️  Debug mode should be disabled in production', 'yellow');
      hasWarnings = true;
    }
    
    // Check analytics is enabled
    const analytics = mergedEnv['NEXT_PUBLIC_ENABLE_ANALYTICS'];
    if (!analytics || analytics.toLowerCase() !== 'true') {
      log('⚠️  Consider enabling analytics in production', 'yellow');
      hasWarnings = true;
    }
  }
  
  // Summary
  log('\n📊 Validation Summary:', 'blue');
  if (hasErrors) {
    log('❌ Validation failed - please fix the errors above', 'red');
    return false;
  } else if (hasWarnings && strict) {
    log('⚠️  Validation passed with warnings', 'yellow');
    return true;
  } else {
    log('✅ All validations passed', 'green');
    return true;
  }
}

function generateEnvTemplate(environment = 'development') {
  log(`📝 Generating .env.${environment} template...`, 'blue');
  
  const template = [
    `# Healthcare Study Companion Frontend - ${environment.toUpperCase()} Environment`,
    '# Copy this file to .env.local and fill in your actual values',
    '',
    '# =============================================================================',
    '# REQUIRED VARIABLES',
    '# =============================================================================',
    ''
  ];
  
  Object.entries(envVarDefinitions.required).forEach(([key, config]) => {
    template.push(`# ${config.description}`);
    template.push(`# Examples: ${config.examples.join(', ')}`);
    template.push(`${key}=`);
    template.push('');
  });
  
  template.push('# =============================================================================');
  template.push('# OPTIONAL VARIABLES');
  template.push('# =============================================================================');
  template.push('');
  
  Object.entries(envVarDefinitions.optional).forEach(([key, config]) => {
    template.push(`# ${config.description}`);
    if (config.examples) {
      template.push(`# Examples: ${config.examples.join(', ')}`);
    }
    template.push(`# ${key}=`);
    template.push('');
  });
  
  const templatePath = `.env.${environment}.template`;
  fs.writeFileSync(templatePath, template.join('\n'));
  log(`✅ Template saved to ${templatePath}`, 'green');
}

// CLI interface
function main() {
  const args = process.argv.slice(2);
  const environment = args.find(arg => ['development', 'staging', 'production'].includes(arg)) || 'development';
  const strict = args.includes('--strict');
  const generateTemplate = args.includes('--generate-template');
  
  if (generateTemplate) {
    generateEnvTemplate(environment);
    return;
  }
  
  log('🎯 Healthcare Study Companion - Frontend Environment Validation', 'magenta');
  log('=============================================================', 'magenta');
  
  const isValid = validateEnvironment(environment, strict);
  
  if (!isValid) {
    log('\n💡 Tips:', 'blue');
    log('1. Copy .env.example to .env.local and fill in the values', 'cyan');
    log('2. Set environment variables in your deployment platform', 'cyan');
    log('3. Use --generate-template to create a template file', 'cyan');
    process.exit(1);
  }
  
  log('\n🎉 Environment validation completed successfully!', 'green');
}

// Export functions for use in other scripts
module.exports = {
  validateEnvironment,
  generateEnvTemplate,
  envVarDefinitions
};

// Run if called directly
if (require.main === module) {
  main();
}