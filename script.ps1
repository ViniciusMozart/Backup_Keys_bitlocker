wget https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh; `
chmod +x dotnet-install.sh; `
./dotnet-install.sh -version 6.0.417; `
$ENV:PATH="$HOME/.dotnet:$ENV:PATH"; `
dotnet tool install --global dotnet-ef --version 6.0.1; `
git clone https://github.com/Azure/Commercial-Marketplace-SaaS-Accelerator.git -b 7.5.1 --depth 1; `
cd ./Commercial-Marketplace-SaaS-Accelerator/deployment; `
.\Deploy.ps1 `
 -WebAppNamePrefix "SAAC01" `
 -ResourceGroupForDeployment "SA04-RG-Accelerator" `
 -PublisherAdminUsers "mozart@bybbiskuahotmail.onmicrosoft.com,rafael.castro@bybbiskuahotmail.onmicrosoft.com" `
 -Location "East US" 


 ✅ If the intallation completed without error complete the folllowing checklist:
   🔵 Add The following URL in PartnerCenter SaaS Technical Configuration
      ➡️ Landing Page section:       https://SAAC01-portal.azurewebsites.net/
      ➡️ Connection Webhook section: https://SAAC01-portal.azurewebsites.net/api/AzureWebhook
      ➡️ Tenant ID:                  6e116e30-2dd0-4f4c-a74c-297eab38d504
      ➡️ AAD Application ID section: 0c997808-ab94-4092-b27d-3cde4d382a53
Deployment Complete in 14m:5s
DO NOT CLOSE THIS SCREEN.  Please make sure you copy or perform the actions above before closing.

