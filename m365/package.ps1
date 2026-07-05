<#
.SYNOPSIS
Build the M365 Copilot app package (zip) for sideloading or admin-center upload.

.DESCRIPTION
Stamps the deployed academy-api base URL into openapi.json and zips the appPackage
contents (files at the archive root, as the platform requires).

.EXAMPLE
./package.ps1 -ApiBaseUrl "https://ca-academy-api.<env>.eastus2.azurecontainerapps.io"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$ApiBaseUrl,

    [string]$OutFile = "$PSScriptRoot\dist\hr-service-delivery-agent.zip"
)

$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "appPackage"
$staging = Join-Path $env:TEMP ("academy-apppkg-" + [guid]::NewGuid().ToString("N"))

New-Item -ItemType Directory -Path $staging | Out-Null
Copy-Item "$src\*" $staging -Recurse

# Stamp the deployed API base URL into the OpenAPI servers entry.
$openapi = Join-Path $staging "openapi.json"
(Get-Content $openapi -Raw).Replace("__ACADEMY_API_BASE_URL__", $ApiBaseUrl.TrimEnd("/")) |
    Set-Content $openapi -Encoding utf8

$missing = @("manifest.json", "declarativeAgent.json", "ai-plugin.json", "openapi.json",
             "color.png", "outline.png") | Where-Object { -not (Test-Path (Join-Path $staging $_)) }
if ($missing) {
    throw "app package is missing: $($missing -join ', ') (run scripts/make_icons.py for the icons)"
}

New-Item -ItemType Directory -Force -Path (Split-Path $OutFile) | Out-Null
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }
Compress-Archive -Path "$staging\*" -DestinationPath $OutFile
Remove-Item $staging -Recurse -Force

Write-Host "app package written -> $OutFile"
Write-Host "next: sideload via Agents Toolkit, or upload in the Teams admin center (docs/07)."
