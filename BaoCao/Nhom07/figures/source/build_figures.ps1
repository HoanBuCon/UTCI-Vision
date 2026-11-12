$ErrorActionPreference = 'Stop'
$sourceDir = $PSScriptRoot
$figureDir = Split-Path $sourceDir -Parent
$reportDir = Split-Path $figureDir -Parent
$outputDir = Join-Path $reportDir 'build\figure-assets'
New-Item -ItemType Directory -Force $outputDir | Out-Null
Push-Location $sourceDir
try {
    foreach ($figure in Get-ChildItem -LiteralPath $sourceDir -Filter 'fig_*.tex') {
        $logPath = Join-Path $outputDir ($figure.BaseName + '-build.txt')
        & xelatex -interaction=nonstopmode -halt-on-error -file-line-error "-output-directory=$outputDir" $figure.Name *> $logPath
        if ($LASTEXITCODE -ne 0) { throw "Biên dịch thất bại: $($figure.Name). Xem $logPath" }
        $pdfPath = Join-Path $outputDir ($figure.BaseName + '.pdf')
        Copy-Item -LiteralPath $pdfPath -Destination (Join-Path $figureDir ($figure.BaseName + '.pdf')) -Force
        & pdftocairo -svg $pdfPath (Join-Path $figureDir ($figure.BaseName + '.svg'))
        if ($LASTEXITCODE -ne 0) { throw "Không xuất được SVG: $($figure.Name)" }
        Write-Output "Đã tạo $($figure.BaseName).svg và .pdf"
    }
}
finally { Pop-Location }
