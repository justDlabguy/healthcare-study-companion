# Comprehensive Environment Validation Script (PowerShell)
# This script validates environment configuration for both backend and frontend
# across all environments (development, staging, production)

param(
    [string[]]$Environment = @("development", "staging", "production"),
    [switch]$Strict,
    [switch]$Verbose,
    [switch]$Json,
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Write-Host "Environment Validation Script" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Usage: .\scripts\validate-all-environments.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Environment ENV[]     Validate specific environment(s) only"
    Write-Host "  -Strict               Fail on warnings (useful for CI/CD)"
    Write-Host "  -Verbose              Show detailed output"
    Write-Host "  -Json                 Output results in JSON format"
    Write-Host "  -Help                 Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\scripts\validate-all-environments.ps1"
    Write-Host "  .\scripts\validate-all-environments.ps1 -Environment production -Strict"
    Write-Host "  .\scripts\validate-all-environments.ps1 -Verbose"
    exit 0
}

# Global variables
$ExitCode = 0
$TotalValidations = 0
$PassedValidations = 0
$FailedValidations = 0

# Function to print colored output
function Write-Status {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    if (-not $Json) {
        Write-Host $Message -ForegroundColor $Color
    }
}

# Function to validate backend environment
function Test-BackendEnvironment {
    param([string]$Env)
    
    $args = @("--environment", $Env)
    
    if ($Strict) { $args += "--strict" }
    if ($Verbose) { $args += "--verbose" }
    if ($Json) { $args += "--json" }
    
    Write-Status "🔍 Validating backend environment: $Env" "Blue"
    
    Push-Location backend
    try {
        $result = & python scripts/validate_environment.py @args
        $success = $LASTEXITCODE -eq 0
        
        if ($success) {
            Write-Status "✅ Backend $Env validation passed" "Green"
        } else {
            Write-Status "❌ Backend $Env validation failed" "Red"
        }
        
        return $success
    }
    catch {
        Write-Status "❌ Backend $Env validation failed with error: $_" "Red"
        return $false
    }
    finally {
        Pop-Location
    }
}

# Function to validate frontend environment
function Test-FrontendEnvironment {
    param([string]$Env)
    
    $args = @("--environment", $Env)
    
    if ($Strict) { $args += "--strict" }
    if ($Verbose) { $args += "--verbose" }
    if ($Json) { $args += "--json" }
    
    Write-Status "🔍 Validating frontend environment: $Env" "Blue"
    
    Push-Location frontend
    try {
        $result = & node scripts/validate-environment.js @args
        $success = $LASTEXITCODE -eq 0
        
        if ($success) {
            Write-Status "✅ Frontend $Env validation passed" "Green"
        } else {
            Write-Status "❌ Frontend $Env validation failed" "Red"
        }
        
        return $success
    }
    catch {
        Write-Status "❌ Frontend $Env validation failed with error: $_" "Red"
        return $false
    }
    finally {
        Pop-Location
    }
}

# Function to check prerequisites
function Test-Prerequisites {
    $missingFiles = @()
    
    # Check backend files
    if (-not (Test-Path "backend/scripts/validate_environment.py")) {
        $missingFiles += "backend/scripts/validate_environment.py"
    }
    
    if (-not (Test-Path "backend/app/config.py")) {
        $missingFiles += "backend/app/config.py"
    }
    
    # Check frontend files
    if (-not (Test-Path "frontend/scripts/validate-environment.js")) {
        $missingFiles += "frontend/scripts/validate-environment.js"
    }
    
    # Check environment files
    foreach ($env in $Environment) {
        if (-not (Test-Path "backend/.env.$env")) {
            $missingFiles += "backend/.env.$env"
        }
        
        if (-not (Test-Path "frontend/.env.$env")) {
            $missingFiles += "frontend/.env.$env"
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Status "❌ Missing required files:" "Red"
        foreach ($file in $missingFiles) {
            Write-Status "   - $file" "Red"
        }
        return $false
    }
    
    return $true
}

# Function to generate summary report
function Write-Summary {
    if (-not $Json) {
        Write-Host ""
        Write-Status "📊 Validation Summary" "Blue"
        Write-Host "   Total validations: $TotalValidations"
        Write-Host "   Passed: $PassedValidations"
        Write-Host "   Failed: $FailedValidations"
        Write-Host ""
        
        if ($FailedValidations -eq 0) {
            Write-Status "🎉 All environment validations passed!" "Green"
        } else {
            Write-Status "💥 $FailedValidations environment validation(s) failed!" "Red"
            Write-Status "   Please fix the issues above before deploying." "Yellow"
        }
    }
}

# Main execution
function Main {
    Write-Status "🚀 Starting comprehensive environment validation" "Blue"
    Write-Status "   Environments: $($Environment -join ', ')" "Blue"
    Write-Status "   Strict mode: $Strict" "Blue"
    Write-Status "   Verbose: $Verbose" "Blue"
    Write-Host ""
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Status "❌ Prerequisites check failed" "Red"
        exit 1
    }
    
    # Validate each environment
    foreach ($env in $Environment) {
        Write-Status "🔄 Validating environment: $env" "Yellow"
        Write-Host ""
        
        # Validate backend
        $script:TotalValidations++
        if (Test-BackendEnvironment $env) {
            $script:PassedValidations++
        } else {
            $script:FailedValidations++
            $script:ExitCode = 1
        }
        
        Write-Host ""
        
        # Validate frontend
        $script:TotalValidations++
        if (Test-FrontendEnvironment $env) {
            $script:PassedValidations++
        } else {
            $script:FailedValidations++
            $script:ExitCode = 1
        }
        
        Write-Host ""
        Write-Status "─────────────────────────────────────────" "Blue"
        Write-Host ""
    }
    
    # Generate summary
    Write-Summary
    
    exit $ExitCode
}

# Run main function
Main