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
  $oldEap = $ErrorActionPreference
  $ErrorActionPreference = "SilentlyContinue"
  $count = & az acr list --resource-group $ResourceGroup --query "[?name=='$Name'] | length(@)" --output tsv 2>$null
  $ErrorActionPreference = $oldEap
  if ($LASTEXITCODE -ne 0) {
    return $false
  }
  return [int]$count -gt 0
}

function Build-WithDocker($ContextPath, $ImageTag, $AcrLoginServer, $AcrName) {
  $fullImage = "$AcrLoginServer/$ImageTag"
  $docker = Get-Command docker -ErrorAction SilentlyContinue
  if (-not $docker) {
    throw @"
ACR cloud build failed and Docker is not installed on this machine.
Install Docker Desktop or rerun after Azure Container Registry cloud builds are available.
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

function Build-AndPushImage($ContextPath, $ImageTag, $AcrLoginServer, $AcrName) {
  Write-Host "Building image in Azure Container Registry: $ImageTag"
  & az acr build --registry $AcrName --image $ImageTag $ContextPath --output none
  if ($LASTEXITCODE -eq 0) {
    return
  }

  Write-Host "ACR cloud build failed. Falling back to local Docker build/push."
  Build-WithDocker -ContextPath $ContextPath -ImageTag $ImageTag -AcrLoginServer $AcrLoginServer -AcrName $AcrName
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

$oldEap = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$existingGroup = & az group show --name $ResourceGroup --output json 2>$null
$ErrorActionPreference = $oldEap
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($existingGroup)) {
  $group = $existingGroup | ConvertFrom-Json
  if ($group.location -ne $Location) {
    Write-Host "Resource group $ResourceGroup already exists in $($group.location). Using that location instead of $Location."
    $Location = $group.location
  } else {
    Write-Host "Resource group $ResourceGroup already exists in $Location"
  }
} else {
  Write-Host "Creating resource group $ResourceGroup in $Location"
  & az group create --name $ResourceGroup --location $Location | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az group create failed for $ResourceGroup in $Location"
  }
}

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
