param(
  [string]$SubscriptionId = "",
  [string]$Location = "westus3",
  [string]$ResourceGroup = "rg-hxrizxn-demo",
  [string]$NameSuffix = "",
  [string]$PostgresLocation = "",
  [string]$PostgresName = "",
  [string]$PostgresPublicAccess = "0.0.0.0",
  [string]$PostgresAdminUser = "hxrizxnadmin",
  [string]$PostgresAdminPassword = "",
  [bool]$DemoMode = $true
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

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

function Test-AzResource($Arguments) {
  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    $null = & az @Arguments --output none 2>$null
    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorActionPreference
  }
  return $exitCode -eq 0
}

function Ensure-Provider($Namespace) {
  Write-Host "Registering provider $Namespace"
  & az provider register --namespace $Namespace | Out-Null
  for ($i = 0; $i -lt 30; $i++) {
    $state = Invoke-AzText @("provider", "show", "--namespace", $Namespace, "--query", "registrationState")
    if ($state -eq "Registered") {
      return
    }
    Start-Sleep -Seconds 10
  }
  throw "Provider $Namespace did not reach Registered state in time"
}

function New-ZipPackage($SourceDir, $StageDir, $ZipPath) {
  if (Test-Path $StageDir) {
    Remove-Item -LiteralPath $StageDir -Recurse -Force
  }
  New-Item -ItemType Directory -Path $StageDir | Out-Null

  $excluded = @(
    ".env",
    ".next",
    ".pytest_cache",
    "__pycache__",
    "hxrizxn.db",
    "node_modules",
    "playwright-report",
    "test-results",
    "uploads"
  )

  Get-ChildItem -Path $SourceDir -Force | Where-Object {
    $excluded -notcontains $_.Name
  } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $StageDir -Recurse -Force
  }

  if (Test-Path $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
  }
  Compress-Archive -Path (Join-Path $StageDir "*") -DestinationPath $ZipPath -Force
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

if ([string]::IsNullOrWhiteSpace($NameSuffix)) {
  $NameSuffix = $account.id.Replace("-", "").Substring(0, 8).ToLowerInvariant()
}

$planName = "hxrizxn-plan-$NameSuffix"
$apiName = "hxrizxn-api-$NameSuffix"
$webName = "hxrizxn-web-$NameSuffix"
if ([string]::IsNullOrWhiteSpace($PostgresName)) {
  $PostgresName = "hxrizxn-pg-$NameSuffix"
}
$storageName = ("hxrstore" + $NameSuffix).ToLowerInvariant()
$keyVaultName = "hxrizxn-kv-$NameSuffix"
$apiUrl = "https://$apiName.azurewebsites.net"
$webUrl = "https://$webName.azurewebsites.net"

if ([string]::IsNullOrWhiteSpace($PostgresAdminPassword)) {
  $PostgresAdminPassword = "Hxz!" + [guid]::NewGuid().ToString("N").Substring(0, 20) + "9a"
  Write-Host "Generated a PostgreSQL admin password for this deployment."
}

Ensure-Provider "Microsoft.Web"
Ensure-Provider "Microsoft.DBforPostgreSQL"
Ensure-Provider "Microsoft.Storage"
Ensure-Provider "Microsoft.KeyVault"

$existingGroup = & az group show --name $ResourceGroup --output json 2>$null
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

if ([string]::IsNullOrWhiteSpace($PostgresLocation)) {
  $PostgresLocation = $Location
}

if (-not (Test-AzResource @("appservice", "plan", "show", "--name", $planName, "--resource-group", $ResourceGroup))) {
  Write-Host "Creating App Service plan $planName"
  & az appservice plan create --name $planName --resource-group $ResourceGroup --location $Location --is-linux --sku B1 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az appservice plan create failed for $planName"
  }
}

if (-not (Test-AzResource @("storage", "account", "show", "--name", $storageName, "--resource-group", $ResourceGroup))) {
  Write-Host "Creating Storage account $storageName"
  & az storage account create --name $storageName --resource-group $ResourceGroup --location $Location --sku Standard_LRS --kind StorageV2 --allow-blob-public-access false --min-tls-version TLS1_2 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az storage account create failed for $storageName"
  }
}

$storageKey = Invoke-AzText @("storage", "account", "keys", "list", "--account-name", $storageName, "--resource-group", $ResourceGroup, "--query", "[0].value")
$storageConnectionString = "DefaultEndpointsProtocol=https;AccountName=$storageName;AccountKey=$storageKey;EndpointSuffix=core.windows.net"
& az storage container create --name uploads --account-name $storageName --account-key $storageKey --public-access off | Out-Null
if ($LASTEXITCODE -ne 0) {
  throw "az storage container create failed for uploads"
}

if (-not (Test-AzResource @("keyvault", "show", "--name", $keyVaultName, "--resource-group", $ResourceGroup))) {
  Write-Host "Creating Key Vault $keyVaultName"
  & az keyvault create --name $keyVaultName --resource-group $ResourceGroup --location $Location --sku standard --enable-rbac-authorization false | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az keyvault create failed for $keyVaultName"
  }
}

