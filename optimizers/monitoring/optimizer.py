from .analyzer import MonitoringAnalyzer
from .manager import MonitoringManager
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MonitoringOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = MonitoringAnalyzer(subscription_id)
        self.manager = MonitoringManager(subscription_id)

    def optimize_monitoring(self, time_range_days: int = 7) -> Dict:
        """Perform comprehensive monitoring optimization."""
        try:
            # Analyze resource health
            analysis = self.analyzer.analyze_resource_health(time_range_days)
            if not analysis:
                return {'error': 'Failed to analyze resource health'}

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
            logger.error(f"Error optimizing monitoring: {str(e)}")
            return {'error': str(e)}

    def _generate_recommendations(self, analysis: Dict) -> Dict:
        """Generate monitoring optimization recommendations."""
        try:
            recommendations = {
                'immediate_actions': [],
                'short_term': [],
                'long_term': [],
                'monitoring_improvements': [],
                'alert_optimizations': []
            }

            # Process VM recommendations
            if 'virtual_machines' in analysis:
                vm_data = analysis['virtual_machines']
                self._process_vm_recommendations(vm_data, recommendations)

            # Process App Service recommendations
            if 'app_services' in analysis:
                app_data = analysis['app_services']
                self._process_app_recommendations(app_data, recommendations)

            # Process Storage recommendations
            if 'storage_accounts' in analysis:
                storage_data = analysis['storage_accounts']
                self._process_storage_recommendations(storage_data, recommendations)

            # Process Network recommendations
            if 'network_resources' in analysis:
                network_data = analysis['network_resources']
                self._process_network_recommendations(network_data, recommendations)

            # Process anomaly recommendations
            if 'anomalies' in analysis:
                anomaly_data = analysis['anomalies']
                self._process_anomaly_recommendations(anomaly_data, recommendations)

            # Process performance trend recommendations
            if 'performance_trends' in analysis:
                trend_data = analysis['performance_trends']
                self._process_trend_recommendations(trend_data, recommendations)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {}

    def _create_optimization_plan(self, analysis: Dict, recommendations: Dict) -> Dict:
        """Create a detailed monitoring optimization plan."""
        try:
            plan = {
                'phases': [
                    {
                        'name': 'Phase 1: Critical Monitoring Improvements',
                        'description': 'Address critical monitoring gaps and alerts',
                        'actions': [],
                        'estimated_effort': 'low',
                        'priority': 'high'
                    },
                    {
                        'name': 'Phase 2: Enhanced Monitoring Configuration',
                        'description': 'Implement advanced monitoring and alerting',
                        'actions': [],
                        'estimated_effort': 'medium',
                        'priority': 'medium'
                    },
                    {
                        'name': 'Phase 3: Proactive Monitoring Strategy',
                        'description': 'Implement predictive monitoring and automation',
                        'actions': [],
                        'estimated_effort': 'high',
                        'priority': 'low'
                    }
                ],
                'estimated_timeline': '2-3 weeks',
                'risk_assessment': self._assess_optimization_risks(analysis),
                'implementation_steps': self._create_implementation_steps(recommendations)
            }

            # Add immediate actions
            for rec in recommendations.get('immediate_actions', []):
                plan['phases'][0]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['resource_name'],
                    'action': 'update_monitoring_config',
                    'config': rec['recommended_config'],
                    'priority': 'high',
                    'implementation': self._get_implementation_details(rec)
                })

            # Add enhanced monitoring actions
            for rec in recommendations.get('monitoring_improvements', []):
                plan['phases'][1]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['resource_name'],
                    'action': 'enhance_monitoring',
                    'config': rec['recommended_config'],
                    'priority': 'medium',
                    'implementation': self._get_implementation_details(rec)
                })

            # Add proactive monitoring actions
            for rec in recommendations.get('long_term', []):
                plan['phases'][2]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['resource_name'],
                    'action': 'implement_proactive_monitoring',
                    'config': rec['recommended_config'],
                    'priority': 'low',
                    'implementation': self._get_implementation_details(rec)
                })

            return plan

        except Exception as e:
            logger.error(f"Error creating optimization plan: {str(e)}")
            return {}

    def _process_vm_recommendations(self, vm_data: Dict, recommendations: Dict):
        """Process VM-specific monitoring recommendations."""
        try:
            for issue in vm_data.get('performance_issues', []):
                if issue.get('severity') == 'high':
                    recommendations['immediate_actions'].append({
                        'type': 'vm_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_vm_monitoring_config(issue)
                    })
                else:
                    recommendations['monitoring_improvements'].append({
                        'type': 'vm_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_vm_monitoring_config(issue)
                    })

        except Exception as e:
            logger.error(f"Error processing VM recommendations: {str(e)}")

    def _process_app_recommendations(self, app_data: Dict, recommendations: Dict):
        """Process App Service-specific monitoring recommendations."""
        try:
            for issue in app_data.get('performance_issues', []):
                if issue.get('severity') == 'high':
                    recommendations['immediate_actions'].append({
                        'type': 'app_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_app_monitoring_config(issue)
                    })
                else:
                    recommendations['monitoring_improvements'].append({
                        'type': 'app_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_app_monitoring_config(issue)
                    })

        except Exception as e:
            logger.error(f"Error processing App recommendations: {str(e)}")

    def _process_storage_recommendations(self, storage_data: Dict, recommendations: Dict):
        """Process Storage-specific monitoring recommendations."""
        try:
            for issue in storage_data.get('performance_issues', []):
                if issue.get('severity') == 'high':
                    recommendations['immediate_actions'].append({
                        'type': 'storage_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_storage_monitoring_config(issue)
                    })
                else:
                    recommendations['monitoring_improvements'].append({
                        'type': 'storage_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_storage_monitoring_config(issue)
                    })

        except Exception as e:
            logger.error(f"Error processing Storage recommendations: {str(e)}")

    def _process_network_recommendations(self, network_data: Dict, recommendations: Dict):
        """Process Network-specific monitoring recommendations."""
        try:
            for issue in network_data.get('performance_issues', []):
                if issue.get('severity') == 'high':
                    recommendations['immediate_actions'].append({
                        'type': 'network_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_network_monitoring_config(issue)
                    })
                else:
                    recommendations['monitoring_improvements'].append({
                        'type': 'network_monitoring',
                        'resource_name': issue['name'],
                        'issue': issue['issues'],
                        'recommended_config': self._get_network_monitoring_config(issue)
                    })

        except Exception as e:
            logger.error(f"Error processing Network recommendations: {str(e)}")

    def _process_anomaly_recommendations(self, anomaly_data: Dict, recommendations: Dict):
        """Process anomaly-based monitoring recommendations."""
        try:
            for resource_type, anomalies in anomaly_data.items():
                for anomaly in anomalies:
                    if anomaly.get('severity') == 'high':
                        recommendations['immediate_actions'].append({
                            'type': f'{resource_type}_monitoring',
                            'resource_name': anomaly['name'],
                            'issue': 'Anomaly detected',
                            'recommended_config': self._get_anomaly_monitoring_config(anomaly)
                        })
                    else:
                        recommendations['alert_optimizations'].append({
                            'type': f'{resource_type}_monitoring',
                            'resource_name': anomaly['name'],
                            'issue': 'Anomaly detected',
                            'recommended_config': self._get_anomaly_monitoring_config(anomaly)
                        })

        except Exception as e:
            logger.error(f"Error processing anomaly recommendations: {str(e)}")

    def _process_trend_recommendations(self, trend_data: Dict, recommendations: Dict):
        """Process trend-based monitoring recommendations."""
        try:
            for resource_type, trends in trend_data.items():
                for trend in trends:
                    recommendations['long_term'].append({
                        'type': f'{resource_type}_monitoring',
                        'resource_name': trend['name'],
                        'trend': trend['pattern'],
                        'recommended_config': self._get_trend_monitoring_config(trend)
                    })

        except Exception as e:
            logger.error(f"Error processing trend recommendations: {str(e)}")

    def _assess_optimization_risks(self, analysis: Dict) -> Dict:
        """Assess risks associated with monitoring optimization."""
        try:
            risks = {
                'high': [],
                'medium': [],
                'low': []
            }

            # Assess alert volume risks
            alert_count = sum(
                len(data.get('performance_issues', [])) 
                for data in analysis.values() 
                if isinstance(data, dict)
            )
            if alert_count > 100:
                risks['high'].append({
                    'type': 'alert_volume',
                    'description': 'High number of alerts may cause alert fatigue',
                    'mitigation': 'Implement alert aggregation and correlation'
                })

            # Assess monitoring coverage risks
            coverage_gaps = self._assess_monitoring_coverage(analysis)
            if coverage_gaps:
                risks['medium'].append({
                    'type': 'monitoring_coverage',
                    'description': 'Gaps in monitoring coverage detected',
                    'mitigation': 'Implement comprehensive monitoring'
                })

            return risks

        except Exception as e:
            logger.error(f"Error assessing optimization risks: {str(e)}")
            return {}
