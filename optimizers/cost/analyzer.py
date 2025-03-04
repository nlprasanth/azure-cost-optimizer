from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class CostAnalyzer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.consumption_client = ConsumptionManagementClient(self.credential, subscription_id)
        self.cost_client = CostManagementClient(self.credential)

    def analyze_costs(self, time_range_days: int = 30) -> Dict:
        """Perform comprehensive cost analysis."""
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=time_range_days)

            analysis = {
                'cost_summary': self._analyze_cost_summary(start_time, end_time),
                'resource_costs': self._analyze_resource_costs(start_time, end_time),
                'service_costs': self._analyze_service_costs(start_time, end_time),
                'cost_trends': self._analyze_cost_trends(start_time, end_time),
                'cost_anomalies': self._detect_cost_anomalies(start_time, end_time),
                'budget_analysis': self._analyze_budget_compliance(),
                'cost_drivers': self._identify_cost_drivers(start_time, end_time),
                'optimization_opportunities': self._identify_optimization_opportunities()
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing costs: {str(e)}")
            return {}

    def _analyze_cost_summary(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze overall cost summary."""
        try:
            # Get cost data
            scope = f"/subscriptions/{self.subscription_id}"
            cost_data = self._get_cost_data(scope, start_time, end_time)

            # Calculate summary metrics
            total_cost = sum(item.get('cost', 0) for item in cost_data)
            daily_average = total_cost / (end_time - start_time).days
            
            # Calculate cost trends
            cost_trend = self._calculate_cost_trend(cost_data)
            
            return {
                'total_cost': total_cost,
                'daily_average': daily_average,
                'cost_trend': cost_trend,
                'currency': cost_data[0].get('currency', 'USD') if cost_data else 'USD',
                'time_period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing cost summary: {str(e)}")
            return {}

    def _analyze_resource_costs(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze costs by resource."""
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            # Get resource usage and costs
            resource_costs = self._get_resource_costs(scope, start_time, end_time)
            
            # Analyze each resource type
            analysis = {
                'compute': self._analyze_compute_costs(resource_costs),
                'storage': self._analyze_storage_costs(resource_costs),
                'networking': self._analyze_networking_costs(resource_costs),
                'databases': self._analyze_database_costs(resource_costs),
                'other': self._analyze_other_costs(resource_costs)
            }
            
            # Calculate cost distribution
            total_cost = sum(costs['total_cost'] for costs in analysis.values())
            for category in analysis:
                if total_cost > 0:
                    analysis[category]['percentage'] = (
                        analysis[category]['total_cost'] / total_cost * 100
                    )
                else:
                    analysis[category]['percentage'] = 0

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resource costs: {str(e)}")
            return {}

    def _analyze_service_costs(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze costs by Azure service."""
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            # Get service usage and costs
            service_costs = self._get_service_costs(scope, start_time, end_time)
            
            # Group and analyze by service
            analysis = {}
            for service, costs in service_costs.items():
                analysis[service] = {
                    'total_cost': sum(cost['cost'] for cost in costs),
                    'usage_metrics': self._analyze_service_usage(costs),
                    'cost_trend': self._calculate_service_cost_trend(costs)
                }
            
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing service costs: {str(e)}")
            return {}

    def _analyze_cost_trends(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze cost trends and patterns."""
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            # Get historical cost data
            cost_data = self._get_cost_data(scope, start_time, end_time)
            
            # Analyze daily trends
            daily_trends = self._analyze_daily_cost_trends(cost_data)
            
            # Analyze weekly patterns
            weekly_patterns = self._analyze_weekly_cost_patterns(cost_data)
            
            # Analyze monthly patterns
            monthly_patterns = self._analyze_monthly_cost_patterns(cost_data)
            
            # Predict future costs
            cost_forecast = self._forecast_costs(cost_data)
            
            return {
                'daily_trends': daily_trends,
                'weekly_patterns': weekly_patterns,
                'monthly_patterns': monthly_patterns,
                'cost_forecast': cost_forecast
            }

        except Exception as e:
            logger.error(f"Error analyzing cost trends: {str(e)}")
            return {}

    def _detect_cost_anomalies(self, start_time: datetime, end_time: datetime) -> Dict:
        """Detect cost anomalies and unusual patterns."""
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            # Get cost data
            cost_data = self._get_cost_data(scope, start_time, end_time)
            
            # Detect daily cost anomalies
            daily_anomalies = self._detect_daily_cost_anomalies(cost_data)
            
            # Detect service-specific anomalies
            service_anomalies = self._detect_service_cost_anomalies(cost_data)
            
            # Detect resource-specific anomalies
            resource_anomalies = self._detect_resource_cost_anomalies(cost_data)
            
            return {
                'daily_anomalies': daily_anomalies,
                'service_anomalies': service_anomalies,
                'resource_anomalies': resource_anomalies
            }

        except Exception as e:
            logger.error(f"Error detecting cost anomalies: {str(e)}")
            return {}

    def _analyze_budget_compliance(self) -> Dict:
        """Analyze budget compliance and forecasts."""
        try:
            # Get budget information
            budgets = list(self.consumption_client.budgets.list())
            
            analysis = {
                'budgets': [],
                'forecasts': [],
                'violations': []
            }
            
            for budget in budgets:
                # Analyze budget status
                status = self._analyze_budget_status(budget)
                analysis['budgets'].append(status)
                
                # Generate forecast
                forecast = self._generate_budget_forecast(budget)
                analysis['forecasts'].append(forecast)
                
                # Check for violations
                violations = self._check_budget_violations(budget)
                if violations:
                    analysis['violations'].extend(violations)
            
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing budget compliance: {str(e)}")
            return {}

    def _identify_cost_drivers(self, start_time: datetime, end_time: datetime) -> Dict:
        """Identify main cost drivers and their impact."""
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            # Get detailed cost data
            cost_data = self._get_cost_data(scope, start_time, end_time)
            
            # Analyze by service
            service_drivers = self._analyze_service_cost_drivers(cost_data)
            
            # Analyze by resource
            resource_drivers = self._analyze_resource_cost_drivers(cost_data)
            
            # Analyze by location
            location_drivers = self._analyze_location_cost_drivers(cost_data)
            
            return {
                'service_drivers': service_drivers,
                'resource_drivers': resource_drivers,
                'location_drivers': location_drivers
            }

        except Exception as e:
            logger.error(f"Error identifying cost drivers: {str(e)}")
            return {}

    def _identify_optimization_opportunities(self) -> Dict:
        """Identify cost optimization opportunities."""
        try:
            opportunities = {
                'immediate': [],
                'short_term': [],
                'long_term': []
            }
            
            # Analyze resource sizing opportunities
            sizing_opportunities = self._analyze_sizing_opportunities()
            self._categorize_opportunities(sizing_opportunities, opportunities)
            
            # Analyze reservation opportunities
            reservation_opportunities = self._analyze_reservation_opportunities()
            self._categorize_opportunities(reservation_opportunities, opportunities)
            
            # Analyze usage pattern opportunities
            usage_opportunities = self._analyze_usage_pattern_opportunities()
            self._categorize_opportunities(usage_opportunities, opportunities)
            
            return opportunities

        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {str(e)}")
            return {}

    def _get_cost_data(self, scope: str, start_time: datetime, 
                      end_time: datetime) -> List[Dict]:
        """Get cost data from Azure Cost Management."""
        try:
            # Define time period
            time_period = {
                'from': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'to': end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            # Define query
            query = {
                'type': 'ActualCost',
                'timeframe': 'Custom',
                'timePeriod': time_period,
                'dataset': {
                    'granularity': 'Daily',
                    'aggregation': {
                        'totalCost': {
                            'name': 'Cost',
                            'function': 'Sum'
                        }
                    },
                    'grouping': [
                        {
                            'type': 'Dimension',
                            'name': 'ResourceId'
                        },
                        {
                            'type': 'Dimension',
                            'name': 'ResourceType'
                        }
                    ]
                }
            }

            # Get cost data
            response = self.cost_client.query.usage(scope, query)
            
            return self._process_cost_data(response)

        except Exception as e:
            logger.error(f"Error getting cost data: {str(e)}")
            return []

    def _process_cost_data(self, response: Dict) -> List[Dict]:
        """Process and format cost data."""
        try:
            processed_data = []
            
            for row in response.rows:
                processed_data.append({
                    'date': row[0],
                    'resource_id': row[1],
                    'resource_type': row[2],
                    'cost': float(row[3]),
                    'currency': row[4] if len(row) > 4 else 'USD'
                })
            
            return processed_data

        except Exception as e:
            logger.error(f"Error processing cost data: {str(e)}")
            return []
