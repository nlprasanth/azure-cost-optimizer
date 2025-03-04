from .analyzer import ScalingAnalyzer
from .manager import ScalingManager
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ScalingOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = ScalingAnalyzer(subscription_id)
        self.manager = ScalingManager(subscription_id)

    def optimize_scaling(self, time_range_days: int = 30) -> Dict:
        """Perform comprehensive scaling optimization."""
        try:
            # Analyze current scaling patterns
            analysis = self.analyzer.analyze_scaling_patterns(time_range_days)
            if not analysis:
                return {'error': 'Failed to analyze scaling patterns'}

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
            logger.error(f"Error optimizing scaling: {str(e)}")
            return {'error': str(e)}

    def _generate_recommendations(self, analysis: Dict) -> Dict:
        """Generate scaling optimization recommendations."""
        try:
            recommendations = {
                'immediate_actions': [],
                'short_term': [],
                'long_term': [],
                'cost_optimizations': [],
                'performance_improvements': []
            }

            # VMSS recommendations
            if 'vm_scale_sets' in analysis:
                vmss_data = analysis['vm_scale_sets']
                
                # Process optimization opportunities
                for opportunity in vmss_data.get('optimization_opportunities', []):
                    if opportunity.get('priority') == 'high':
                        recommendations['immediate_actions'].append({
                            'type': 'vmss_scaling',
                            'resource_id': opportunity['vmss_id'],
                            'name': opportunity['name'],
                            'current_config': opportunity['current_config'],
                            'recommended_config': opportunity['recommended_config'],
                            'potential_savings': opportunity.get('potential_savings', 0),
                            'priority': 'high'
                        })
                    else:
                        recommendations['short_term'].append({
                            'type': 'vmss_scaling',
                            'resource_id': opportunity['vmss_id'],
                            'name': opportunity['name'],
                            'current_config': opportunity['current_config'],
                            'recommended_config': opportunity['recommended_config'],
                            'potential_savings': opportunity.get('potential_savings', 0),
                            'priority': 'medium'
                        })

            # App Service recommendations
            if 'app_services' in analysis:
                app_data = analysis['app_services']
                
                # Process optimization opportunities
                for opportunity in app_data.get('optimization_opportunities', []):
                    if opportunity.get('priority') == 'high':
                        recommendations['immediate_actions'].append({
                            'type': 'app_service_scaling',
                            'resource_id': opportunity['app_id'],
                            'name': opportunity['name'],
                            'current_config': opportunity['current_config'],
                            'recommended_config': opportunity['recommended_config'],
                            'potential_savings': opportunity.get('potential_savings', 0),
                            'priority': 'high'
                        })
                    else:
                        recommendations['short_term'].append({
                            'type': 'app_service_scaling',
                            'resource_id': opportunity['app_id'],
                            'name': opportunity['name'],
                            'current_config': opportunity['current_config'],
                            'recommended_config': opportunity['recommended_config'],
                            'potential_savings': opportunity.get('potential_savings', 0),
                            'priority': 'medium'
                        })

            # AKS recommendations
            if 'aks_clusters' in analysis:
                aks_data = analysis['aks_clusters']
                
                # Process optimization opportunities
                for opportunity in aks_data.get('optimization_opportunities', []):
                    if opportunity.get('priority') == 'high':
                        recommendations['immediate_actions'].append({
                            'type': 'aks_scaling',
                            'resource_id': opportunity['cluster_id'],
                            'name': opportunity['name'],
                            'current_config': opportunity['current_config'],
                            'recommended_config': opportunity['recommended_config'],
                            'potential_savings': opportunity.get('potential_savings', 0),
                            'priority': 'high'
                        })
                    else:
                        recommendations['short_term'].append({
                            'type': 'aks_scaling',
                            'resource_id': opportunity['cluster_id'],
                            'name': opportunity['name'],
                            'current_config': opportunity['current_config'],
                            'recommended_config': opportunity['recommended_config'],
                            'potential_savings': opportunity.get('potential_savings', 0),
                            'priority': 'medium'
                        })

            # Process workload patterns
            if 'workload_patterns' in analysis:
                pattern_recommendations = self._generate_pattern_based_recommendations(
                    analysis['workload_patterns']
                )
                recommendations['long_term'].extend(pattern_recommendations)

            # Cost optimization recommendations
            if 'cost_impact' in analysis:
                cost_recommendations = self._generate_cost_optimization_recommendations(
                    analysis['cost_impact']
                )
                recommendations['cost_optimizations'].extend(cost_recommendations)

            # Performance improvement recommendations
            performance_recommendations = self._generate_performance_recommendations(analysis)
            recommendations['performance_improvements'].extend(performance_recommendations)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {}

    def _create_optimization_plan(self, analysis: Dict, recommendations: Dict) -> Dict:
        """Create a detailed optimization plan."""
        try:
            plan = {
                'phases': [
                    {
                        'name': 'Phase 1: Immediate Optimizations',
                        'description': 'Address critical scaling inefficiencies',
                        'actions': [],
                        'estimated_effort': 'low',
                        'priority': 'high'
                    },
                    {
                        'name': 'Phase 2: Pattern-Based Optimizations',
                        'description': 'Implement workload pattern-based scaling',
                        'actions': [],
                        'estimated_effort': 'medium',
                        'priority': 'medium'
                    },
                    {
                        'name': 'Phase 3: Advanced Optimizations',
                        'description': 'Implement predictive and advanced scaling strategies',
                        'actions': [],
                        'estimated_effort': 'high',
                        'priority': 'low'
                    }
                ],
                'estimated_timeline': '2-3 weeks',
                'risk_assessment': self._assess_optimization_risks(analysis),
                'implementation_steps': self._create_implementation_steps(recommendations)
            }

            # Add immediate optimization actions
            for rec in recommendations.get('immediate_actions', []):
                plan['phases'][0]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['name'],
                    'action': 'update_scaling_rules',
                    'config': rec['recommended_config'],
                    'potential_savings': rec.get('potential_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })

            # Add pattern-based optimization actions
            for rec in recommendations.get('short_term', []):
                plan['phases'][1]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['name'],
                    'action': 'implement_pattern_based_scaling',
                    'patterns': rec.get('patterns', {}),
                    'config': rec['recommended_config'],
                    'potential_savings': rec.get('potential_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })

            # Add advanced optimization actions
            for rec in recommendations.get('long_term', []):
                plan['phases'][2]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['name'],
                    'action': 'implement_advanced_scaling',
                    'strategy': rec.get('strategy', ''),
                    'config': rec.get('config', {}),
                    'potential_savings': rec.get('potential_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })

            return plan

        except Exception as e:
            logger.error(f"Error creating optimization plan: {str(e)}")
            return {}

    def _generate_pattern_based_recommendations(self, patterns: Dict) -> List[Dict]:
        """Generate recommendations based on workload patterns."""
        try:
            recommendations = []

            # Process daily patterns
            if 'daily_patterns' in patterns:
                daily = patterns['daily_patterns']
                if daily.get('peak_hours'):
                    recommendations.append({
                        'type': 'scheduled_scaling',
                        'pattern': 'daily',
                        'description': 'Implement time-based scaling for daily peak hours',
                        'config': {
                            'peak_hours': daily['peak_hours'],
                            'scale_out_factor': 1.5,
                            'scale_in_factor': 0.5
                        }
                    })

            # Process weekly patterns
            if 'weekly_patterns' in patterns:
                weekly = patterns['weekly_patterns']
                if weekly.get('weekday_patterns'):
                    recommendations.append({
                        'type': 'scheduled_scaling',
                        'pattern': 'weekly',
                        'description': 'Implement day-of-week based scaling',
                        'config': {
                            'weekday_config': weekly['weekday_patterns'],
                            'weekend_config': weekly.get('weekend_patterns', {})
                        }
                    })

            # Process seasonal patterns
            if 'seasonal_patterns' in patterns:
                seasonal = patterns['seasonal_patterns']
                if seasonal.get('seasonal_trends'):
                    recommendations.append({
                        'type': 'predictive_scaling',
                        'pattern': 'seasonal',
                        'description': 'Implement predictive scaling based on seasonal trends',
                        'config': {
                            'trends': seasonal['seasonal_trends'],
                            'prediction_window': '30d'
                        }
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating pattern-based recommendations: {str(e)}")
            return []

    def _generate_cost_optimization_recommendations(self, cost_impact: Dict) -> List[Dict]:
        """Generate cost optimization recommendations."""
        try:
            recommendations = []

            # Process resource-specific cost impact
            for resource_type, impact in cost_impact.get('resource_specific', {}).items():
                if impact.get('optimization_potential', 0) > 0:
                    recommendations.append({
                        'type': 'cost_optimization',
                        'resource_type': resource_type,
                        'potential_savings': impact['optimization_potential'],
                        'recommendations': impact.get('recommendations', [])
                    })

            # Add general cost optimization recommendations
            if 'optimization_potential' in cost_impact:
                recommendations.extend(
                    self._generate_general_cost_recommendations(
                        cost_impact['optimization_potential']
                    )
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating cost optimization recommendations: {str(e)}")
            return []

    def _generate_performance_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate performance improvement recommendations."""
        try:
            recommendations = []

            # Process VMSS performance
            if 'vm_scale_sets' in analysis:
                vmss_data = analysis['vm_scale_sets']
                for impact in vmss_data.get('performance_impact', []):
                    if impact.get('performance_issues'):
                        recommendations.append({
                            'type': 'performance_optimization',
                            'resource_type': 'vmss',
                            'resource_name': impact['name'],
                            'issues': impact['performance_issues'],
                            'recommendations': impact['recommendations']
                        })

            # Process App Service performance
            if 'app_services' in analysis:
                app_data = analysis['app_services']
                for impact in app_data.get('performance_impact', []):
                    if impact.get('performance_issues'):
                        recommendations.append({
                            'type': 'performance_optimization',
                            'resource_type': 'app_service',
                            'resource_name': impact['name'],
                            'issues': impact['performance_issues'],
                            'recommendations': impact['recommendations']
                        })

            # Process AKS performance
            if 'aks_clusters' in analysis:
                aks_data = analysis['aks_clusters']
                for impact in aks_data.get('performance_impact', []):
                    if impact.get('performance_issues'):
                        recommendations.append({
                            'type': 'performance_optimization',
                            'resource_type': 'aks',
                            'resource_name': impact['name'],
                            'issues': impact['performance_issues'],
                            'recommendations': impact['recommendations']
                        })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating performance recommendations: {str(e)}")
            return []

    def _assess_optimization_risks(self, analysis: Dict) -> Dict:
        """Assess risks associated with scaling optimization."""
        try:
            risks = {
                'high': [],
                'medium': [],
                'low': []
            }

            # Assess VMSS risks
            if 'vm_scale_sets' in analysis:
                vmss_count = len(analysis['vm_scale_sets'].get('scaling_metrics', []))
                if vmss_count > 5:
                    risks['high'].append({
                        'type': 'vmss_scaling',
                        'description': f'Large number of VMSS ({vmss_count}) to be optimized',
                        'mitigation': 'Implement changes gradually and monitor performance'
                    })

            # Assess App Service risks
            if 'app_services' in analysis:
                app_count = len(analysis['app_services'].get('scaling_metrics', []))
                if app_count > 10:
                    risks['medium'].append({
                        'type': 'app_service_scaling',
                        'description': f'Multiple App Services ({app_count}) to be optimized',
                        'mitigation': 'Test scaling rules in staging environment first'
                    })

            # Assess workload pattern risks
            if 'workload_patterns' in analysis:
                pattern_complexity = self._assess_pattern_complexity(
                    analysis['workload_patterns']
                )
                if pattern_complexity > 0.7:
                    risks['medium'].append({
                        'type': 'pattern_complexity',
                        'description': 'Complex workload patterns detected',
                        'mitigation': 'Implement pattern-based scaling gradually'
                    })

            return risks

        except Exception as e:
            logger.error(f"Error assessing optimization risks: {str(e)}")
            return {}
