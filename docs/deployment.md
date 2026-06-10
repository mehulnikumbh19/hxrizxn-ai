# Deployment

## Local

```bash
python -m pip install -e apps/api[dev]
npm install
docker compose up --build
```

## Azure Recommended Path

Because this workstation does not currently have Docker installed, the recommended path uses Azure Container Registry cloud builds and deploys both API and web to Azure Container Apps.

```powershell
az login
.\scripts\deploy_azure_recommended.ps1 `
  -SubscriptionId "<subscription-id>" `
  -Location "eastus" `
  -ResourceGroup "rg-hxrizxn-demo"
```

The script:

1. Confirms Azure login and subscription.
2. Registers required resource providers.
3. Creates the resource group.
4. Creates or reuses ACR.
5. Builds `hxrizxn-api:latest` and `hxrizxn-web:latest` in ACR.
6. Deploys `infra/bicep/main.bicep`.
7. Prints API and web URLs.

Optional real integration parameters:

```powershell
.\scripts\deploy_azure_recommended.ps1 `
  -SubscriptionId "<subscription-id>" `
  -FoundryIqEndpoint "<endpoint>" `
  -FoundryIqApiKey "<key>" `
  -AzureOpenAiEndpoint "<endpoint>" `
  -AzureOpenAiApiKey "<key>" `
  -AzureOpenAiDeployment "<deployment-name>" `
  -DemoMode $false
```

Do not paste real keys into chat or commit them. Prefer shell environment variables or a local secure prompt when running the script.

GitHub Actions includes `ci.yml`, `docker.yml`, and `deploy-azure.yml`, but the local script is the fastest first deployment route.
