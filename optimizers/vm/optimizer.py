from typing import Dict, List
import logging
from .analyzer import VMAnalyzer
from .recommendations import VMOptimizationRecommender
from datetime import datetime

logger = logging.getLogger(__name__)

class VMOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = VMAnalyzer(subscription_id)
        self.recommender = VMOptimizationRecommender()

    def optimize_vm(self, resource_group: str, vm_name: str) -> Dict:
        """
        Analyze and optimize a single VM.
        """
        try:
            # Get VM analysis
            vm_analysis = self.analyzer.analyze_vm_usage(vm_name, resource_group)
            if not vm_analysis:
                return {
                    'status': 'error',
                    'message': f'Failed to analyze VM {vm_name}',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Get recommendations
            recommendations = self.recommender.get_size_recommendations(vm_analysis)

            # Calculate potential savings
            total_savings = self._calculate_total_savings(recommendations)

            return {
                'status': 'success',
                'vm_name': vm_name,
                'resource_group': resource_group,
                'analysis': vm_analysis,
                'recommendations': recommendations,
                'potential_savings': total_savings,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing VM {vm_name}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def optimize_resource_group(self, resource_group: str) -> List[Dict]:
        """
        Analyze and optimize all VMs in a resource group.
        """
        try:
            # Get all VMs in the resource group
            vms = self.analyzer.compute_client.virtual_machines.list(resource_group)
            
            results = []
            for vm in vms:
                result = self.optimize_vm(resource_group, vm.name)
                results.append(result)

            return {
                'status': 'success',
                'resource_group': resource_group,
                'vm_count': len(results),
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing resource group {resource_group}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def optimize_subscription(self) -> Dict:
        """
        Analyze and optimize all VMs in the subscription.
        """
        try:
            # Get all resource groups
            resource_groups = self.analyzer.resource_client.resource_groups.list()
            
            results = []
            for rg in resource_groups:
                result = self.optimize_resource_group(rg.name)
                results.append(result)

            return {
                'status': 'success',
                'subscription_id': self.subscription_id,
                'resource_group_count': len(results),
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing subscription: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _calculate_total_savings(self, recommendations: List[Dict]) -> Dict:
        """
        Calculate total potential savings from all recommendations.
        """
        try:
            monthly_savings = 0
            annual_savings = 0

            for rec in recommendations:
                if 'estimated_savings' in rec:
                    savings = self.recommender.calculate_savings(
                        rec.get('current_size', ''),
                        rec
                    )
                    if savings:
                        monthly_savings += savings['estimated_monthly_savings']
                        annual_savings += savings['estimated_annual_savings']

            return {
                'monthly_savings': monthly_savings,
                'annual_savings': annual_savings,
                'currency': 'USD'
            }

        except Exception as e:
            logger.error(f"Error calculating total savings: {str(e)}")
            return {
                'monthly_savings': 0,
                'annual_savings': 0,
                'currency': 'USD'
            }
