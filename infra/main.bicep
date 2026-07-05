// AI Academy API on Azure Container Apps — test-tenant deployment (e.g. the Deloitte tenant).
//
// Choices:
// - Container Apps over App Service: scale-to-zero fits an intermittently used teaching API.
// - A user-assigned managed identity pulls from ACR (no admin creds, no anonymous pull).
// - The API key is a Container Apps secret, never a plain env value.
// - Ingress targetPort 8000 matches the uvicorn port in the Dockerfile.
//
// Deploy via infra/deploy.ps1 (validates with what-if first).

@description('Base name for all resources (letters/digits, short).')
param prefix string = 'academy'

@description('Azure region.')
param location string = resourceGroup().location

@description('Container image to run. First deploy uses the placeholder; deploy.ps1 swaps in the built image.')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Shared key required in the X-Api-Key header. Empty disables auth (mock/demo only).')
@secure()
param apiKey string = ''

var acrName = toLower(replace('${prefix}acr${uniqueString(resourceGroup().id)}', '-', ''))

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: { name: 'Basic' } // Basic SKU: anonymous pull unavailable; pulls go through AcrPull RBAC only
  properties: {
    adminUserEnabled: false
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${prefix}-api-identity'
  location: location
}

// AcrPull for the app identity — least privilege, no registry credentials anywhere.
resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, identity.id, 'acrpull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${prefix}-api'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identity.id}': {} }
  }
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000 // must match the uvicorn port in the Dockerfile
        transport: 'auto'
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: identity.id
        }
      ]
      secrets: empty(apiKey) ? [] : [
        { name: 'academy-api-key', value: apiKey }
      ]
    }
    template: {
      containers: [
        {
          name: 'academy-api'
          image: containerImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: concat(
            [
              { name: 'ACADEMY_RUNTIME', value: 'mock' } // flip to live/maf once AOAI is configured
            ],
            empty(apiKey) ? [] : [
              { name: 'ACADEMY_API_KEY', secretRef: 'academy-api-key' }
            ]
          )
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 2 } // scale-to-zero: teaching API, intermittent use
    }
  }
  dependsOn: [acrPull]
}

output apiFqdn string = app.properties.configuration.ingress.fqdn
output apiBaseUrl string = 'https://${app.properties.configuration.ingress.fqdn}'
output acrLoginServer string = acr.properties.loginServer
output acrName string = acr.name
