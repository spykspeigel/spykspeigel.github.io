$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$cvDir = Join-Path $repoRoot "cv"
$outputPdf = Join-Path $repoRoot "files\cv.pdf"

Push-Location $cvDir
try {
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  Copy-Item -LiteralPath "main.pdf" -Destination $outputPdf -Force
  Remove-Item -LiteralPath "main.aux", "main.log", "main.out", "main.pdf" -Force -ErrorAction SilentlyContinue
}
finally {
  Pop-Location
}
