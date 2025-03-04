from typing import Dict, List
import logging
from datetime import datetime
from .analyzer import CostForecastAnalyzer
from .forecaster import CostForecaster

logger = logging.getLogger(__name__)

class CostForecastOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = CostForecastAnalyzer(subscription_id)
        self.forecaster = CostForecaster()

    def generate_cost_forecast(self, months: int = 12) -> Dict:
        """
        Generate cost forecasts and analysis.
        """
        try:
            # Analyze historical costs
            analysis = self.analyzer.analyze_historical_costs(months)
            if not analysis:
                return {
                    'status': 'error',
                    'message': 'Failed to analyze historical costs',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Get historical data for forecasting
            historical_data = self.analyzer._get_historical_costs(months)
            
            # Generate forecasts
            forecasts = self.forecaster.generate_forecast(historical_data, analysis)
            if not forecasts:
                return {
                    'status': 'error',
                    'message': 'Failed to generate forecasts',
                    'timestamp': datetime.utcnow().isoformat()
                }

            return {
                'status': 'success',
                'historical_analysis': analysis,
                'forecasts': forecasts,
                'insights': self._generate_insights(analysis, forecasts),
                'recommendations': self._generate_recommendations(analysis, forecasts),
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating cost forecast: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _generate_insights(self, analysis: Dict, forecasts: Dict) -> List[Dict]:
        """Generate insights from analysis and forecasts."""
        try:
            insights = []
            
            # Cost trend insights
            if analysis['trends']['linear_trend']['trend_type'] == 'increasing':
                insights.append({
                    'type': 'trend',
                    'category': 'cost_trend',
                    'severity': 'high' if analysis['trends']['linear_trend']['trend_strength'] > 0.1 else 'medium',
                    'description': 'Costs show an increasing trend',
                    'details': {
                        'trend_strength': analysis['trends']['linear_trend']['trend_strength'],
                        'monthly_growth': analysis['month_over_month_growth']['average_growth']
                    }
                })

            # Seasonality insights
            if analysis['seasonality']['monthly']:
                insights.append({
                    'type': 'pattern',
                    'category': 'seasonality',
                    'severity': 'medium',
                    'description': 'Clear monthly cost patterns detected',
                    'details': analysis['seasonality']['monthly']
                })

            # Cost concentration insights
            if analysis['cost_drivers']['cost_concentration'] > 0.5:
                insights.append({
                    'type': 'concentration',
                    'category': 'cost_distribution',
                    'severity': 'high',
                    'description': 'High concentration of costs in few resources',
                    'details': {
                        'concentration_index': analysis['cost_drivers']['cost_concentration'],
                        'top_resources': analysis['cost_drivers']['top_resources']
                    }
                })

            # Forecast uncertainty insights
            uncertainty_metrics = forecasts['metrics']['uncertainty_metrics']
            high_uncertainty = any(
                metrics['relative_uncertainty'] > 0.2 
                for metrics in uncertainty_metrics.values()
            )
            if high_uncertainty:
                insights.append({
                    'type': 'uncertainty',
                    'category': 'forecast_quality',
                    'severity': 'medium',
                    'description': 'High uncertainty in cost forecasts',
                    'details': uncertainty_metrics
                })

            # Growth rate insights
            forecast_growth = forecasts['metrics']['forecast_growth']
            if abs(forecast_growth) > 0.2:
                insights.append({
                    'type': 'growth',
                    'category': 'future_trend',
                    'severity': 'high',
                    'description': f"Significant {'increase' if forecast_growth > 0 else 'decrease'} in costs expected",
                    'details': {
                        'growth_rate': forecast_growth,
                        'trend': forecasts['metrics']['forecast_trend']
                    }
                })

            return insights

        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []

    def _generate_recommendations(self, analysis: Dict, forecasts: Dict) -> List[Dict]:
        """Generate recommendations based on analysis and forecasts."""
        try:
            recommendations = []
            
            # Cost trend recommendations
            if analysis['trends']['linear_trend']['trend_type'] == 'increasing':
                recommendations.append({
                    'type': 'cost_optimization',
                    'priority': 'high',
                    'title': 'Implement Cost Controls',
                    'description': 'Rising cost trend detected. Consider implementing:',
                    'actions': [
                        'Set up budget alerts',
                        'Review and optimize resource usage',
                        'Implement auto-scaling policies',
                        'Consider reserved instances for stable workloads'
                    ]
                })

            # Seasonal optimization recommendations
            if analysis['seasonality']['monthly']:
                recommendations.append({
                    'type': 'resource_management',
                    'priority': 'medium',
                    'title': 'Optimize for Seasonal Patterns',
                    'description': 'Clear seasonal patterns detected. Consider:',
                    'actions': [
                        'Implement auto-scaling based on seasonal patterns',
                        'Schedule resources based on usage patterns',
                        'Review capacity planning for peak periods'
                    ]
                })

            # Cost distribution recommendations
            if analysis['cost_drivers']['cost_concentration'] > 0.5:
                recommendations.append({
                    'type': 'cost_distribution',
                    'priority': 'high',
                    'title': 'Diversify Resource Usage',
                    'description': 'High concentration of costs. Consider:',
                    'actions': [
                        'Review and optimize top cost-driving resources',
                        'Evaluate alternative service options',
                        'Implement multi-service architecture where applicable'
                    ]
                })

            # Forecast-based recommendations
            forecast_growth = forecasts['metrics']['forecast_growth']
            if forecast_growth > 0.2:
                recommendations.append({
                    'type': 'future_planning',
                    'priority': 'high',
                    'title': 'Prepare for Cost Increases',
                    'description': 'Significant cost increase expected. Actions needed:',
                    'actions': [
                        'Review and adjust budgets',
                        'Implement stricter cost controls',
                        'Evaluate cost-saving opportunities',
                        'Consider long-term resource commitments'
                    ]
                })

            # Uncertainty management recommendations
            uncertainty_metrics = forecasts['metrics']['uncertainty_metrics']
            if any(metrics['relative_uncertainty'] > 0.2 for metrics in uncertainty_metrics.values()):
                recommendations.append({
                    'type': 'risk_management',
                    'priority': 'medium',
                    'title': 'Manage Cost Uncertainty',
                    'description': 'High forecast uncertainty detected. Consider:',
                    'actions': [
                        'Set up buffer in cost budgets',
                        'Implement more granular monitoring',
                        'Review and stabilize variable cost components',
                        'Consider reserved instances for stable components'
                    ]
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def get_forecast_summary(self, result: Dict) -> Dict:
        """Generate a summary of forecast results."""
        try:
            if result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': 'Cannot generate summary from failed forecast'
                }

            forecasts = result['forecasts']
            analysis = result['historical_analysis']

            summary = {
                'historical_metrics': {
                    'total_cost': analysis['total_cost'],
                    'average_monthly_cost': analysis['average_monthly_cost'],
                    'cost_trend': analysis['trends']['linear_trend']['trend_type'],
                    'cost_variability': analysis['cost_std_dev'] / analysis['average_monthly_cost']
                },
                'forecast_metrics': {
                    'total_forecast': forecasts['metrics']['total_forecast'],
                    'average_monthly_forecast': forecasts['metrics']['average_monthly_forecast'],
                    'forecast_trend': forecasts['metrics']['forecast_trend'],
                    'forecast_growth': forecasts['metrics']['forecast_growth']
                },
                'key_insights': self._summarize_insights(result['insights']),
                'key_recommendations': self._summarize_recommendations(result['recommendations']),
                'uncertainty_assessment': self._summarize_uncertainty(forecasts['metrics']['uncertainty_metrics'])
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating forecast summary: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _summarize_insights(self, insights: List[Dict]) -> Dict:
        """Summarize key insights."""
        try:
            return {
                'high_severity': len([i for i in insights if i['severity'] == 'high']),
                'medium_severity': len([i for i in insights if i['severity'] == 'medium']),
                'categories': list(set(i['category'] for i in insights)),
                'top_insights': [i['description'] for i in insights if i['severity'] == 'high']
            }

        except Exception as e:
            logger.error(f"Error summarizing insights: {str(e)}")
            return {}

    def _summarize_recommendations(self, recommendations: List[Dict]) -> Dict:
        """Summarize key recommendations."""
        try:
            return {
                'high_priority': len([r for r in recommendations if r['priority'] == 'high']),
                'medium_priority': len([r for r in recommendations if r['priority'] == 'medium']),
                'categories': list(set(r['type'] for r in recommendations)),
                'top_recommendations': [r['title'] for r in recommendations if r['priority'] == 'high']
            }

        except Exception as e:
            logger.error(f"Error summarizing recommendations: {str(e)}")
            return {}

    def _summarize_uncertainty(self, uncertainty_metrics: Dict) -> Dict:
        """Summarize forecast uncertainty."""
        try:
            return {
                'overall_assessment': 'high' if any(
                    metrics['relative_uncertainty'] > 0.2 
                    for metrics in uncertainty_metrics.values()
                ) else 'medium' if any(
                    metrics['relative_uncertainty'] > 0.1 
                    for metrics in uncertainty_metrics.values()
                ) else 'low',
                'confidence_levels': {
                    level: metrics['relative_uncertainty']
                    for level, metrics in uncertainty_metrics.items()
                }
            }

        except Exception as e:
            logger.error(f"Error summarizing uncertainty: {str(e)}")
            return {}
