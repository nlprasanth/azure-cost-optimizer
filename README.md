# Azure Cost Optimization Platform

A comprehensive cloud cost management solution that analyzes Azure resources to optimize expenses and improve efficiency.

## 🚀 Features

### 1. Cost Analysis
- Detailed cost breakdown by resource type and resource group
- Historical cost trends and patterns
- Budget compliance tracking
- Cost anomaly detection
- Multi-subscription cost analysis

### 2. Resource Optimization
- VM right-sizing recommendations
- Auto-scaling optimization
- Storage tier optimization
- Reserved Instance recommendations
- Spot Instance opportunities

### 3. Performance Monitoring
- Resource utilization tracking
- Performance metrics analysis
- Availability monitoring
- Capacity planning
- Anomaly detection

### 4. Interactive Dashboard
- Real-time cost insights
- Resource utilization graphs
- Optimization recommendations
- Custom reporting
- Multi-subscription view

## 📋 Prerequisites

### 1. Azure Account Requirements
- An Azure account with active subscriptions
- Permissions to create service principals
- Access to Azure Active Directory

### 2. Technical Requirements
- Python 3.8 or higher
- Git (for cloning the repository)
- pip (Python package manager)

## 🔑 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/nlprasanth/azure-cost-optimizer.git
cd azure-cost-optimizer
```

### 2. Create Azure Service Principal

1. **Log in to Azure Portal**
   - Go to [Azure Portal](https://portal.azure.com)
   - Sign in with your Azure account

2. **Get Tenant ID**
   - Navigate to "Azure Active Directory"
   - In Overview, copy the "Tenant ID"

3. **Create App Registration**
   - In Azure Active Directory:
     - Go to "App registrations"
     - Click "New registration"
     - Name: "AzureCostOptimizer"
     - Account type: "Accounts in this organizational directory only"
     - Click "Register"
   - Copy the "Application (client) ID"

4. **Create Client Secret**
   - In your new app registration:
     - Go to "Certificates & secrets"
     - Click "New client secret"
     - Add description and choose expiry
     - Click "Add"
     - IMMEDIATELY copy the secret value

5. **Assign Permissions**
   - Go to "Subscriptions"
   - Select your subscription(s)
   - Go to "Access control (IAM)"
   - Click "Add role assignment"
   - Assign these roles:
     - "Cost Management Reader"
     - "Reader"
   - Select your app registration as the assignee

### 3. Configure Environment

1. **Create Environment File**
   ```bash
   cp .env.template .env
   ```

2. **Edit .env File**
   ```plaintext
   AZURE_TENANT_ID=your_tenant_id
   AZURE_CLIENT_ID=your_client_id
   AZURE_CLIENT_SECRET=your_client_secret
   
   # Optional: Specify subscription ID
   # Leave empty to analyze all accessible subscriptions
   AZURE_SUBSCRIPTION_ID=optional_subscription_id
   ```

### 4. Set Up Python Environment

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

2. **Activate Virtual Environment**
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

1. **Start the Application**
   ```bash
   python main.py
   ```

2. **Access Features**
   - Cost Analysis: View detailed cost breakdowns and trends
   - Resource Optimization: Get recommendations for resource optimization
   - Performance Monitoring: Monitor resource utilization and performance
   - Dashboard: Access the web interface for visualization

## 📊 Available Analysis Types

### 1. Cost Analysis
- **Timeframes**: Last30Days, Last7Days, Custom
- **Grouping**: ResourceGroup, ResourceType, Location
- **Metrics**: ActualCost, AmortizedCost, Usage

### 2. Resource Optimization
- **VM Optimization**
  - Right-sizing recommendations
  - Schedule-based scaling
  - Spot instance opportunities
  
- **Storage Optimization**
  - Tier recommendations
  - Unused resource detection
  - Backup optimization

- **Network Optimization**
  - Traffic pattern analysis
  - Reserved bandwidth recommendations
  - Load balancer optimization

### 3. Performance Monitoring
- **Metrics Tracked**
  - CPU utilization
  - Memory usage
  - Network throughput
  - Storage IOPS
  - Response times

## 🔐 Security Best Practices

1. **Credential Management**
   - Store credentials only in .env file
   - Never commit .env file to source control
   - Rotate client secrets regularly
   - Use minimum required permissions

2. **Access Control**
   - Use dedicated service principals
   - Implement role-based access
   - Regular permission audits
   - Monitor service principal usage

## 🛠 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify credentials in .env file
   - Check service principal permissions
   - Ensure secret hasn't expired
   - Verify tenant ID is correct

2. **Access Issues**
   - Verify role assignments
   - Check subscription access
   - Validate resource permissions
   - Review Azure AD settings

3. **Performance Issues**
   - Check Python version
   - Verify system requirements
   - Monitor resource usage
   - Review log files

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, please:
1. Check the documentation
2. Review troubleshooting guide
3. Open an issue on GitHub
4. Contact the maintainers
