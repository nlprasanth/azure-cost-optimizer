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

## 🔧 Quick Setup

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## 🔑 Detailed Setup Instructions

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

## 💡 Usage Examples

### 1. Cost Analysis Examples

#### View Monthly Cost Trends
```python
from optimizers.cost.analyzer import CostAnalyzer

# Initialize analyzer
analyzer = CostAnalyzer()

# Get monthly costs for last 6 months
costs = analyzer.get_cost_trends(
    timeframe="Last6Months",
    granularity="Monthly",
    group_by=["ResourceType"]
)

# View top spending categories
top_costs = analyzer.get_top_spending_resources(limit=5)
```

#### Budget Analysis
```python
from optimizers.budget.analyzer import BudgetAnalyzer

# Initialize analyzer
analyzer = BudgetAnalyzer()

# Check budget compliance
compliance = analyzer.check_budget_compliance(
    budget_amount=5000,
    timeframe="CurrentMonth"
)

# Get forecasted overages
forecast = analyzer.forecast_budget_overages(
    months_ahead=3
)
```

### 2. Resource Optimization Examples

#### VM Optimization
```python
from optimizers.vm.optimizer import VMOptimizer

# Initialize optimizer
optimizer = VMOptimizer()

# Get right-sizing recommendations
recommendations = optimizer.get_rightsizing_recommendations(
    min_cpu_threshold=20,
    min_memory_threshold=30,
    lookback_days=30
)

# Find spot instance opportunities
spot_opportunities = optimizer.find_spot_opportunities(
    max_interruption_rate=10,
    min_savings_percentage=50
)
```

#### Storage Optimization
```python
from optimizers.storage.optimizer import StorageOptimizer

# Initialize optimizer
optimizer = StorageOptimizer()

# Find unused disks
unused_disks = optimizer.find_unused_disks(
    unused_days=30
)

# Get tier optimization recommendations
tier_recommendations = optimizer.get_tier_recommendations(
    min_savings=100  # in dollars
)
```

### 3. Performance Monitoring Examples

#### Resource Health Monitoring
```python
from optimizers.monitoring.analyzer import MonitoringAnalyzer

# Initialize analyzer
analyzer = MonitoringAnalyzer()

# Get resource health status
health_status = analyzer.get_resource_health(
    resource_types=["Microsoft.Compute/virtualMachines"],
    timeframe="Last24Hours"
)

# Get performance metrics
metrics = analyzer.get_performance_metrics(
    metric_names=["CPU", "Memory", "Network"],
    aggregation="Average",
    interval="5m"
)
```

### 4. Dashboard Examples

#### Custom Reporting
```python
from dashboard.api import DashboardAPI

# Initialize dashboard
api = DashboardAPI()

# Create custom cost report
report = api.create_cost_report(
    timeframe="LastMonth",
    group_by=["ResourceGroup", "Tags"],
    metrics=["ActualCost", "AmortizedCost"]
)

# Export report
api.export_report(
    report_id=report.id,
    format="excel",
    destination="path/to/report.xlsx"
)
```

## 🔄 Automation Examples

### 1. Scheduled Cost Reports
```python
from optimizers.cost.manager import CostManager

# Initialize manager
manager = CostManager()

# Schedule daily cost report
manager.schedule_cost_report(
    schedule="0 8 * * *",  # 8 AM daily
    recipients=["team@company.com"],
    report_type="DailyCostSummary"
)
```

### 2. Automated Optimization
```python
from optimizers.scaling.manager import ScalingManager

# Initialize manager
manager = ScalingManager()

# Set up auto-scaling rules
manager.configure_auto_scaling(
    resource_group="production-rg",
    vm_scale_set="web-vmss",
    rules=[
        {
            "metric": "CPU",
            "threshold": 75,
            "action": "ScaleOut",
            "increment": 2
        },
        {
            "metric": "CPU",
            "threshold": 25,
            "action": "ScaleIn",
            "decrement": 1
        }
    ]
)
```

### 3. Alert Configuration
```python
from optimizers.monitoring.manager import MonitoringManager

# Initialize manager
manager = MonitoringManager()

# Configure cost alerts
manager.set_cost_alerts(
    budget_amount=10000,
    alert_thresholds=[50, 75, 90, 100],
    notification_emails=["finance@company.com"]
)

# Configure performance alerts
manager.set_performance_alerts(
    rules=[
        {
            "metric": "CPU",
            "threshold": 90,
            "duration": "5m",
            "severity": "High"
        },
        {
            "metric": "Memory",
            "threshold": 85,
            "duration": "10m",
            "severity": "Medium"
        }
    ]
)
```

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
