# Launch Godot editor with AETHRAS project
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$GodotProject = Join-Path $Root "game\godot"

# Try common Godot locations
$GodotExe = $null
$cmd = Get-Command godot -ErrorAction SilentlyContinue
$paths = @(
    $(if ($cmd) { $cmd.Source }),
    "$env:LOCALAPPDATA\Microsoft\WinGet\Links\godot.exe",
    "$env:LOCALAPPDATA\Programs\Godot\Godot*.exe"
)
foreach ($p in $paths) {
    if ($p -and (Test-Path $p)) { $GodotExe = $p; break }
}
if (-not $GodotExe) {
    $found = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter "Godot*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $GodotExe = $found.FullName }
}

if (-not $GodotExe) {
    Write-Error "Godot not found. Install via: winget install GodotEngine.GodotEngine"
}

Write-Host "Launching Godot: $GodotExe"
& $GodotExe --path $GodotProject --import
& $GodotExe --path $GodotProject
