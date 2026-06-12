targetScope = 'resourceGroup'

@description('Location for Azure resources.')
param location string = resourceGroup().location

@description('Short environment name used as a resource prefix.')
param environmentName string = 'hxrizxn'

@description('Existing Azure Container Registry name. The deploy script creates this before Bicep runs.')
param acrName string

@description('Full backend image name, for example myacr.azurecr.io/hxrizxn-api:latest.')
param backendImage string

@description('Full frontend image name, for example myacr.azurecr.io/hxrizxn-web:latest.')
param frontendImage string

@secure()
param postgresAdminPassword string

param postgresAdminUser string = 'hxrizxnadmin'
param containerCpu string = '0.5'
param containerMemory string = '1Gi'
param webCpu string = '0.5'
param webMemory string = '1Gi'
param demoMode bool = false

@description('Optional real Foundry IQ endpoint. Leave blank for mock retrieval.')
param foundryIqEndpoint string = ''

@secure()
@description('Optional real Foundry IQ key. Leave blank for mock retrieval.')
param foundryIqApiKey string = ''

param foundryIqIndexName string = 'hxrizxn-demo'

@description('Optional Azure OpenAI endpoint. Leave blank for deterministic demo mode.')
param azureOpenAiEndpoint string = ''

@secure()
@description('Optional Azure OpenAI API key. Leave blank for deterministic demo mode.')
param azureOpenAiApiKey string = ''

param azureOpenAiDeployment string = ''
param azureOpenAiApiVersion string = '2025-04-01-preview'

var suffix = uniqueString(resourceGroup().id)
var storageName = toLower('hxr${suffix}')
var postgresName = '${environmentName}-pg-${suffix}'
var workspaceName = '${environmentName}-log-${suffix}'
var appInsightsName = '${environmentName}-appi-${suffix}'
var envName = '${environmentName}-cae-${suffix}'
var apiName = '${environmentName}-api'
var webName = '${environmentName}-web'
var kvName = '${environmentName}-kv-${suffix}'
var identityName = '${environmentName}-pull-${suffix}'
var databaseUrl = 'postgresql+psycopg://${postgresAdminUser}:${postgresAdminPassword}@${postgres.properties.fullyQualifiedDomainName}:5432/hxrizxn?sslmode=require'
var blobConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${storage.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
var acrPullRoleDefinitionId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
var resolvedFoundryIqApiKey = empty(foundryIqApiKey) ? 'not-configured' : foundryIqApiKey
var resolvedAzureOpenAiApiKey = empty(azureOpenAiApiKey) ? 'not-configured' : azureOpenAiApiKey

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, pullIdentity.id, 'AcrPull')
  scope: acr
  properties: {
    principalId: pullIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPullRoleDefinitionId
  }
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource uploads 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'uploads'
  properties: {
    publicAccess: 'None'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: kvName
  location: location
  properties: {
    tenantId: tenant().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enabledForDeployment: true
    enabledForTemplateDeployment: true
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: postgresName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: postgresAdminUser
    administratorLoginPassword: postgresAdminPassword
    network: {
      publicNetworkAccess: 'Enabled'
    }
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-12-01-preview' = {
  parent: postgres
  name: 'hxrizxn'
}

resource postgresAllowAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-12-01-preview' = {
  parent: postgres
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource containerEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: envName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
  }
}

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${pullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: pullIdentity.id
        }
      ]
      secrets: [
        {
          name: 'database-url'
          value: databaseUrl
        }
        {
          name: 'azure-storage-connection-string'
          value: blobConnectionString
        }
        {
          name: 'foundry-iq-api-key'
          value: resolvedFoundryIqApiKey
        }
        {
          name: 'azure-openai-api-key'
          value: resolvedAzureOpenAiApiKey
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: backendImage
          env: [
            {
              name: 'DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'DEMO_MODE'
              value: string(demoMode)
            }
            {
              name: 'AZURE_STORAGE_CONNECTION_STRING'
              secretRef: 'azure-storage-connection-string'
            }
            {
              name: 'AZURE_BLOB_CONTAINER'
              value: 'uploads'
            }
            {
              name: 'APPINSIGHTS_CONNECTION_STRING'
              value: appInsights.properties.ConnectionString
            }
            {
              name: 'FOUNDRY_IQ_ENDPOINT'
              value: foundryIqEndpoint
            }
            {
              name: 'FOUNDRY_IQ_API_KEY'
              secretRef: 'foundry-iq-api-key'
            }
            {
              name: 'FOUNDRY_IQ_INDEX_NAME'
              value: foundryIqIndexName
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: azureOpenAiEndpoint
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              secretRef: 'azure-openai-api-key'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: azureOpenAiDeployment
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: azureOpenAiApiVersion
            }
          ]
          resources: {
            cpu: json(containerCpu)
            memory: containerMemory
          }
        }
      ]
    }
  }
  dependsOn: [
    acrPullRole
    database
    uploads
  ]
}

resource web 'Microsoft.App/containerApps@2024-03-01' = {
  name: webName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${pullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 3000
        transport: 'auto'
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: pullIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'web'
          image: frontendImage
          env: [
            {
              name: 'NEXT_PUBLIC_API_URL'
              value: 'https://${api.properties.configuration.ingress.fqdn}'
            }
          ]
          resources: {
            cpu: json(webCpu)
            memory: webMemory
          }
        }
      ]
    }
  }
  dependsOn: [
    acrPullRole
  ]
}

output apiUrl string = 'https://${api.properties.configuration.ingress.fqdn}'
output webUrl string = 'https://${web.properties.configuration.ingress.fqdn}'
output acrLoginServer string = acr.properties.loginServer
output postgresServerName string = postgres.name
output storageAccountName string = storage.name
output keyVaultName string = keyVault.name
output appInsightsConnectionString string = appInsights.properties.ConnectionString
