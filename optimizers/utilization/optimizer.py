from .analyzer import UtilizationAnalyzer
from .manager import ResourceManager
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class UtilizationOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = UtilizationAnalyzer(subscription_id)
        self.manager = ResourceManager(subscription_id)

    def optimize_utilization(self, time_range_days: int = 30) -> Dict:
        """Perform comprehensive utilization optimization."""
        try:
            # Analyze current utilization
            analysis = self.analyzer.analyze_resource_utilization(time_range_days)
            if not analysis:
                return {'error': 'Failed to analyze resource utilization'}

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
            logger.error(f"Error optimizing utilization: {str(e)}")
            return {'error': str(e)}

    def _generate_recommendations(self, analysis: Dict) -> Dict:
        """Generate optimization recommendations based on analysis."""
        try:
            recommendations = {
                'immediate_actions': [],
                'short_term': [],
                'long_term': [],
                'cost_savings': [],
                'performance_improvements': []
            }

            # VM recommendations
            if 'virtual_machines' in analysis:
                vm_data = analysis['virtual_machines']
                
                # Immediate actions for underutilized VMs
                for vm in vm_data.get('underutilized_vms', []):
                    recommendations['immediate_actions'].append({
                        'type': 'vm_optimization',
                        'resource_id': vm['vm_id'],
                        'name': vm['name'],
                        'action': 'resize_down',
                        'current_metrics': vm['metrics'],
                        'potential_savings': vm.get('potential_savings', 0),
                        'priority': 'high'
                    })

                # Right-sizing recommendations
                for vm in vm_data.get('right_size_candidates', []):
                    recommendations['short_term'].append({
                        'type': 'vm_rightsizing',
                        'resource_id': vm['vm_id'],
                        'name': vm['name'],
                        'current_size': vm['current_size'],
                        'recommended_size': vm['recommended_size'],
                        'potential_savings': vm['potential_savings'],
                        'priority': 'medium'
                    })

                # Stop recommendations
                for vm in vm_data.get('stop_candidates', []):
                    recommendations['immediate_actions'].append({
                        'type': 'vm_stop',
                        'resource_id': vm['vm_id'],
                        'name': vm['name'],
                        'last_active': vm['last_active'],
                        'potential_savings': vm['potential_savings'],
                        'priority': 'high'
                    })

            # Storage recommendations
            if 'storage_accounts' in analysis:
                storage_data = analysis['storage_accounts']
                
                # Tier optimization recommendations
                for account in storage_data.get('tier_recommendations', []):
                    recommendations['short_term'].append({
                        'type': 'storage_tier_optimization',
                        'resource_id': account['account_id'],
                        'name': account['name'],
                        'current_tier': account['current_tier'],
                        'recommended_tier': account['recommended_tier'],
                        'potential_savings': account['potential_savings'],
                        'priority': 'medium'
                    })

            # Network recommendations
            if 'network_resources' in analysis:
                network_data = analysis['network_resources']
                
                for resource in network_data.get('optimization_candidates', []):
                    recommendations['short_term'].append({
                        'type': 'network_optimization',
                        'resource_id': resource['resource_id'],
                        'name': resource['name'],
                        'optimization_type': resource['optimization_type'],
                        'potential_savings': resource['potential_savings'],
                        'priority': 'medium'
                    })

            # Cost savings summary
            total_savings = sum(
                rec.get('potential_savings', 0) 
                for recs in recommendations.values() 
                for rec in recs
            )
            recommendations['cost_savings'] = {
                'total_potential_savings': total_savings,
                'savings_by_category': self._calculate_savings_by_category(recommendations)
            }

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
                        'description': 'Address highly underutilized resources and immediate cost-saving opportunities',
                        'actions': [],
                        'estimated_effort': 'low',
                        'priority': 'high'
                    },
                    {
                        'name': 'Phase 2: Resource Right-sizing',
                        'description': 'Implement resource right-sizing recommendations',
                        'actions': [],
                        'estimated_effort': 'medium',
                        'priority': 'medium'
                    },
                    {
                        'name': 'Phase 3: Long-term Optimizations',
                        'description': 'Implement architectural and long-term optimization strategies',
                        'actions': [],
                        'estimated_effort': 'high',
                        'priority': 'low'
                    }
                ],
                'estimated_timeline': '2-4 weeks',
                'risk_assessment': self._assess_optimization_risks(analysis),
                'implementation_steps': self._create_implementation_steps(recommendations)
            }

            # Add immediate optimization actions
            for rec in recommendations.get('immediate_actions', []):
                plan['phases'][0]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['name'],
                    'action': rec.get('action', 'optimize'),
                    'potential_savings': rec.get('potential_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })

            # Add right-sizing actions
            for rec in recommendations.get('short_term', []):
                plan['phases'][1]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['name'],
                    'action': 'resize',
                    'details': {
                        'current_size': rec.get('current_size'),
                        'recommended_size': rec.get('recommended_size')
                    },
                    'potential_savings': rec.get('potential_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })

            # Add long-term optimization actions
            for rec in recommendations.get('long_term', []):
                plan['phases'][2]['actions'].append({
                    'type': rec['type'],
                    'resource': rec['name'],
                    'action': rec.get('action', 'optimize'),
                    'potential_savings': rec.get('potential_savings', 0),
                    'implementation': self._get_implementation_details(rec)
                })

            return plan

        except Exception as e:
            logger.error(f"Error creating optimization plan: {str(e)}")
            return {}

    def _calculate_savings_by_category(self, recommendations: Dict) -> Dict:
        """Calculate potential savings by category."""
        try:
            savings = {
                'compute': 0,
                'storage': 0,
                'network': 0,
                'other': 0
            }

            for category in recommendations:
                if isinstance(recommendations[category], list):
                    for rec in recommendations[category]:
                        if 'vm' in rec.get('type', ''):
                            savings['compute'] += rec.get('potential_savings', 0)
                        elif 'storage' in rec.get('type', ''):
                            savings['storage'] += rec.get('potential_savings', 0)
                        elif 'network' in rec.get('type', ''):
                            savings['network'] += rec.get('potential_savings', 0)
                        else:
                            savings['other'] += rec.get('potential_savings', 0)

            return savings

        except Exception as e:
            logger.error(f"Error calculating savings by category: {str(e)}")
            return {}

    def _assess_optimization_risks(self, analysis: Dict) -> Dict:
        """Assess risks associated with optimization actions."""
        try:
            risks = {
                'high': [],
                'medium': [],
                'low': []
            }

            # Assess VM-related risks
            if 'virtual_machines' in analysis:
                vm_count = len(analysis['virtual_machines'].get('right_size_candidates', []))
                if vm_count > 10:
                    risks['high'].append({
                        'type': 'vm_rightsizing',
                        'description': f'Large number of VMs ({vm_count}) to be resized',
                        'mitigation': 'Implement changes in batches and validate after each batch'
                    })

            # Assess storage-related risks
            if 'storage_accounts' in analysis:
                storage_count = len(analysis['storage_accounts'].get('tier_recommendations', []))
                if storage_count > 5:
                    risks['medium'].append({
                        'type': 'storage_optimization',
                        'description': f'Multiple storage accounts ({storage_count}) to be optimized',
                        'mitigation': 'Validate access patterns before changing tiers'
                    })

            return risks

        except Exception as e:
            logger.error(f"Error assessing optimization risks: {str(e)}")
            return {}

    def _create_implementation_steps(self, recommendations: Dict) -> List[Dict]:
        """Create detailed implementation steps."""
        try:
            steps = []

            # Add steps for immediate actions
            for rec in recommendations.get('immediate_actions', []):
                steps.extend(self._create_action_steps(rec))

            # Add steps for short-term actions
            for rec in recommendations.get('short_term', []):
                steps.extend(self._create_action_steps(rec))

            # Add validation and monitoring steps
            steps.append({
                'phase': 'validation',
                'description': 'Monitor resource performance after changes',
                'duration': '1 week',
                'success_criteria': [
                    'No performance degradation',
                    'Cost reduction achieved',
                    'No service disruptions'
                ]
            })

            return steps

        except Exception as e:
            logger.error(f"Error creating implementation steps: {str(e)}")
            return []

    def _create_action_steps(self, recommendation: Dict) -> List[Dict]:
        """Create steps for a specific recommendation."""
        try:
            steps = []
            
            if recommendation['type'] == 'vm_rightsizing':
                steps.extend([
                    {
                        'phase': 'preparation',
                        'description': f"Backup VM {recommendation['name']}",
                        'duration': '1 hour'
                    },
                    {
                        'phase': 'implementation',
                        'description': f"Resize VM {recommendation['name']} to {recommendation['recommended_size']}",
                        'duration': '1 hour'
                    },
                    {
                        'phase': 'validation',
                        'description': f"Validate VM {recommendation['name']} performance",
                        'duration': '4 hours'
                    }
                ])
            elif recommendation['type'] == 'storage_tier_optimization':
                steps.extend([
                    {
                        'phase': 'preparation',
                        'description': f"Analyze access patterns for {recommendation['name']}",
                        'duration': '2 hours'
                    },
                    {
                        'phase': 'implementation',
                        'description': f"Change storage tier for {recommendation['name']}",
                        'duration': '1 hour'
                    }
                ])

            return steps

        except Exception as e:
            logger.error(f"Error creating action steps: {str(e)}")
            return []

    def _get_implementation_details(self, recommendation: Dict) -> Dict:
        """Get implementation details for a recommendation."""
        try:
            details = {
                'steps': [],
                'prerequisites': [],
                'validation_criteria': []
            }

            if recommendation['type'] == 'vm_rightsizing':
                details.update({
                    'steps': [
                        'Create VM backup',
                        'Schedule maintenance window',
                        'Resize VM',
                        'Validate performance'
                    ],
                    'prerequisites': [
                        'Backup completed',
                        'Maintenance window approved',
                        'Application owners notified'
                    ],
                    'validation_criteria': [
                        'VM starts successfully',
                        'Applications running correctly',
                        'Performance metrics within expected range'
                    ]
                })
            elif recommendation['type'] == 'storage_tier_optimization':
                details.update({
                    'steps': [
                        'Analyze current access patterns',
                        'Change storage tier',
                        'Monitor performance'
                    ],
                    'prerequisites': [
                        'Access pattern analysis completed',
                        'No active large data transfers'
                    ],
                    'validation_criteria': [
                        'Data accessible',
                        'Performance meets requirements',
                        'No increased costs'
                    ]
                })

            return details

        except Exception as e:
            logger.error(f"Error getting implementation details: {str(e)}")
            return {}
