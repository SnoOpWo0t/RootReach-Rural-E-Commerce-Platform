$targetDir = "f:\RootReach-Rural-E-Commerce-Platform\downloaded_images"
New-Item -ItemType Directory -Force -Path $targetDir

Write-Host "Fetching file list from GitHub API..."
try {
    $files = Invoke-RestMethod -Uri "https://api.github.com/repos/HAVIC-47/portfolio/contents/public/projects/rootreach"
} catch {
    Write-Host "Error fetching from GitHub API: $_"
    exit 1
}

foreach ($file in $files) {
    if ($file.type -eq "file") {
        $outFile = Join-Path $targetDir $file.name
        Write-Host "Downloading $($file.name)..."
        try {
            Invoke-WebRequest -Uri $file.download_url -OutFile $outFile
        } catch {
            Write-Host "Failed to download $($file.name): $_"
        }
    }
}
Write-Host "Download completed. Files saved to $targetDir"
