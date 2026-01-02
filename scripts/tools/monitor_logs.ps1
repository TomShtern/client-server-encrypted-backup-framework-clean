# PowerShell Script for Live Log Monitoring - CyberBackup 3.0
# Usage: .\scripts\monitor_logs.ps1 [ServerType] [TailLines]
# ServerType: api, backup, or both (default: both)
# TailLines: Number of lines to show from end (default: 50)

param(
    [string]$ServerType = "both",
    [int]$TailLines = 50
)

Write-Host "CyberBackup 3.0 - Live Log Monitor (PowerShell)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if logs directory exists
if (!(Test-Path "logs")) {
    Write-Host "ERROR: logs directory not found!" -ForegroundColor Red
    Write-Host "Make sure the servers have been started at least once." -ForegroundColor Yellow
    exit 1
}

# Get available log files
$LogFiles = @()
Get-ChildItem "logs\*.log" | Where-Object { $_.Name -notlike "latest-*" } | ForEach-Object {
    $ServerName = ""
    $Color = "White"
    
    if ($_.Name -like "*api-server*") {
        $ServerName = "API Server"
        $Color = "Blue"
    } elseif ($_.Name -like "*backup-server*") {
        $ServerName = "Backup Server"
        $Color = "Green"
    } else {
        return  # Skip unknown log types
    }
    
    $LogFiles += @{
        Path = $_.FullName
        Name = $_.Name
        ServerName = $ServerName
        Color = $Color
        Modified = $_.LastWriteTime
    }
}

# Sort by modification time (newest first)
$LogFiles = $LogFiles | Sort-Object { $_.Modified } -Descending

if ($LogFiles.Count -eq 0) {
    Write-Host "No log files found in logs directory!" -ForegroundColor Red
    exit 1
}

# Filter by server type
$FilesToMonitor = @()
foreach ($LogFile in $LogFiles) {
    if ($ServerType -eq "both") {
        $FilesToMonitor += $LogFile
    } elseif ($ServerType -eq "api" -and $LogFile.ServerName -eq "API Server") {
        $FilesToMonitor += $LogFile
    } elseif ($ServerType -eq "backup" -and $LogFile.ServerName -eq "Backup Server") {
        $FilesToMonitor += $LogFile
    }
}

if ($FilesToMonitor.Count -eq 0) {
    Write-Host "No matching log files found for server type: $ServerType" -ForegroundColor Red
    exit 1
}

# Display files to monitor
Write-Host "Monitoring Files:" -ForegroundColor Yellow
foreach ($File in $FilesToMonitor) {
    Write-Host "  - " -NoNewline
    Write-Host $File.ServerName -ForegroundColor $File.Color -NoNewline
    Write-Host ": $($File.Name)"
}
Write-Host ""
Write-Host "Showing last $TailLines lines, then following new content..." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
Write-Host ("=" * 80) -ForegroundColor DarkGray
Write-Host ""

# Function to colorize log lines
function Get-ColorizedLogLine {
    param([string]$Line, [string]$ServerPrefix, [string]$ServerColor)
    
    $Timestamp = Get-Date -Format "HH:mm:ss"
    $LineUpper = $Line.ToUpper()
    
    # Determine log level color
    $LogColor = "White"
    if ($LineUpper -match " DEBUG ") { $LogColor = "DarkGray" }
    elseif ($LineUpper -match " INFO ") { $LogColor = "Cyan" }
    elseif ($LineUpper -match " WARNING ") { $LogColor = "Yellow" }
    elseif ($LineUpper -match " ERROR ") { $LogColor = "Red" }
    elseif ($LineUpper -match " CRITICAL ") { $LogColor = "Magenta" }
    
    # Output formatted line
    Write-Host "[$Timestamp] " -ForegroundColor DarkGray -NoNewline
    Write-Host "[$ServerPrefix] " -ForegroundColor $ServerColor -NoNewline
    Write-Host $Line -ForegroundColor $LogColor
}

try {
    if ($FilesToMonitor.Count -eq 1) {
        # Monitor single file
        $File = $FilesToMonitor[0]
        $ServerPrefix = if ($File.ServerName -eq "API Server") { "API" } else { "BCK" }
        
        Get-Content $File.Path -Tail $TailLines -Wait | ForEach-Object {
            Get-ColorizedLogLine -Line $_ -ServerPrefix $ServerPrefix -ServerColor $File.Color
        }
    } else {
        # Monitor multiple files (requires PowerShell jobs)
        Write-Host "Multi-file monitoring requires PowerShell background jobs..." -ForegroundColor Yellow
        Write-Host "Starting monitoring jobs for each file..." -ForegroundColor Yellow
        Write-Host ""
        
        $Jobs = @()
        foreach ($File in $FilesToMonitor) {
            $ServerPrefix = if ($File.ServerName -eq "API Server") { "API" } else { "BCK" }
            
            $Job = Start-Job -ScriptBlock {
                param($FilePath, $ServerPrefix, $ServerColor, $TailLines)
                
                Get-Content $FilePath -Tail $TailLines -Wait | ForEach-Object {
                    $Timestamp = Get-Date -Format "HH:mm:ss"
                    Write-Output "[$Timestamp] [$ServerPrefix] $_"
                }
            } -ArgumentList $File.Path, $ServerPrefix, $File.Color, $TailLines
            
            $Jobs += $Job
        }
        
        # Display output from all jobs
        while ($true) {
            foreach ($Job in $Jobs) {
                $Output = Receive-Job $Job
                if ($Output) {
                    foreach ($Line in $Output) {
                        # Parse the line to extract server prefix and colorize
                        if ($Line -match '^\[([\d:]+)\] \[(\w+)\] (.*)$') {
                            $Time = $Matches[1]
                            $Server = $Matches[2]
                            $Message = $Matches[3]
                            
                            $Color = if ($Server -eq "API") { "Blue" } else { "Green" }
                            
                            Write-Host "[$Time] " -ForegroundColor DarkGray -NoNewline
                            Write-Host "[$Server] " -ForegroundColor $Color -NoNewline
                            
                            # Colorize by log level
                            $LogColor = "White"
                            $MessageUpper = $Message.ToUpper()
                            if ($MessageUpper -match " DEBUG ") { $LogColor = "DarkGray" }
                            elseif ($MessageUpper -match " INFO ") { $LogColor = "Cyan" }
                            elseif ($MessageUpper -match " WARNING ") { $LogColor = "Yellow" }
                            elseif ($MessageUpper -match " ERROR ") { $LogColor = "Red" }
                            elseif ($MessageUpper -match " CRITICAL ") { $LogColor = "Magenta" }
                            
                            Write-Host $Message -ForegroundColor $LogColor
                        } else {
                            Write-Host $Line
                        }
                    }
                }
            }
            Start-Sleep -Milliseconds 100
        }
    }
} catch {
    Write-Host ""
    Write-Host "Monitoring stopped" -ForegroundColor Yellow
} finally {
    # Clean up jobs if they exist
    if ($Jobs) {
        Write-Host "Cleaning up background jobs..." -ForegroundColor Yellow
        $Jobs | Stop-Job -ErrorAction SilentlyContinue
        $Jobs | Remove-Job -ErrorAction SilentlyContinue
    }
}