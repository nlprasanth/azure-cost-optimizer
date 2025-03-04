from typing import Dict, List
import logging
from datetime import datetime
from .analyzer import NetworkAnalyzer
from .recommendations import NetworkOptimizationRecommender

logger = logging.getLogger(__name__)

class NetworkOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = NetworkAnalyzer(subscription_id)
        self.recommender = NetworkOptimizationRecommender()

    def optimize_network(self, resource_group: str) -> Dict:
        """
        Analyze and optimize network resources in a resource group.
        """
        try:
            # Get network analysis
            network_analysis = self.analyzer.analyze_network_resources(resource_group)
            if not network_analysis:
                return {
                    'status': 'error',
                    'message': f'Failed to analyze network resources in {resource_group}',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Get recommendations
            recommendations = self.recommender.get_recommendations(network_analysis)

            # Calculate potential savings
            savings = self.recommender.calculate_savings(network_analysis, recommendations)

            return {
                'status': 'success',
                'resource_group': resource_group,
                'analysis': network_analysis,
                'recommendations': recommendations,
                'potential_savings': savings,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing network in {resource_group}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def optimize_subscription(self) -> Dict:
        """
        Analyze and optimize network resources across the subscription.
        """
        try:
            # Get all resource groups
            resource_groups = self.analyzer.network_client.resource_groups.list()
            
            results = []
            total_savings = {
                'monthly': 0,
                'annual': 0,
                'one_time': 0,
                'by_category': {
                    'public_ip': 0,
                    'load_balancer': 0,
                    'bandwidth': 0,
                    'other': 0
                }
            }

            for rg in resource_groups:
                result = self.optimize_network(rg.name)
                results.append(result)
                
                if result['status'] == 'success':
                    savings = result['potential_savings']
                    total_savings['monthly'] += savings['monthly_savings']
                    total_savings['annual'] += savings['annual_savings']
                    total_savings['one_time'] += savings['one_time_savings']
                    
                    # Aggregate category-wise savings
                    for category, amount in savings['breakdown'].items():
                        total_savings['by_category'][category] += amount

            return {
                'status': 'success',
                'subscription_id': self.subscription_id,
                'resource_group_count': len(results),
                'results': results,
                'total_potential_savings': total_savings,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing subscription network resources: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_optimization_summary(self, result: Dict) -> Dict:
        """
        Generate a summary of network optimization findings.
        """
        try:
            if result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': 'Cannot generate summary from failed optimization'
                }

            summary = {
                'resource_groups_analyzed': 0,
                'total_recommendations': 0,
                'recommendation_types': {},
                'potential_savings': {
                    'monthly': 0,
                    'annual': 0,
                    'one_time': 0,
                    'by_category': {
                        'public_ip': 0,
                        'load_balancer': 0,
                        'bandwidth': 0,
                        'other': 0
                    }
                },
                'high_impact_recommendations': [],
                'quick_wins': [],
                'resource_stats': {
                    'public_ips': 0,
                    'load_balancers': 0,
                    'vnets': 0
                }
            }

            # Process results recursively
            self._process_optimization_results(result, summary)

            return summary

        except Exception as e:
            logger.error(f"Error generating optimization summary: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _process_optimization_results(self, result: Dict, summary: Dict) -> None:
        """
        Recursively process optimization results to build summary.
        """
        if 'results' in result:
            # Process nested results
            for nested_result in result['results']:
                self._process_optimization_results(nested_result, summary)
        else:
            # Process individual resource group result
            summary['resource_groups_analyzed'] += 1
            
            if result.get('recommendations'):
                summary['total_recommendations'] += len(result['recommendations'])
                
                # Process recommendation types
                for rec in result['recommendations']:
                    rec_type = rec['type']
                    if rec_type not in summary['recommendation_types']:
                        summary['recommendation_types'][rec_type] = 0
                    summary['recommendation_types'][rec_type] += 1
                    
                    # Track high impact recommendations
                    if rec.get('impact') == 'high':
                        summary['high_impact_recommendations'].append({
                            'resource_group': result['resource_group'],
                            'type': rec_type,
                            'description': rec['description'],
                            'estimated_savings': rec.get('details', {}).get('estimated_savings', 'N/A')
                        })
                    
                    # Track quick wins (low risk, medium-high impact)
                    if rec.get('implementation_risk') == 'low' and rec.get('impact') in ['medium', 'high']:
                        summary['quick_wins'].append({
                            'resource_group': result['resource_group'],
                            'type': rec_type,
                            'description': rec['description'],
                            'estimated_savings': rec.get('details', {}).get('estimated_savings', 'N/A')
                        })
            
            # Add up potential savings
            if 'potential_savings' in result:
                savings = result['potential_savings']
                summary['potential_savings']['monthly'] += savings['monthly_savings']
                summary['potential_savings']['annual'] += savings['annual_savings']
                summary['potential_savings']['one_time'] += savings['one_time_savings']
                
                for category, amount in savings['breakdown'].items():
                    summary['potential_savings']['by_category'][category] += amount
            
            # Collect resource stats
            if 'analysis' in result:
                analysis = result['analysis']
                if 'public_ips' in analysis:
                    summary['resource_stats']['public_ips'] += analysis['public_ips']['total_count']
                if 'load_balancers' in analysis:
                    summary['resource_stats']['load_balancers'] += analysis['load_balancers']['total_count']
                if 'virtual_networks' in analysis:
                    summary['resource_stats']['vnets'] += analysis['virtual_networks']['total_count']
