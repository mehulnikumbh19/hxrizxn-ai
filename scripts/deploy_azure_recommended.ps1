param(
  [string]$SubscriptionId = "",
  [string]$Location = "eastus",
  [string]$ResourceGroup = "rg-hxrizxn-demo",
  [string]$EnvironmentName = "hxrizxn",
  [string]$AcrName = "",
  [string]$PostgresAdminPassword = "",
  [bool]$DemoMode = $true,
  [string]$FoundryIqEndpoint = "",
  [string]$FoundryIqApiKey = "",
  [string]$FoundryIqIndexName = "hxrizxn-demo",
  [string]$AzureOpenAiEndpoint = "",
  [string]$AzureOpenAiApiKey = "",
  [string]$AzureOpenAiDeployment = "",
  [switch]$SkipBuild = $false
)

$ErrorActionPreference = "Stop"

function Invoke-AzJson($Arguments) {
  $result = & az @Arguments --output json
  if ($LASTEXITCODE -ne 0) {
    throw "az $($Arguments -join ' ') failed"
  }
  if ([string]::IsNullOrWhiteSpace($result)) {
    return $null
  }
  return $result | ConvertFrom-Json
}

function Invoke-AzText($Arguments) {
  $result = & az @Arguments --output tsv
  if ($LASTEXITCODE -ne 0) {
    throw "az $($Arguments -join ' ') failed"
  }
  return $result
}

function Test-AcrExists($Name, $ResourceGroup) {
  $null = & az acr show --name $Name --resource-group $ResourceGroup --output none 2>$null
  return $LASTEXITCODE -eq 0
}

function Build-AndPushImage($ContextPath, $ImageTag, $AcrLoginServer, $AcrName) {
  $fullImage = "$AcrLoginServer/$ImageTag"
  $docker = Get-Command docker -ErrorAction SilentlyContinue
  if (-not $docker) {
    throw @"
Docker is required on this machine because the current Azure subscription does not allow ACR cloud builds (az acr build).
Install Docker Desktop, then rerun this script. GitHub Actions can also build and push with .github/workflows/build-push-acr.yml.
"@
  }

  Write-Host "Logging in to ACR $AcrName"
  & az acr login --name $AcrName | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az acr login --name $AcrName failed"
  }

  Write-Host "Building image $fullImage from $ContextPath"
  & docker build -t $fullImage $ContextPath
  if ($LASTEXITCODE -ne 0) {
    throw "docker build failed for $fullImage"
  }

  Write-Host "Pushing image $fullImage"
  & docker push $fullImage
  if ($LASTEXITCODE -ne 0) {
    throw "docker push failed for $fullImage"
  }
}

try {
  Invoke-AzJson @("account", "show") | Out-Null
} catch {
  Write-Host "Azure CLI is not logged in. Opening az login..."
  & az login | Out-Null
}

if (-not [string]::IsNullOrWhiteSpace($SubscriptionId)) {
  & az account set --subscription $SubscriptionId
}

$account = Invoke-AzJson @("account", "show")
Write-Host "Using subscription: $($account.name) ($($account.id))"

if ([string]::IsNullOrWhiteSpace($AcrName)) {
  $AcrName = ("hxr" + (Get-Random -Minimum 10000 -Maximum 99999) + "acr").ToLowerInvariant()
}

if ([string]::IsNullOrWhiteSpace($PostgresAdminPassword)) {
  $PostgresAdminPassword = "Hxz!" + [guid]::NewGuid().ToString("N").Substring(0, 20) + "9a"
  Write-Host "Generated a PostgreSQL admin password for this deployment. Store it from Azure if you need direct DB admin access."
}

$providers = @(
  "Microsoft.App",
  "Microsoft.ContainerRegistry",
  "Microsoft.DBforPostgreSQL",
  "Microsoft.Insights",
  "Microsoft.KeyVault",
  "Microsoft.ManagedIdentity",
  "Microsoft.OperationalInsights",
  "Microsoft.Storage"
)

foreach ($provider in $providers) {
  Write-Host "Registering provider $provider"
  & az provider register --namespace $provider | Out-Null
}

Write-Host "Creating resource group $ResourceGroup in $Location"
& az group create --name $ResourceGroup --location $Location | Out-Null

if (-not (Test-AcrExists $AcrName $ResourceGroup)) {
  Write-Host "Creating Azure Container Registry $AcrName in $Location"
  & az acr create --name $AcrName --resource-group $ResourceGroup --location $Location --sku Basic --admin-enabled false | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az acr create failed for $AcrName in $Location"
  }
}

$acrLoginServer = Invoke-AzText @("acr", "show", "--name", $AcrName, "--resource-group", $ResourceGroup, "--query", "loginServer")
$backendImage = "$acrLoginServer/hxrizxn-api:latest"
$frontendImage = "$acrLoginServer/hxrizxn-web:latest"

if (-not $SkipBuild) {
  Write-Host "Building and pushing backend image: $backendImage"
  Build-AndPushImage -ContextPath "apps/api" -ImageTag "hxrizxn-api:latest" -AcrLoginServer $acrLoginServer -AcrName $AcrName

  Write-Host "Building and pushing frontend image: $frontendImage"
  Build-AndPushImage -ContextPath "apps/web" -ImageTag "hxrizxn-web:latest" -AcrLoginServer $acrLoginServer -AcrName $AcrName
} else {
  Write-Host "Skipping image build/push. Expecting $backendImage and $frontendImage to already exist in ACR."
}

Write-Host "Deploying Bicep infrastructure and Container Apps"
$deployment = Invoke-AzJson @(
  "deployment", "group", "create",
  "--resource-group", $ResourceGroup,
  "--template-file", "infra/bicep/main.bicep",
  "--parameters",
  "location=$Location",
  "environmentName=$EnvironmentName",
  "acrName=$AcrName",
  "backendImage=$backendImage",
  "frontendImage=$frontendImage",
  "postgresAdminPassword=$PostgresAdminPassword",
  "demoMode=$DemoMode",
  "foundryIqEndpoint=$FoundryIqEndpoint",
  "foundryIqApiKey=$FoundryIqApiKey",
  "foundryIqIndexName=$FoundryIqIndexName",
  "azureOpenAiEndpoint=$AzureOpenAiEndpoint",
  "azureOpenAiApiKey=$AzureOpenAiApiKey",
  "azureOpenAiDeployment=$AzureOpenAiDeployment"
)

$outputs = $deployment.properties.outputs
Write-Host ""
Write-Host "Deployment complete."
Write-Host "API URL: $($outputs.apiUrl.value)"
Write-Host "Web URL: $($outputs.webUrl.value)"
Write-Host "ACR: $AcrName"
Write-Host "Resource group: $ResourceGroup"
Write-Host ""
Write-Host "Verify:"
Write-Host "  Invoke-RestMethod '$($outputs.apiUrl.value)/api/health'"
Write-Host "  Open '$($outputs.webUrl.value)'"

