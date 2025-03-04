from azure.mgmt.consumption import ConsumptionManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class CostForecastAnalyzer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.consumption_client = ConsumptionManagementClient(self.credential, subscription_id)

        # Default forecast settings
        self.forecast_periods = 12  # months
        self.confidence_levels = [0.95, 0.80, 0.50]  # confidence intervals
        self.min_historical_months = 6

    def analyze_historical_costs(self, months: int = 12) -> Dict:
        """Analyze historical cost patterns."""
        try:
            # Get historical cost data
            historical_data = self._get_historical_costs(months)
            if not historical_data:
                return None

            # Convert to pandas DataFrame
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            # Calculate key metrics
            analysis = {
                'total_cost': df['cost'].sum(),
                'average_monthly_cost': df['cost'].mean(),
                'cost_std_dev': df['cost'].std(),
                'min_monthly_cost': df['cost'].min(),
                'max_monthly_cost': df['cost'].max(),
                'month_over_month_growth': self._calculate_mom_growth(df),
                'seasonality': self._analyze_seasonality(df),
                'cost_drivers': self._analyze_cost_drivers(df),
                'trends': self._analyze_trends(df)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing historical costs: {str(e)}")
            return None

    def _get_historical_costs(self, months: int) -> List[Dict]:
        """Get historical cost data from Azure."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=months * 30)

            # Get consumption data
            usage = self.consumption_client.usage_details.list(
                scope=f'/subscriptions/{self.subscription_id}',
                expand='properties',
                filter=f"properties/usageStart ge '{start_time.strftime('%Y-%m-%d')}' and properties/usageEnd le '{end_time.strftime('%Y-%m-%d')}'"
            )

            # Process usage data
            cost_data = []
            for item in usage:
                cost_data.append({
                    'date': item.usage_start.strftime('%Y-%m-%d'),
                    'cost': item.cost,
                    'resource_type': item.resource_type,
                    'resource_group': item.resource_group,
                    'tags': item.tags or {}
                })

            return cost_data

        except Exception as e:
            logger.error(f"Error getting historical costs: {str(e)}")
            return []

    def _calculate_mom_growth(self, df: pd.DataFrame) -> Dict:
        """Calculate month-over-month growth rates."""
        try:
            # Resample to monthly and calculate growth rates
            monthly = df.resample('M')['cost'].sum()
            growth_rates = monthly.pct_change()

            return {
                'average_growth': growth_rates.mean(),
                'growth_std_dev': growth_rates.std(),
                'last_month_growth': growth_rates.iloc[-1] if len(growth_rates) > 0 else 0,
                'growth_trend': 'increasing' if growth_rates.mean() > 0 else 'decreasing'
            }

        except Exception as e:
            logger.error(f"Error calculating MoM growth: {str(e)}")
            return {
                'average_growth': 0,
                'growth_std_dev': 0,
                'last_month_growth': 0,
                'growth_trend': 'stable'
            }

    def _analyze_seasonality(self, df: pd.DataFrame) -> Dict:
        """Analyze seasonal patterns in cost data."""
        try:
            # Resample to monthly
            monthly = df.resample('M')['cost'].sum()
            
            # Calculate seasonal patterns
            seasonal_patterns = {
                'monthly': self._calculate_monthly_seasonality(monthly),
                'quarterly': self._calculate_quarterly_seasonality(monthly),
                'weekday': self._calculate_weekday_seasonality(df)
            }

            return seasonal_patterns

        except Exception as e:
            logger.error(f"Error analyzing seasonality: {str(e)}")
            return {
                'monthly': {},
                'quarterly': {},
                'weekday': {}
            }

    def _calculate_monthly_seasonality(self, monthly_data: pd.Series) -> Dict:
        """Calculate monthly seasonal patterns."""
        try:
            monthly_patterns = monthly_data.groupby(monthly_data.index.month).mean()
            highest_month = monthly_patterns.idxmax()
            lowest_month = monthly_patterns.idxmin()

            return {
                'highest_cost_month': highest_month,
                'lowest_cost_month': lowest_month,
                'seasonal_variation': monthly_patterns.std() / monthly_patterns.mean()
            }

        except Exception as e:
            logger.error(f"Error calculating monthly seasonality: {str(e)}")
            return {}

    def _calculate_quarterly_seasonality(self, monthly_data: pd.Series) -> Dict:
        """Calculate quarterly seasonal patterns."""
        try:
            quarterly = monthly_data.resample('Q').sum()
            quarterly_patterns = quarterly.groupby(quarterly.index.quarter).mean()
            
            return {
                'highest_cost_quarter': quarterly_patterns.idxmax(),
                'lowest_cost_quarter': quarterly_patterns.idxmin(),
                'quarter_variation': quarterly_patterns.std() / quarterly_patterns.mean()
            }

        except Exception as e:
            logger.error(f"Error calculating quarterly seasonality: {str(e)}")
            return {}

    def _calculate_weekday_seasonality(self, df: pd.DataFrame) -> Dict:
        """Calculate weekday vs weekend patterns."""
        try:
            weekday_costs = df.groupby(df.index.dayofweek)['cost'].mean()
            
            return {
                'weekday_avg': weekday_costs[0:5].mean(),
                'weekend_avg': weekday_costs[5:7].mean(),
                'day_variation': weekday_costs.std() / weekday_costs.mean()
            }

        except Exception as e:
            logger.error(f"Error calculating weekday seasonality: {str(e)}")
            return {}

    def _analyze_cost_drivers(self, df: pd.DataFrame) -> Dict:
        """Analyze main cost drivers."""
        try:
            # Group by resource type
            resource_costs = df.groupby('resource_type')['cost'].sum()
            
            # Calculate percentage of total cost
            total_cost = resource_costs.sum()
            resource_percentages = (resource_costs / total_cost * 100).round(2)
            
            # Get top cost drivers
            top_drivers = resource_percentages.nlargest(5)
            
            return {
                'top_resources': top_drivers.to_dict(),
                'cost_concentration': self._calculate_cost_concentration(resource_percentages)
            }

        except Exception as e:
            logger.error(f"Error analyzing cost drivers: {str(e)}")
            return {
                'top_resources': {},
                'cost_concentration': 0
            }

    def _calculate_cost_concentration(self, percentages: pd.Series) -> float:
        """Calculate cost concentration (Herfindahl-Hirschman Index)."""
        try:
            # Calculate HHI (ranges from 0 to 1)
            hhi = (percentages / 100) ** 2
            return round(hhi.sum(), 2)

        except Exception as e:
            logger.error(f"Error calculating cost concentration: {str(e)}")
            return 0

    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze cost trends."""
        try:
            # Resample to monthly
            monthly = df.resample('M')['cost'].sum()
            
            # Calculate trend metrics
            trend_analysis = {
                'linear_trend': self._calculate_linear_trend(monthly),
                'volatility': monthly.std() / monthly.mean(),
                'trend_changes': self._detect_trend_changes(monthly),
                'growth_stability': self._analyze_growth_stability(monthly)
            }

            return trend_analysis

        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {}

    def _calculate_linear_trend(self, data: pd.Series) -> Dict:
        """Calculate linear trend in the data."""
        try:
            x = np.arange(len(data))
            coefficients = np.polyfit(x, data, 1)
            
            return {
                'slope': coefficients[0],
                'trend_type': 'increasing' if coefficients[0] > 0 else 'decreasing',
                'trend_strength': abs(coefficients[0]) / data.mean()
            }

        except Exception as e:
            logger.error(f"Error calculating linear trend: {str(e)}")
            return {}

    def _detect_trend_changes(self, data: pd.Series) -> Dict:
        """Detect significant changes in trend."""
        try:
            # Calculate rolling mean and standard deviation
            rolling_mean = data.rolling(window=3).mean()
            rolling_std = data.rolling(window=3).std()
            
            # Detect significant deviations
            significant_changes = []
            for i in range(3, len(data)):
                if abs(data.iloc[i] - rolling_mean.iloc[i-1]) > 2 * rolling_std.iloc[i-1]:
                    significant_changes.append(data.index[i])

            return {
                'change_points': len(significant_changes),
                'last_change': significant_changes[-1] if significant_changes else None,
                'stability': 'stable' if len(significant_changes) <= 2 else 'volatile'
            }

        except Exception as e:
            logger.error(f"Error detecting trend changes: {str(e)}")
            return {}

    def _analyze_growth_stability(self, data: pd.Series) -> Dict:
        """Analyze stability of growth patterns."""
        try:
            growth_rates = data.pct_change()
            
            return {
                'growth_volatility': growth_rates.std(),
                'consistent_growth': abs(growth_rates.mean()) > growth_rates.std(),
                'growth_predictability': 'high' if growth_rates.std() < 0.1 else 'medium' if growth_rates.std() < 0.2 else 'low'
            }

        except Exception as e:
            logger.error(f"Error analyzing growth stability: {str(e)}")
            return {}
