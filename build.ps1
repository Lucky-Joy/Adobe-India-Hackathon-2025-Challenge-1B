# build.ps1

param(
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

function Log($type, $msg) {
    $color = @{ "INFO" = "Blue"; "SUCCESS" = "Green"; "WARNING" = "Yellow"; "ERROR" = "Red" }[$type]
    Write-Host "[$type] $msg" -ForegroundColor $color
}

function Check-Prereqs {
    Log "INFO" "Checking prerequisites..."
    try { docker --version | Out-Null; Log "SUCCESS" "Docker OK" } catch { Log "ERROR" "Docker missing"; exit 1 }
    try { python --version | Out-Null; Log "SUCCESS" "Python OK" } catch { Log "ERROR" "Python missing"; exit 1 }
}

function Install-Dependencies {
    if (Test-Path "Challenge_1b\requirements.txt") {
        pip install -r "Challenge_1b\requirements.txt"
        Log "SUCCESS" "Challenge 1B dependencies installed"
    }
}

function Build-Challenge1B {
    Log "INFO" "Building Challenge 1B Docker image..."
    Push-Location Challenge_1b
    docker build --platform linux/amd64 -t adobe-challenge1b . || { Log "ERROR" "Build failed"; Pop-Location; exit 1 }
    Pop-Location
    Log "SUCCESS" "Docker build completed"
}

function Run-Challenge1B {
    Log "INFO" "Running Challenge 1B..."
    docker run --rm \
        -v "$(Resolve-Path Challenge_1b):/app/collections" \
        --network none \
        adobe-challenge1b
    Log "SUCCESS" "Execution finished"
}

function Validate-Docs {
    $required = @(
        "Challenge_1b\Dockerfile",
        "Challenge_1b\requirements.txt",
        "Challenge_1b\README.md",
        "Challenge_1b\approach_explanation.md"
    )
    foreach ($file in $required) {
        if (!(Test-Path $file)) { Log "WARNING" "Missing $file" }
    }
    Log "SUCCESS" "Documentation check done"
}

Check-Prereqs
Install-Dependencies
Build-Challenge1B
if (-not $SkipTests) { Run-Challenge1B }
Validate-Docs
Log "SUCCESS" "🎉 Challenge 1B script complete"