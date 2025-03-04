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

### 5. Advanced Usage Examples

#### Resource Tag-Based Analysis
```python
from optimizers.tagging.analyzer import TaggingAnalyzer

# Initialize analyzer
analyzer = TaggingAnalyzer()

# Analyze costs by environment tag
env_costs = analyzer.analyze_costs_by_tag(
    tag_name="Environment",
    timeframe="Last3Months",
    group_by=["ResourceType"]
)

# Find untagged resources
untagged = analyzer.find_untagged_resources(
    required_tags=["Environment", "Department", "Owner"]
)

# Get tag compliance report
compliance = analyzer.get_tag_compliance_report(
    tag_policies={
        "Environment": ["prod", "dev", "test", "staging"],
        "Department": ["it", "finance", "marketing"],
        "CostCenter": r"^\d{4}$"  # regex pattern
    }
)
```

#### Advanced Cost Forecasting
```python
from optimizers.forecasting.forecaster import CostForecaster

# Initialize forecaster
forecaster = CostForecaster()

# Generate cost forecast with ML model
forecast = forecaster.predict_costs(
    forecast_months=6,
    confidence_interval=0.95,
    include_seasonality=True,
    factors=[
        "historical_trend",
        "resource_growth",
        "planned_changes"
    ]
)

# Get cost anomaly detection
anomalies = forecaster.detect_anomalies(
    sensitivity="medium",
    lookback_period="90d",
    detection_methods=["statistical", "ml_based"]
)
```

#### Reserved Instance Optimization
```python
from optimizers.reserved_instance.optimizer import RIOptimizer

# Initialize optimizer
optimizer = RIOptimizer()

# Get RI recommendations
ri_recommendations = optimizer.get_ri_recommendations(
    commitment_term="1_year",
    payment_option="no_upfront",
    threshold_hours=700,
    min_savings_percentage=30
)

# Analyze existing RIs
ri_analysis = optimizer.analyze_ri_utilization(
    include_expired=False,
    lookback_period="90d"
)

# Get RI purchase plan
purchase_plan = optimizer.generate_purchase_plan(
    budget=100000,
    max_commitment_term="3_years",
    target_coverage=80,
    risk_tolerance="medium"
)
```

#### Network Cost Optimization
```python
from optimizers.network.optimizer import NetworkOptimizer

# Initialize optimizer
optimizer = NetworkOptimizer()

# Analyze bandwidth costs
bandwidth_analysis = optimizer.analyze_bandwidth_costs(
    regions=["eastus", "westus"],
    timeframe="Last3Months",
    group_by=["Direction", "ServiceType"]
)

# Get bandwidth optimization recommendations
recommendations = optimizer.get_bandwidth_recommendations(
    min_savings=1000,
    include_reserved_bandwidth=True,
    consider_cdn=True
)

# Analyze ExpressRoute circuits
expressroute_analysis = optimizer.analyze_expressroute_usage(
    circuits=["circuit1", "circuit2"],
    include_redundant_circuits=True,
    lookback_period="90d"
)
```

## 📝 Configuration Examples

The platform uses YAML configuration files for various components. Here are some examples:

### 1. Cost Alerts Configuration
```yaml
# config/cost_alerts.yaml
alerts:
  budget:
    monthly:
      amount: 10000
      currency: USD
      thresholds: [50, 75, 90, 100]
  anomaly:
    sensitivity: "medium"
    baseline_period: 30  # days

notifications:
  email:
    recipients: ["finance@company.com"]
  teams:
    webhook_url: "https://teams.webhook.url"
```

### 2. Resource Optimization Configuration
```yaml
# config/resource_optimization.yaml
vm_optimization:
  rightsizing:
    cpu:
      underutilized:
        threshold: 20  # percentage
        duration: 14  # days
    memory:
      underutilized:
        threshold: 30
        duration: 14

storage_optimization:
  unused_resources:
    disks:
      unused_threshold_days: 30
```

### 3. Monitoring Configuration
```yaml
# config/monitoring.yaml
metrics:
  collection:
    interval: "5m"
    retention_days: 90
  
  performance:
    cpu:
      warning_threshold: 80
      critical_threshold: 90
```

## 🔄 Common Workflows

### 1. Monthly Cost Review
```python
from optimizers.cost.analyzer import CostAnalyzer
from optimizers.reporting.generator import ReportGenerator

def monthly_cost_review():
    # Get cost analysis
    analyzer = CostAnalyzer()
    costs = analyzer.get_cost_trends(timeframe="LastMonth")
    
    # Generate report
    generator = ReportGenerator()
    report = generator.create_monthly_report(
        cost_data=costs,
        include_sections=[
            "executive_summary",
            "cost_breakdown",
            "savings_opportunities",
            "recommendations"
        ],
        format="pdf"
    )
    
    # Send report
    generator.distribute_report(
        report_path=report.path,
        recipients=["stakeholders@company.com"],
        include_dashboard_link=True
    )
```

### 2. Weekly Resource Optimization
```python
from optimizers.vm.optimizer import VMOptimizer
from optimizers.storage.optimizer import StorageOptimizer
from optimizers.reporting.generator import ReportGenerator

def weekly_optimization():
    # VM optimization
    vm_opt = VMOptimizer()
    vm_recommendations = vm_opt.get_rightsizing_recommendations()
    
    # Storage optimization
    storage_opt = StorageOptimizer()
    storage_recommendations = storage_opt.get_tier_recommendations()
    
    # Generate and send report
    generator = ReportGenerator()
    report = generator.create_optimization_report(
        vm_recommendations=vm_recommendations,
        storage_recommendations=storage_recommendations,
        format="excel",
        include_savings_summary=True
    )
    
    # Implement high-confidence recommendations
    vm_opt.apply_recommendations(
        recommendations=vm_recommendations,
        confidence_threshold=0.9,
        require_approval=True
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