$postgresExists = Test-AzResource @("postgres", "flexible-server", "show", "--name", $PostgresName, "--resource-group", $ResourceGroup)
if (-not $postgresExists) {
  Write-Host "Creating PostgreSQL flexible server $PostgresName in $PostgresLocation"
  & az postgres flexible-server create `
    --resource-group $ResourceGroup `
    --name $PostgresName `
    --location $PostgresLocation `
    --admin-user $PostgresAdminUser `
    --admin-password $PostgresAdminPassword `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 16 `
    --database-name hxrizxn `
    --public-access $PostgresPublicAccess `
    --yes | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az postgres flexible-server create failed for $PostgresName"
  }
} else {
  Write-Host "PostgreSQL flexible server $PostgresName already exists; resetting admin password for this deployment."
  & az postgres flexible-server update --resource-group $ResourceGroup --name $PostgresName --admin-password $PostgresAdminPassword | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az postgres flexible-server update failed for $PostgresName"
  }
}

$postgresFqdn = Invoke-AzText @("postgres", "flexible-server", "show", "--name", $PostgresName, "--resource-group", $ResourceGroup, "--query", "fullyQualifiedDomainName")
$encodedPassword = [uri]::EscapeDataString($PostgresAdminPassword)
$databaseUrl = "postgresql+psycopg://${PostgresAdminUser}:${encodedPassword}@${postgresFqdn}:5432/hxrizxn?sslmode=require"

Write-Host "Storing deployment secrets in Key Vault"
& az keyvault secret set --vault-name $keyVaultName --name database-url --value $databaseUrl | Out-Null
& az keyvault secret set --vault-name $keyVaultName --name storage-connection-string --value $storageConnectionString | Out-Null
& az keyvault secret set --vault-name $keyVaultName --name postgres-admin-password --value $PostgresAdminPassword | Out-Null

if (-not (Test-AzResource @("webapp", "show", "--name", $apiName, "--resource-group", $ResourceGroup))) {
  Write-Host "Creating API App Service $apiName"
  & az webapp create --resource-group $ResourceGroup --plan $planName --name $apiName --runtime "PYTHON:3.12" --https-only true | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az webapp create failed for $apiName"
  }
}

if (-not (Test-AzResource @("webapp", "show", "--name", $webName, "--resource-group", $ResourceGroup))) {
  Write-Host "Creating Web App Service $webName"
  & az webapp create --resource-group $ResourceGroup --plan $planName --name $webName --runtime "NODE:24-lts" --https-only true | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "az webapp create failed for $webName"
  }
}

Write-Host "Configuring API App Service"
& az webapp config set --resource-group $ResourceGroup --name $apiName --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" --always-on true --min-tls-version "1.2" --ftps-state Disabled | Out-Null
& az webapp config appsettings set --resource-group $ResourceGroup --name $apiName --settings `
  "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
  "ENABLE_ORYX_BUILD=true" `
  "APP_ENV=production" `
  "DEMO_MODE=$DemoMode" `
  "DATABASE_URL=$databaseUrl" `
  "API_CORS_ORIGINS=$webUrl,http://localhost:3000,http://127.0.0.1:3000" `
  "AZURE_STORAGE_CONNECTION_STRING=$storageConnectionString" `
  "AZURE_BLOB_CONTAINER=uploads" | Out-Null

Write-Host "Configuring Web App Service"
& az webapp config set --resource-group $ResourceGroup --name $webName --startup-file "npm run start" --always-on true --min-tls-version "1.2" --ftps-state Disabled | Out-Null
& az webapp config appsettings set --resource-group $ResourceGroup --name $webName --settings `
  "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
  "ENABLE_ORYX_BUILD=true" `
  "NPM_CONFIG_PRODUCTION=false" `
  "NODE_ENV=production" `
  "NEXT_PUBLIC_API_URL=$apiUrl" | Out-Null

$workspace = (Resolve-Path ".").Path
$outputDir = Join-Path $workspace "output\azure-appservice"
if (Test-Path $outputDir) {
  $resolvedOutput = (Resolve-Path $outputDir).Path
  if (-not $resolvedOutput.StartsWith($workspace)) {
    throw "Refusing to delete output path outside workspace: $resolvedOutput"
  }
  Remove-Item -LiteralPath $outputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $outputDir | Out-Null

$apiZip = Join-Path $outputDir "api.zip"
$webZip = Join-Path $outputDir "web.zip"
New-ZipPackage -SourceDir (Join-Path $workspace "apps\api") -StageDir (Join-Path $outputDir "api-stage") -ZipPath $apiZip
New-ZipPackage -SourceDir (Join-Path $workspace "apps\web") -StageDir (Join-Path $outputDir "web-stage") -ZipPath $webZip

Write-Host "Deploying API zip"
& az webapp deployment source config-zip --resource-group $ResourceGroup --name $apiName --src $apiZip --timeout 900 | Out-Null
if ($LASTEXITCODE -ne 0) {
  throw "API zip deployment failed"
}

Write-Host "Deploying web zip"
& az webapp deployment source config-zip --resource-group $ResourceGroup --name $webName --src $webZip --timeout 900 | Out-Null
if ($LASTEXITCODE -ne 0) {
  throw "Web zip deployment failed"
}

Write-Host "Restarting apps"
& az webapp restart --resource-group $ResourceGroup --name $apiName | Out-Null
& az webapp restart --resource-group $ResourceGroup --name $webName | Out-Null

Write-Host ""
Write-Host "Deployment complete."
Write-Host "API URL: $apiUrl"
Write-Host "Web URL: $webUrl"
Write-Host "Resource group: $ResourceGroup"
Write-Host "Location: $Location"
Write-Host "PostgreSQL: $PostgresName ($PostgresLocation)"
Write-Host "Storage: $storageName"
Write-Host "Key Vault: $keyVaultName"
Write-Host ""
Write-Host "Verify:"
Write-Host "  Invoke-RestMethod '$apiUrl/api/health'"
Write-Host "  Open '$webUrl'"
