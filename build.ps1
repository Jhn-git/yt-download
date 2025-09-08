# YT-Download Build Script  
# Creates Windows executable using PyInstaller

param(
    [switch]$Clean,
    [switch]$Test,
    [string]$OutputDir = "dist"
)

# Colors for output
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m" 
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Success($Message) {
    Write-Host "$Green✓ $Message$Reset"
}

function Write-Error($Message) {
    Write-Host "$Red✗ $Message$Reset"
}

function Write-Warning($Message) {
    Write-Host "$Yellow⚠ $Message$Reset"
}

function Write-Info($Message) {
    Write-Host "$Blue→ $Message$Reset"
}

function Test-Command($Command) {
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Get-FileSize($Path) {
    if (Test-Path $Path) {
        $size = (Get-Item $Path).Length
        return [math]::Round($size / 1MB, 1)
    }
    return 0
}

Write-Host "$Blue"
Write-Host "YT-Download Build Script"
Write-Host "========================$Reset"
Write-Host ""

# Check if setup has been run
Write-Info "Checking setup requirements..."

if (-not (Test-Path ".venv" -PathType Container) -and -not $env:VIRTUAL_ENV) {
    Write-Error "Virtual environment not found!"
    Write-Host "Please run setup.ps1 first to configure the environment:"
    Write-Host "  .\setup.ps1"
    exit 1
}

# Activate virtual environment if not already active
if (-not $env:VIRTUAL_ENV) {
    Write-Info "Activating virtual environment..."
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
        Write-Success "Virtual environment activated"
    } else {
        Write-Error "Could not find virtual environment activation script!"
        exit 1
    }
} else {
    Write-Success "Virtual environment already active"
}

# Check Python and PyInstaller
Write-Info "Verifying build tools..."

if (-not (Test-Command "python")) {
    Write-Error "Python not found in PATH!"
    exit 1
}

try {
    python -m PyInstaller --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller check failed"
    }
    Write-Success "PyInstaller available"
}
catch {
    Write-Error "PyInstaller not installed!"
    Write-Host "Install with: python -m pip install pyinstaller"
    Write-Host "Or run setup.ps1 to install all dependencies"
    exit 1
}

# Check required files
Write-Info "Checking build requirements..."
$requiredFiles = @(
    "YT-Download-GUI.spec",
    "config.json",
    "src\ytdl\gui_main.py"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Error "Missing required files for build:"
    foreach ($file in $missingFiles) {
        Write-Host "  - $file"
    }
    exit 1
}
Write-Success "All build files present"

# Check yt-dlp binary
Write-Info "Checking yt-dlp binary..."
$ytdlpExe = "binaries\yt-dlp.exe"
$ytdlpLinux = "binaries\yt-dlp_linux"

if (Test-Path $ytdlpExe) {
    Write-Success "Found yt-dlp.exe for Windows build"
    $binaryFound = $true
} elseif (Test-Path $ytdlpLinux) {
    Write-Warning "Found yt-dlp_linux instead of yt-dlp.exe"
    Write-Warning "Windows executable may not work correctly"
    $binaryFound = $true
} else {
    Write-Error "No yt-dlp binary found!"
    Write-Host "Expected: $ytdlpExe"
    Write-Host "Download from: https://github.com/yt-dlp/yt-dlp"
    exit 1
}

# Clean previous builds
if ($Clean -or (Test-Path "build") -or (Test-Path $OutputDir)) {
    Write-Info "Cleaning previous build artifacts..."
    
    if (Test-Path "build") {
        Remove-Item -Recurse -Force "build"
        Write-Success "Removed build/ directory"
    }
    
    if (Test-Path $OutputDir) {
        Remove-Item -Recurse -Force $OutputDir
        Write-Success "Removed $OutputDir/ directory"
    }
    
    # Clean .pyc files
    Get-ChildItem -Recurse -Include "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force
    Write-Success "Cleaned Python cache files"
}

# Build executable
Write-Info "Building Windows executable..."
Write-Host ""

$buildStartTime = Get-Date
try {
    python -m PyInstaller YT-Download-GUI.spec --clean --noconfirm
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Error "Build failed: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Common solutions:"
    Write-Host "  • Ensure all dependencies are installed (run setup.ps1)"
    Write-Host "  • Check that source files exist in src/ytdl/"
    Write-Host "  • Verify YT-Download-GUI.spec is correct"
    exit 1
}

$buildEndTime = Get-Date
$buildTime = [math]::Round(($buildEndTime - $buildStartTime).TotalSeconds, 1)

Write-Host ""
Write-Success "Build completed in $buildTime seconds"

# Verify executable was created
$executablePath = "$OutputDir\YT-Download-GUI.exe"
Write-Info "Verifying executable..."

if (-not (Test-Path $executablePath)) {
    Write-Error "Executable was not created at: $executablePath"
    Write-Host ""
    Write-Host "Check PyInstaller output above for errors"
    exit 1
}

$exeSize = Get-FileSize $executablePath
Write-Success "Executable created: $executablePath"
Write-Success "Size: $exeSize MB"

# Test executable if requested
if ($Test) {
    Write-Info "Testing executable..."
    
    try {
        # Test that it launches and shows help
        $testResult = & $executablePath --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Executable launches successfully"
        } else {
            Write-Warning "Executable launched but returned non-zero exit code"
        }
    }
    catch {
        Write-Warning "Could not test executable: $($_.Exception.Message)"
    }
}

# Final summary
Write-Host ""
Write-Host "$Green"
Write-Host "========================"
Write-Host "Build completed successfully!"
Write-Host "========================$Reset"
Write-Host ""
Write-Host "Executable: ${Blue}$executablePath$Reset"
Write-Host "Size: ${Blue}$exeSize MB$Reset"
Write-Host "Build time: ${Blue}$buildTime seconds$Reset"
Write-Host ""
Write-Host "Usage:"
Write-Host "  • Run: ${Blue}$executablePath$Reset"
Write-Host "  • Test: ${Blue}.\build.ps1 -Test$Reset"
Write-Host "  • Clean build: ${Blue}.\build.ps1 -Clean$Reset"
Write-Host ""

# Distribution notes
Write-Host "${Yellow}Distribution Notes:$Reset"
Write-Host "  ✓ Standalone executable - no Python required"
Write-Host "  ✓ Includes all dependencies and yt-dlp binary"
Write-Host "  ✓ Can be copied to any Windows machine"
Write-Host ""

Write-Success "Ready for distribution!"