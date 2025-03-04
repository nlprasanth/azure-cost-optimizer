from typing import Dict, List
import logging
from datetime import datetime
from .analyzer import BudgetAnalyzer
from .manager import BudgetManager

logger = logging.getLogger(__name__)

class BudgetOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = BudgetAnalyzer(subscription_id)
        self.manager = BudgetManager(subscription_id)

    def optimize_budgets(self) -> Dict:
        """
        Analyze and optimize budget configuration and spending.
        """
        try:
            # Get all budgets
            budgets = self.manager.list_budgets()
            if not budgets:
                return {
                    'status': 'error',
                    'message': 'No budgets found',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Analyze each budget
            budget_analyses = []
            for budget in budgets:
                analysis = self.analyzer.analyze_budget_performance(budget['name'])
                if analysis:
                    budget_analyses.append(analysis)

            # Generate optimization recommendations
            recommendations = self._generate_recommendations(budget_analyses)

            return {
                'status': 'success',
                'budget_count': len(budgets),
                'analyses': budget_analyses,
                'recommendations': recommendations,
                'summary': self._generate_summary(budget_analyses),
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing budgets: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _generate_recommendations(self, analyses: List[Dict]) -> List[Dict]:
        """Generate budget optimization recommendations."""
        try:
            recommendations = []
            
            for analysis in analyses:
                budget_metrics = analysis['spending_analysis']['budget_metrics']
                spending_patterns = analysis['spending_analysis']['spending_patterns']
                forecast = analysis['forecast_analysis']
                alerts = analysis['alerts_analysis']
                
                # Check budget utilization
                if budget_metrics['percentage_used'] > 90:
                    recommendations.append({
                        'type': 'budget_adjustment',
                        'priority': 'high',
                        'budget_name': analysis['budget_details']['name'],
                        'description': 'Budget nearly depleted',
                        'actions': [
                            'Review and increase budget allocation',
                            'Implement immediate cost controls',
                            'Review resource utilization'
                        ]
                    })
                elif budget_metrics['percentage_used'] < 50:
                    recommendations.append({
                        'type': 'budget_efficiency',
                        'priority': 'medium',
                        'budget_name': analysis['budget_details']['name'],
                        'description': 'Budget significantly underutilized',
                        'actions': [
                            'Consider reducing budget allocation',
                            'Reallocate funds to other areas',
                            'Review resource planning'
                        ]
                    })

                # Check spending patterns
                if spending_patterns['daily_pattern']['coefficient_of_variation'] > 0.5:
                    recommendations.append({
                        'type': 'spending_pattern',
                        'priority': 'medium',
                        'budget_name': analysis['budget_details']['name'],
                        'description': 'High daily spending variation detected',
                        'actions': [
                            'Implement auto-scaling policies',
                            'Review resource scheduling',
                            'Optimize workload distribution'
                        ]
                    })

                # Check forecast risk
                if forecast['projections']['risk_level'] == 'high':
                    recommendations.append({
                        'type': 'forecast_risk',
                        'priority': 'high',
                        'budget_name': analysis['budget_details']['name'],
                        'description': 'High risk of budget overrun',
                        'actions': [
                            'Implement immediate cost controls',
                            'Review and optimize resource usage',
                            'Consider budget adjustment'
                        ]
                    })

                # Check alert configuration
                for gap in alerts['coverage_analysis'].get('alert_gaps', []):
                    recommendations.append({
                        'type': 'alert_configuration',
                        'priority': 'medium',
                        'budget_name': analysis['budget_details']['name'],
                        'description': gap['description'],
                        'actions': [gap['recommendation']]
                    })

                # Add optimization opportunities
                for opportunity in analysis['optimization_opportunities']:
                    recommendations.append({
                        'type': 'cost_optimization',
                        'priority': opportunity['priority'],
                        'budget_name': analysis['budget_details']['name'],
                        'description': f"Optimization opportunity for {opportunity['type']}",
                        'potential_savings': opportunity['potential_savings'],
                        'actions': [
                            f"Review and optimize {opportunity['resource_type'] if 'resource_type' in opportunity else opportunity['resource_group']}",
                            'Implement resource right-sizing',
                            'Consider reserved instances or spot instances'
                        ]
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _generate_summary(self, analyses: List[Dict]) -> Dict:
        """Generate overall budget optimization summary."""
        try:
            total_budget = 0
            total_spent = 0
            high_risk_budgets = 0
            total_potential_savings = 0

            for analysis in analyses:
                budget_amount = analysis['budget_details']['amount']
                spent = analysis['spending_analysis']['total_spent']
                risk_level = analysis['forecast_analysis']['projections']['risk_level']
                
                total_budget += budget_amount
                total_spent += spent
                
                if risk_level == 'high':
                    high_risk_budgets += 1
                
                # Sum potential savings from optimization opportunities
                total_potential_savings += sum(
                    opp['potential_savings'] 
                    for opp in analysis['optimization_opportunities']
                )

            return {
                'budget_metrics': {
                    'total_budget': total_budget,
                    'total_spent': total_spent,
                    'overall_utilization': (total_spent / total_budget * 100) if total_budget > 0 else 0,
                    'high_risk_budgets': high_risk_budgets
                },
                'optimization_potential': {
                    'total_savings_potential': total_potential_savings,
                    'savings_percentage': (total_potential_savings / total_spent * 100) if total_spent > 0 else 0
                },
                'risk_assessment': {
                    'overall_risk': 'high' if high_risk_budgets > 0 else 'medium' if total_spent / total_budget > 0.8 else 'low',
                    'risk_factors': self._identify_risk_factors(analyses)
                }
            }

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {}

    def _identify_risk_factors(self, analyses: List[Dict]) -> List[Dict]:
        """Identify key risk factors across all budgets."""
        try:
            risk_factors = []
            
            # Check overall spending trend
            increasing_trends = sum(
                1 for a in analyses 
                if a['forecast_analysis']['trend_metrics']['trend_direction'] == 'increasing'
            )
            if increasing_trends > len(analyses) / 2:
                risk_factors.append({
                    'type': 'spending_trend',
                    'description': 'Majority of budgets show increasing spend trend',
                    'severity': 'high'
                })

            # Check alert coverage
            budgets_without_critical_alerts = sum(
                1 for a in analyses 
                if not a['alerts_analysis']['coverage_analysis']['has_critical_alerts']
            )
            if budgets_without_critical_alerts > 0:
                risk_factors.append({
                    'type': 'alert_coverage',
                    'description': f"{budgets_without_critical_alerts} budgets lack critical alerts",
                    'severity': 'medium'
                })

            # Check budget utilization distribution
            high_utilization = sum(
                1 for a in analyses 
                if a['spending_analysis']['budget_metrics']['percentage_used'] > 90
            )
            if high_utilization > 0:
                risk_factors.append({
                    'type': 'utilization',
                    'description': f"{high_utilization} budgets at >90% utilization",
                    'severity': 'high'
                })

            return risk_factors

        except Exception as e:
            logger.error(f"Error identifying risk factors: {str(e)}")
            return []
