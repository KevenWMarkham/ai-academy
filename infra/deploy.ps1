<#
.SYNOPSIS
Deploy the academy-api to Azure Container Apps (test tenant), end to end.

.DESCRIPTION
Two-phase, because the image lives in the ACR the template creates:
  1. Deploy infra (what-if validated) with a placeholder image.
  2. az acr build the real image server-side (no local Docker needed).
  3. Point the container app at the built image.
  4. Smoke-test /healthz and print the URL to stamp into the M365 package.

.EXAMPLE
./deploy.ps1 -ResourceGroup rg-ai-academy-test -Location eastus2 -ApiKey (Read-Host -AsSecureString | ConvertFrom-SecureString -AsPlainText)
#>
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [string]$Location = "eastus2",
    [string]$Prefix = "academy",
    [string]$ApiKey = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path $PSScriptRoot -Parent
$template = Join-Path $PSScriptRoot "main.bicep"
$image = "academy-api:latest"

Write-Host "== 1/4 infra (what-if, then deploy) =="
az group create --name $ResourceGroup --location $Location --output none
az deployment group what-if --resource-group $ResourceGroup --template-file $template `
    --parameters prefix=$Prefix apiKey=$ApiKey
az deployment group create --name academy-infra --resource-group $ResourceGroup `
    --template-file $template --parameters prefix=$Prefix apiKey=$ApiKey --output none

$acrName = az deployment group show -g $ResourceGroup -n academy-infra `
    --query properties.outputs.acrName.value -o tsv
$acrServer = az deployment group show -g $ResourceGroup -n academy-infra `
    --query properties.outputs.acrLoginServer.value -o tsv

Write-Host "== 2/4 build image in ACR ($acrName) =="
az acr build --registry $acrName --image $image $repoRoot

Write-Host "== 3/4 roll the container app to the built image =="
az deployment group create --name academy-infra --resource-group $ResourceGroup `
    --template-file $template `
    --parameters prefix=$Prefix apiKey=$ApiKey containerImage="$acrServer/$image" --output none

$baseUrl = az deployment group show -g $ResourceGroup -n academy-infra `
    --query properties.outputs.apiBaseUrl.value -o tsv

Write-Host "== 4/4 smoke test =="
$health = Invoke-RestMethod -Uri "$baseUrl/healthz" -TimeoutSec 60
Write-Host "healthz: $($health | ConvertTo-Json -Compress)"

Write-Host ""
Write-Host "API deployed:  $baseUrl"
Write-Host "Portal:        https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$ResourceGroup"
Write-Host ""
Write-Host "Next: build the Copilot package against this URL:"
Write-Host "  ..\m365\package.ps1 -ApiBaseUrl $baseUrl"
