# Azure Cost Optimization Analyzer

An intelligent application that analyzes Azure tenant information to optimize costs and improve resource efficiency.

## Features

### 1. Resource Analysis
- VM utilization tracking
- Storage optimization
- Network traffic patterns
- Reserved Instance analysis
- Spot instance opportunities

### 2. Cost Analysis
- Historical cost trends
- Cost forecasting
- Budget tracking
- Anomaly detection

### 3. Optimization Recommendations
- Resource right-sizing
- Auto-scaling configurations
- Storage tier optimization
- Network optimization
- Service-specific recommendations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Azure credentials:
- Create a `.env` file with your Azure credentials
- Grant necessary permissions to the service principal

3. Run the application:
```bash
python main.py
```

## Components

- `data_collectors/`: Azure resource and cost data collection
- `analyzers/`: Analysis modules for different resource types
- `optimizers/`: Cost optimization recommendation engines
- `dashboard/`: Web interface for viewing analysis and recommendations
- `utils/`: Helper functions and common utilities

## Requirements

- Python 3.9+
- Azure subscription
- Service Principal with necessary permissions
- Cost Management API access
