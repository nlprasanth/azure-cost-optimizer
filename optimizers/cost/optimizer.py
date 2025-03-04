from .analyzer import CostAnalyzer
from .manager import CostManager
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CostOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = CostAnalyzer(subscription_id)
        self.manager = CostManager(subscription_id)

    def optimize_costs(self, time_range_days: int = 30) -> Dict:
        """Perform comprehensive cost optimization."""
        try:
            # Analyze costs
            analysis = self.analyzer.analyze_costs(time_range_days)
            if not analysis:
                return {'error': 'Failed to analyze costs'}

            # Generate recommendations
            recommendations = self._generate_recommendations(analysis)

            # Generate optimization plan
            optimization_plan = self._create_optimization_plan(analysis, recommendations)

            return {
                'analysis': analysis,
                'recommendations': recommendations,
                'optimization_plan': optimization_plan
            }

        except Exception as e:
            logger.error(f"Error optimizing costs: {str(e)}")
            return {'error': str(e)}

    def _generate_recommendations(self, analysis: Dict) -> Dict:
        """Generate cost optimization recommendations."""
        try:
            recommendations = {
                'immediate_actions': [],
                'short_term': [],
                'long_term': [],
                'cost_reduction': [],
                'efficiency_improvements': []
            }

            # Process resource cost recommendations
            if 'resource_costs' in analysis:
                resource_data = analysis['resource_costs']
                self._process_resource_recommendations(resource_data, recommendations)

            # Process service cost recommendations
            if 'service_costs' in analysis:
                service_data = analysis['service_costs']
                self._process_service_recommendations(service_data, recommendations)

            # Process cost trend recommendations
            if 'cost_trends' in analysis:
                trend_data = analysis['cost_trends']
                self._process_trend_recommendations(trend_data, recommendations)

            # Process anomaly recommendations
            if 'cost_anomalies' in analysis:
                anomaly_data = analysis['cost_anomalies']
                self._process_anomaly_recommendations(anomaly_data, recommendations)

            # Process optimization opportunities
            if 'optimization_opportunities' in analysis:
                opportunity_data = analysis['optimization_opportunities']
                self._process_opportunity_recommendations(opportunity_data, recommendations)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {}

    def _create_optimization_plan(self, analysis: Dict, recommendations: Dict) -> Dict:
        """Create a detailed cost optimization plan."""
        try:
            plan = {
                'phases': [
                    {
                        'name': 'Phase 1: Immediate Cost Reduction',
                        'description': 'Address immediate cost optimization opportunities',
                        'actions': [],
                        'estimated_savings': 0,
                        'priority': 'high'
                    },
                    {
                        'name': 'Phase 2: Resource Optimization',
                        'description': 'Optimize resource allocation and usage',
                        'actions': [],
                        'estimated_savings': 0,
                        'priority': 'medium'
                    },
                    {
                        'name': 'Phase 3: Long-term Cost Management',
                        'description': 'Implement sustainable cost management practices',
                        'actions': [],
                        'estimated_savings': 0,
                        'priority': 'low'
                    }
                ],
                'estimated_timeline': '2-3 weeks',
                'total_estimated_savings': 0,
                'risk_assessment': self._assess_optimization_risks(analysis),
                'implementation_steps': self._create_implementation_steps(recommendations)
            }

            # Add immediate cost reduction actions
            for rec in recommendations.get('immediate_actions', []):
                plan['phases'][0]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['resource_name'],
                    'action': 'implement_cost_reduction',
                    'estimated_savings': rec.get('estimated_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })
                plan['phases'][0]['estimated_savings'] += rec.get('estimated_savings', 0)

            # Add resource optimization actions
            for rec in recommendations.get('cost_reduction', []):
                plan['phases'][1]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['resource_name'],
                    'action': 'optimize_resource',
                    'estimated_savings': rec.get('estimated_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })
                plan['phases'][1]['estimated_savings'] += rec.get('estimated_savings', 0)

            # Add long-term management actions
            for rec in recommendations.get('long_term', []):
                plan['phases'][2]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['resource_name'],
                    'action': 'implement_cost_management',
                    'estimated_savings': rec.get('estimated_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })
                plan['phases'][2]['estimated_savings'] += rec.get('estimated_savings', 0)

            # Calculate total estimated savings
            plan['total_estimated_savings'] = sum(
                phase['estimated_savings'] for phase in plan['phases']
            )

            return plan

        except Exception as e:
            logger.error(f"Error creating optimization plan: {str(e)}")
            return {}

    def _process_resource_recommendations(self, resource_data: Dict, 
                                       recommendations: Dict):
        """Process resource-specific cost recommendations."""
        try:
            # Process compute recommendations
            if 'compute' in resource_data:
                compute_costs = resource_data['compute']
                if compute_costs['total_cost'] > 1000:  # High compute costs
                    recommendations['immediate_actions'].append({
                        'type': 'compute_optimization',
                        'resource_name': 'Compute Resources',
                        'issue': 'High compute costs',
                        'estimated_savings': compute_costs['total_cost'] * 0.3,
                        'recommendations': [
                            'Right-size underutilized VMs',
                            'Implement auto-shutdown for non-production VMs',
                            'Consider reserved instances for stable workloads'
                        ]
                    })

            # Process storage recommendations
            if 'storage' in resource_data:
                storage_costs = resource_data['storage']
                if storage_costs['total_cost'] > 500:  # High storage costs
                    recommendations['short_term'].append({
                        'type': 'storage_optimization',
                        'resource_name': 'Storage Resources',
                        'issue': 'High storage costs',
                        'estimated_savings': storage_costs['total_cost'] * 0.2,
                        'recommendations': [
                            'Implement lifecycle management policies',
                            'Move infrequently accessed data to cool storage',
                            'Delete unnecessary snapshots and backups'
                        ]
                    })

        except Exception as e:
            logger.error(f"Error processing resource recommendations: {str(e)}")

    def _process_service_recommendations(self, service_data: Dict, 
                                      recommendations: Dict):
        """Process service-specific cost recommendations."""
        try:
            for service, data in service_data.items():
                # Check for high-cost services
                if data['total_cost'] > 1000:
                    recommendations['cost_reduction'].append({
                        'type': 'service_optimization',
                        'resource_name': service,
                        'issue': 'High service costs',
                        'estimated_savings': data['total_cost'] * 0.25,
                        'recommendations': [
                            'Review service usage patterns',
                            'Optimize service configuration',
                            'Consider alternative service tiers'
                        ]
                    })

                # Check for inefficient usage
                if 'usage_metrics' in data:
                    efficiency = data['usage_metrics'].get('efficiency', 0)
                    if efficiency < 0.6:  # Less than 60% efficiency
                        recommendations['efficiency_improvements'].append({
                            'type': 'efficiency_optimization',
                            'resource_name': service,
                            'issue': 'Low resource efficiency',
                            'estimated_savings': data['total_cost'] * 0.15,
                            'recommendations': [
                                'Optimize resource allocation',
                                'Implement auto-scaling',
                                'Review service configuration'
                            ]
                        })

        except Exception as e:
            logger.error(f"Error processing service recommendations: {str(e)}")

    def _process_trend_recommendations(self, trend_data: Dict, recommendations: Dict):
        """Process cost trend recommendations."""
        try:
            # Process daily trends
            if 'daily_trends' in trend_data:
                daily = trend_data['daily_trends']
                if daily.get('trend_coefficient', 0) > 0.1:  # Increasing trend
                    recommendations['immediate_actions'].append({
                        'type': 'cost_trend_optimization',
                        'resource_name': 'Daily Cost Trend',
                        'issue': 'Increasing daily costs',
                        'estimated_savings': daily.get('average_daily_cost', 0) * 0.2,
                        'recommendations': [
                            'Implement stricter cost controls',
                            'Review recent resource additions',
                            'Optimize daily resource usage'
                        ]
                    })

            # Process monthly patterns
            if 'monthly_patterns' in trend_data:
                monthly = trend_data['monthly_patterns']
                if monthly.get('pattern_strength', 0) > 0.7:  # Strong pattern
                    recommendations['long_term'].append({
                        'type': 'pattern_optimization',
                        'resource_name': 'Monthly Cost Pattern',
                        'issue': 'Predictable cost pattern',
                        'estimated_savings': monthly.get('average_monthly_cost', 0) * 0.15,
                        'recommendations': [
                            'Implement scheduled scaling',
                            'Consider reserved instances',
                            'Optimize resource allocation based on patterns'
                        ]
                    })

        except Exception as e:
            logger.error(f"Error processing trend recommendations: {str(e)}")

    def _process_anomaly_recommendations(self, anomaly_data: Dict, 
                                      recommendations: Dict):
        """Process cost anomaly recommendations."""
        try:
            # Process daily anomalies
            if 'daily_anomalies' in anomaly_data:
                for anomaly in anomaly_data['daily_anomalies']:
                    if anomaly.get('severity', 0) > 0.8:  # High severity
                        recommendations['immediate_actions'].append({
                            'type': 'anomaly_resolution',
                            'resource_name': anomaly['resource_name'],
                            'issue': 'Cost spike detected',
                            'estimated_savings': anomaly.get('cost_impact', 0),
                            'recommendations': [
                                'Investigate sudden cost increase',
                                'Implement cost controls',
                                'Review resource usage patterns'
                            ]
                        })

            # Process service anomalies
            if 'service_anomalies' in anomaly_data:
                for anomaly in anomaly_data['service_anomalies']:
                    if anomaly.get('severity', 0) > 0.6:  # Medium-high severity
                        recommendations['short_term'].append({
                            'type': 'service_anomaly_resolution',
                            'resource_name': anomaly['service_name'],
                            'issue': 'Unusual service usage',
                            'estimated_savings': anomaly.get('cost_impact', 0),
                            'recommendations': [
                                'Review service configuration',
                                'Optimize service usage',
                                'Implement usage monitoring'
                            ]
                        })

        except Exception as e:
            logger.error(f"Error processing anomaly recommendations: {str(e)}")

    def _process_opportunity_recommendations(self, opportunity_data: Dict, 
                                          recommendations: Dict):
        """Process optimization opportunity recommendations."""
        try:
            # Process immediate opportunities
            if 'immediate' in opportunity_data:
                for opportunity in opportunity_data['immediate']:
                    recommendations['immediate_actions'].append({
                        'type': 'cost_optimization',
                        'resource_name': opportunity['resource_name'],
                        'issue': opportunity['issue'],
                        'estimated_savings': opportunity.get('estimated_savings', 0),
                        'recommendations': opportunity['recommendations']
                    })

            # Process short-term opportunities
            if 'short_term' in opportunity_data:
                for opportunity in opportunity_data['short_term']:
                    recommendations['short_term'].append({
                        'type': 'cost_optimization',
                        'resource_name': opportunity['resource_name'],
                        'issue': opportunity['issue'],
                        'estimated_savings': opportunity.get('estimated_savings', 0),
                        'recommendations': opportunity['recommendations']
                    })

            # Process long-term opportunities
            if 'long_term' in opportunity_data:
                for opportunity in opportunity_data['long_term']:
                    recommendations['long_term'].append({
                        'type': 'cost_optimization',
                        'resource_name': opportunity['resource_name'],
                        'issue': opportunity['issue'],
                        'estimated_savings': opportunity.get('estimated_savings', 0),
                        'recommendations': opportunity['recommendations']
                    })

        except Exception as e:
            logger.error(f"Error processing opportunity recommendations: {str(e)}")

    def _assess_optimization_risks(self, analysis: Dict) -> Dict:
        """Assess risks associated with cost optimization."""
        try:
            risks = {
                'high': [],
                'medium': [],
                'low': []
            }

            # Assess resource modification risks
            if 'resource_costs' in analysis:
                resource_count = sum(
                    1 for category in analysis['resource_costs'].values()
                    if category.get('total_cost', 0) > 1000
                )
                if resource_count > 5:
                    risks['high'].append({
                        'type': 'resource_modification',
                        'description': 'Large number of high-cost resources to optimize',
                        'mitigation': 'Implement changes gradually and monitor impact'
                    })

            # Assess service modification risks
            if 'service_costs' in analysis:
                service_count = sum(
                    1 for service in analysis['service_costs'].values()
                    if service.get('total_cost', 0) > 1000
                )
                if service_count > 3:
                    risks['medium'].append({
                        'type': 'service_modification',
                        'description': 'Multiple high-cost services to optimize',
                        'mitigation': 'Prioritize services and optimize incrementally'
                    })

            return risks

        except Exception as e:
            logger.error(f"Error assessing optimization risks: {str(e)}")
            return {}
