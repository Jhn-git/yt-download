# YT-Download Setup Script
# Configures Python environment and dependencies for the YT-Download project

param(
    [switch]$Force,
    [switch]$SkipVenv
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

Write-Host "$Blue"
Write-Host "YT-Download Setup Script"
Write-Host "========================$Reset"
Write-Host ""

# Check execution policy
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Warning "PowerShell execution policy is Restricted"
    Write-Host "Run this command as Administrator to fix:"
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine"
    Write-Host ""
    Read-Host "Press Enter to continue anyway (may fail)"
}

# Check if Python is installed
Write-Info "Checking Python installation..."
if (-not (Test-Command "python")) {
    Write-Error "Python is not installed or not in PATH!"
    Write-Host "Please install Python 3.8+ from https://python.org"
    Write-Host "Make sure to check 'Add Python to PATH' during installation"
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>$null
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $majorVersion = [int]$Matches[1]
    $minorVersion = [int]$Matches[2]
    
    if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
        Write-Error "Python version $pythonVersion is not supported!"
        Write-Host "Please install Python 3.8 or higher"
        exit 1
    }
    Write-Success "Python $pythonVersion found"
} else {
    Write-Warning "Could not determine Python version, continuing..."
}

# Check required files
Write-Info "Checking required files..."
$requiredFiles = @("setup.py", "requirements.txt", "config.json", "YT-Download-GUI.spec")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Error "Missing required files:"
    foreach ($file in $missingFiles) {
        Write-Host "  - $file"
    }
    exit 1
}
Write-Success "All required files present"

# Create/activate virtual environment
if (-not $SkipVenv) {
    Write-Info "Setting up Python virtual environment..."
    
    if (Test-Path ".venv" -PathType Container) {
        if ($Force) {
            Write-Info "Removing existing virtual environment..."
            # Deactivate if currently active
            if ($env:VIRTUAL_ENV) {
                Write-Info "Deactivating current virtual environment..."
                deactivate 2>$null
            }
            # Force remove with retry
            try {
                Remove-Item -Recurse -Force ".venv" -ErrorAction Stop
            }
            catch {
                Write-Warning "Failed to remove .venv, trying alternative method..."
                # Use robocopy to remove stubborn directories on Windows
                cmd /c "rmdir /s /q .venv" 2>$null
                Start-Sleep -Seconds 1
                if (Test-Path ".venv") {
                    Write-Error "Could not remove existing virtual environment. Please manually delete .venv folder and try again."
                    exit 1
                }
            }
        } else {
            Write-Warning "Virtual environment already exists"
            if ($env:VIRTUAL_ENV -and $env:VIRTUAL_ENV.Contains(".venv")) {
                Write-Warning "You are currently inside the virtual environment that needs to be recreated."
                Write-Host "Please run: deactivate"
                Write-Host "Then run setup.ps1 again, or use: .\setup.ps1 -Force"
                exit 1
            }
            $response = Read-Host "Remove and recreate? (y/N)"
            if ($response -match "^[Yy]") {
                try {
                    Remove-Item -Recurse -Force ".venv" -ErrorAction Stop
                }
                catch {
                    Write-Warning "Failed to remove .venv, trying alternative method..."
                    cmd /c "rmdir /s /q .venv" 2>$null
                    Start-Sleep -Seconds 1
                    if (Test-Path ".venv") {
                        Write-Error "Could not remove existing virtual environment. Please manually delete .venv folder and try again."
                        exit 1
                    }
                }
            }
        }
    }
    
    if (-not (Test-Path ".venv" -PathType Container)) {
        Write-Info "Creating virtual environment..."
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment!"
            exit 1
        }
        Write-Success "Virtual environment created"
    }
    
    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
        Write-Success "Virtual environment activated"
    } else {
        Write-Error "Could not find virtual environment activation script!"
        exit 1
    }
    
    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to upgrade pip, continuing..."
    } else {
        Write-Success "Pip upgraded"
    }
}

# Install runtime dependencies
Write-Info "Installing runtime dependencies..."
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install runtime dependencies!"
        exit 1
    }
    Write-Success "Runtime dependencies installed"
}

# Install build dependencies
Write-Info "Installing build dependencies..."
python -m pip install pyinstaller setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install build dependencies!"
    exit 1
}
Write-Success "Build dependencies installed"

# Install package in development mode
Write-Info "Installing package in development mode..."
python -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install package in development mode!"
    exit 1
}
Write-Success "Package installed in development mode"

# Check/download yt-dlp.exe for Windows
Write-Info "Checking yt-dlp binary..."
$binariesDir = "binaries"
$ytdlpExe = "$binariesDir\yt-dlp.exe"

if (-not (Test-Path $binariesDir -PathType Container)) {
    Write-Info "Creating binaries directory..."
    New-Item -ItemType Directory -Path $binariesDir | Out-Null
}

if (-not (Test-Path $ytdlpExe)) {
    Write-Warning "Windows yt-dlp.exe not found in binaries/"
    $response = Read-Host "Download yt-dlp.exe automatically? (Y/n)"
    
    if ($response -notmatch "^[Nn]") {
        Write-Info "Downloading yt-dlp.exe..."
        try {
            $url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
            Invoke-WebRequest -Uri $url -OutFile $ytdlpExe
            Write-Success "yt-dlp.exe downloaded successfully"
        }
        catch {
            Write-Error "Failed to download yt-dlp.exe: $($_.Exception.Message)"
            Write-Host "Please manually download from: https://github.com/yt-dlp/yt-dlp"
            Write-Host "And place in: $ytdlpExe"
        }
    } else {
        Write-Warning "Please manually download yt-dlp.exe to: $ytdlpExe"
    }
} else {
    Write-Success "yt-dlp.exe found in binaries/"
}

# Verify installation
Write-Info "Verifying installation..."
try {
    $result = python -c "import ytdl; print('Package import successful')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Package import verification passed"
    } else {
        Write-Warning "Package import verification failed, but continuing..."
    }
}
catch {
    Write-Warning "Could not verify package import"
}

# Check console scripts
Write-Info "Checking console scripts..."
try {
    $ytdlHelp = ytdl --help 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "ytdl command available"
    }
}
catch {
    Write-Warning "ytdl command not available, try: python src\ytdl\main.py"
}

try {
    $ytdlGuiHelp = ytdl-gui --help 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "ytdl-gui command available"
    }
}
catch {
    Write-Warning "ytdl-gui command not available, try: python src\ytdl\gui_main.py"
}

Write-Host ""
Write-Host "$Green"
Write-Host "========================"
Write-Host "Setup completed successfully!"
Write-Host "========================$Reset"
Write-Host ""
Write-Host "You can now:"
Write-Host "  • Run GUI: ${Blue}ytdl-gui$Reset (or ${Blue}python src\ytdl\gui_main.py$Reset)"
Write-Host "  • Run CLI: ${Blue}ytdl [URL]$Reset (or ${Blue}python src\ytdl\main.py [URL]$Reset)"
Write-Host "  • Build executable: ${Blue}.\build.ps1$Reset"
Write-Host "  • Run tests: ${Blue}python tools\run_tests.py$Reset"
Write-Host ""

if (-not $SkipVenv) {
    Write-Host "${Yellow}Note: Virtual environment is activated for this session$Reset"
    Write-Host "${Yellow}For future sessions, run: .venv\Scripts\Activate.ps1$Reset"
    Write-Host ""
}

# Final status
Write-Success "Setup complete! Ready for development and building."