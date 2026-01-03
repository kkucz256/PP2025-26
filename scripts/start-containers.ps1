param(
    [switch]$FollowLogs
)

Write-Host "Running: docker-compose up -d --build"
$proc = Start-Process -FilePath "docker-compose" -ArgumentList "up -d --build" -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    Write-Error "docker-compose returned exit code $($proc.ExitCode)"
    exit $proc.ExitCode
}

Write-Host "Containers started (detached). Use 'docker-compose logs -f' to follow logs."
if ($FollowLogs) {
    Write-Host "Opening new PowerShell window to follow logs..."
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","docker-compose logs -f"
}