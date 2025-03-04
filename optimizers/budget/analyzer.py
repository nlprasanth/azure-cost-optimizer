from azure.mgmt.consumption import ConsumptationManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class BudgetAnalyzer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.consumption_client = ConsumptationManagementClient(self.credential, subscription_id)
        self.cost_client = CostManagementClient(self.credential)

    def analyze_budget_performance(self, budget_name: str = None) -> Dict:
        """Analyze budget performance and spending patterns."""
        try:
            # Get budget details
            budgets = self._get_budgets()
            if not budgets:
                return None

            # Get current budget if name specified
            current_budget = next(
                (b for b in budgets if b['name'] == budget_name),
                budgets[0] if budgets else None
            ) if budget_name else budgets[0]

            if not current_budget:
                return None

            # Get spending data
            spending_data = self._get_spending_data(current_budget)
            
            # Analyze budget performance
            analysis = {
                'budget_details': current_budget,
                'spending_analysis': self._analyze_spending(spending_data, current_budget),
                'forecast_analysis': self._analyze_forecast(spending_data, current_budget),
                'alerts_analysis': self._analyze_alerts(current_budget),
                'optimization_opportunities': self._identify_optimization_opportunities(spending_data, current_budget)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing budget performance: {str(e)}")
            return None

    def _get_budgets(self) -> List[Dict]:
        """Get all budgets for the subscription."""
        try:
            scope = f'/subscriptions/{self.subscription_id}'
            budgets = self.cost_client.budgets.list(scope)
            
            processed_budgets = []
            for budget in budgets:
                processed_budgets.append({
                    'name': budget.name,
                    'amount': budget.amount,
                    'time_grain': budget.time_grain,
                    'start_date': budget.time_period.start_date,
                    'end_date': budget.time_period.end_date,
                    'filters': budget.filters,
                    'notifications': budget.notification
                })

            return processed_budgets

        except Exception as e:
            logger.error(f"Error getting budgets: {str(e)}")
            return []

    def _get_spending_data(self, budget: Dict) -> List[Dict]:
        """Get detailed spending data for budget analysis."""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)  # Last 90 days

            # Get consumption data
            usage = self.consumption_client.usage_details.list(
                scope=f'/subscriptions/{self.subscription_id}',
                expand='properties',
                filter=f"properties/usageStart ge '{start_date.strftime('%Y-%m-%d')}' and properties/usageEnd le '{end_date.strftime('%Y-%m-%d')}'"
            )

            spending_data = []
            for item in usage:
                if self._matches_budget_filters(item, budget):
                    spending_data.append({
                        'date': item.usage_start,
                        'cost': item.cost,
                        'resource_type': item.resource_type,
                        'resource_group': item.resource_group,
                        'tags': item.tags or {}
                    })

            return spending_data

        except Exception as e:
            logger.error(f"Error getting spending data: {str(e)}")
            return []

    def _matches_budget_filters(self, usage_item: Dict, budget: Dict) -> bool:
        """Check if usage item matches budget filters."""
        try:
            if not budget.get('filters'):
                return True

            filters = budget['filters']
            
            # Check resource group filter
            if filters.get('resource_groups'):
                if usage_item.resource_group not in filters['resource_groups']:
                    return False

            # Check resource type filter
            if filters.get('resource_types'):
                if usage_item.resource_type not in filters['resource_types']:
                    return False

            # Check tag filters
            if filters.get('tags'):
                for tag_key, tag_value in filters['tags'].items():
                    if not usage_item.tags:
                        return False
                    if tag_key not in usage_item.tags:
                        return False
                    if usage_item.tags[tag_key] != tag_value:
                        return False

            return True

        except Exception as e:
            logger.error(f"Error matching budget filters: {str(e)}")
            return True

    def _analyze_spending(self, spending_data: List[Dict], budget: Dict) -> Dict:
        """Analyze spending patterns and budget adherence."""
        try:
            df = pd.DataFrame(spending_data)
            if df.empty:
                return {}

            # Calculate key metrics
            total_spent = df['cost'].sum()
            daily_spending = df.groupby(df['date'].dt.date)['cost'].sum()
            
            # Calculate budget metrics
            budget_amount = budget['amount']
            time_grain = budget['time_grain']
            
            if time_grain == 'Monthly':
                periods_in_data = (df['date'].max() - df['date'].min()).days / 30
                normalized_budget = budget_amount * periods_in_data
            else:  # Assume annual
                periods_in_data = (df['date'].max() - df['date'].min()).days / 365
                normalized_budget = budget_amount * periods_in_data

            return {
                'total_spent': total_spent,
                'budget_amount': normalized_budget,
                'spending_metrics': {
                    'average_daily': daily_spending.mean(),
                    'max_daily': daily_spending.max(),
                    'std_dev_daily': daily_spending.std(),
                    'total_days': len(daily_spending)
                },
                'budget_metrics': {
                    'percentage_used': (total_spent / normalized_budget) * 100 if normalized_budget > 0 else 0,
                    'remaining_budget': normalized_budget - total_spent if normalized_budget > 0 else 0,
                    'daily_budget_target': normalized_budget / len(daily_spending) if len(daily_spending) > 0 else 0,
                    'days_until_depletion': self._calculate_days_until_depletion(
                        remaining_budget=normalized_budget - total_spent,
                        daily_average=daily_spending.mean()
                    )
                },
                'spending_patterns': self._analyze_spending_patterns(df)
            }

        except Exception as e:
            logger.error(f"Error analyzing spending: {str(e)}")
            return {}

    def _analyze_forecast(self, spending_data: List[Dict], budget: Dict) -> Dict:
        """Analyze spending forecast and budget projections."""
        try:
            df = pd.DataFrame(spending_data)
            if df.empty:
                return {}

            # Calculate daily spending trend
            daily_spending = df.groupby(df['date'].dt.date)['cost'].sum()
            trend = np.polyfit(range(len(daily_spending)), daily_spending.values, 1)
            
            # Project spending
            days_remaining = 30  # Project for next 30 days
            projected_spending = trend[0] * (len(daily_spending) + days_remaining) + trend[1]
            
            return {
                'trend_metrics': {
                    'daily_trend': trend[0],
                    'trend_direction': 'increasing' if trend[0] > 0 else 'decreasing',
                    'trend_strength': abs(trend[0]) / daily_spending.mean()
                },
                'projections': {
                    'next_30_days': projected_spending,
                    'expected_overage': projected_spending - budget['amount'] if projected_spending > budget['amount'] else 0,
                    'risk_level': self._calculate_risk_level(projected_spending, budget['amount'])
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing forecast: {str(e)}")
            return {}

    def _analyze_alerts(self, budget: Dict) -> Dict:
        """Analyze budget alerts and notifications."""
        try:
            notifications = budget.get('notifications', {})
            
            return {
                'alert_count': len(notifications),
                'alert_thresholds': [n.get('threshold') for n in notifications],
                'alert_types': [n.get('type') for n in notifications],
                'coverage_analysis': {
                    'has_warning_alerts': any(n.get('threshold', 0) <= 80 for n in notifications),
                    'has_critical_alerts': any(n.get('threshold', 0) >= 90 for n in notifications),
                    'lowest_threshold': min((n.get('threshold', 100) for n in notifications), default=100),
                    'alert_gaps': self._identify_alert_gaps(notifications)
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing alerts: {str(e)}")
            return {}

    def _identify_optimization_opportunities(self, spending_data: List[Dict], budget: Dict) -> List[Dict]:
        """Identify opportunities for budget optimization."""
        try:
            df = pd.DataFrame(spending_data)
            if df.empty:
                return []

            opportunities = []
            
            # Analyze resource type distribution
            resource_costs = df.groupby('resource_type')['cost'].sum()
            top_resources = resource_costs.nlargest(5)
            
            for resource_type, cost in top_resources.items():
                opportunities.append({
                    'type': 'resource_optimization',
                    'resource_type': resource_type,
                    'current_cost': cost,
                    'potential_savings': cost * 0.2,  # Assume 20% potential savings
                    'priority': 'high' if cost > budget['amount'] * 0.2 else 'medium'
                })

            # Analyze daily patterns
            daily_spending = df.groupby(df['date'].dt.date)['cost'].sum()
            if daily_spending.std() / daily_spending.mean() > 0.5:
                opportunities.append({
                    'type': 'spending_pattern',
                    'description': 'High daily spending variation detected',
                    'potential_savings': daily_spending.std() * 0.5,
                    'priority': 'medium'
                })

            # Analyze resource groups
            rg_costs = df.groupby('resource_group')['cost'].sum()
            top_rgs = rg_costs.nlargest(3)
            
            for rg, cost in top_rgs.items():
                opportunities.append({
                    'type': 'resource_group_optimization',
                    'resource_group': rg,
                    'current_cost': cost,
                    'potential_savings': cost * 0.15,  # Assume 15% potential savings
                    'priority': 'high' if cost > budget['amount'] * 0.3 else 'medium'
                })

            return opportunities

        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {str(e)}")
            return []

    def _calculate_days_until_depletion(self, remaining_budget: float, daily_average: float) -> int:
        """Calculate days until budget depletion."""
        try:
            if daily_average <= 0:
                return float('inf')
            return int(remaining_budget / daily_average)

        except Exception as e:
            logger.error(f"Error calculating days until depletion: {str(e)}")
            return 0

    def _analyze_spending_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze detailed spending patterns."""
        try:
            # Daily patterns
            daily_spending = df.groupby(df['date'].dt.date)['cost'].sum()
            
            # Weekly patterns
            weekly_spending = df.groupby(df['date'].dt.isocalendar().week)['cost'].sum()
            
            # Resource type patterns
            resource_spending = df.groupby('resource_type')['cost'].sum()
            
            return {
                'daily_pattern': {
                    'average': daily_spending.mean(),
                    'std_dev': daily_spending.std(),
                    'coefficient_of_variation': daily_spending.std() / daily_spending.mean() if daily_spending.mean() > 0 else 0
                },
                'weekly_pattern': {
                    'average': weekly_spending.mean(),
                    'std_dev': weekly_spending.std(),
                    'coefficient_of_variation': weekly_spending.std() / weekly_spending.mean() if weekly_spending.mean() > 0 else 0
                },
                'resource_distribution': {
                    'top_resources': resource_spending.nlargest(5).to_dict(),
                    'resource_count': len(resource_spending)
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {str(e)}")
            return {}

    def _calculate_risk_level(self, projected_spending: float, budget_amount: float) -> str:
        """Calculate budget risk level."""
        try:
            if projected_spending <= budget_amount:
                return 'low'
            
            overage_percentage = ((projected_spending - budget_amount) / budget_amount) * 100
            
            if overage_percentage > 20:
                return 'high'
            elif overage_percentage > 10:
                return 'medium'
            else:
                return 'low'

        except Exception as e:
            logger.error(f"Error calculating risk level: {str(e)}")
            return 'unknown'

    def _identify_alert_gaps(self, notifications: List[Dict]) -> List[Dict]:
        """Identify gaps in alert coverage."""
        try:
            gaps = []
            thresholds = sorted([n.get('threshold', 0) for n in notifications])
            
            # Check for early warning gap
            if not thresholds or thresholds[0] > 50:
                gaps.append({
                    'type': 'early_warning',
                    'description': 'No alerts below 50% of budget',
                    'recommendation': 'Add alert at 40% or 50% for early warning'
                })

            # Check for critical warning gap
            if not thresholds or thresholds[-1] < 90:
                gaps.append({
                    'type': 'critical_warning',
                    'description': 'No alerts above 90% of budget',
                    'recommendation': 'Add alert at 90% or 95% for critical warning'
                })

            # Check for large gaps between thresholds
            for i in range(len(thresholds) - 1):
                if thresholds[i + 1] - thresholds[i] > 30:
                    gaps.append({
                        'type': 'threshold_gap',
                        'description': f'Large gap between {thresholds[i]}% and {thresholds[i + 1]}%',
                        'recommendation': f'Add intermediate alert at {(thresholds[i] + thresholds[i + 1]) // 2}%'
                    })

            return gaps

        except Exception as e:
            logger.error(f"Error identifying alert gaps: {str(e)}")
            return []
