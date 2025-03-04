from typing import Dict, List
import logging
from datetime import datetime
from .analyzer import StorageAnalyzer
from .recommendations import StorageOptimizationRecommender

logger = logging.getLogger(__name__)

class StorageOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = StorageAnalyzer(subscription_id)
        self.recommender = StorageOptimizationRecommender()

    def optimize_storage_account(self, resource_group: str, account_name: str) -> Dict:
        """
        Analyze and optimize a single storage account.
        """
        try:
            # Get storage analysis
            storage_analysis = self.analyzer.analyze_storage_account(
                resource_group,
                account_name
            )
            
            if not storage_analysis:
                return {
                    'status': 'error',
                    'message': f'Failed to analyze storage account {account_name}',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Get recommendations
            recommendations = self.recommender.get_recommendations(storage_analysis)

            # Calculate potential savings
            savings = self.recommender.calculate_savings(storage_analysis, recommendations)

            return {
                'status': 'success',
                'account_name': account_name,
                'resource_group': resource_group,
                'analysis': storage_analysis,
                'recommendations': recommendations,
                'potential_savings': savings,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing storage account {account_name}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def optimize_resource_group(self, resource_group: str) -> Dict:
        """
        Analyze and optimize all storage accounts in a resource group.
        """
        try:
            # Get all storage accounts in the resource group
            storage_accounts = self.analyzer.storage_client.storage_accounts.list_by_resource_group(
                resource_group
            )
            
            results = []
            total_savings = {
                'monthly': 0,
                'annual': 0
            }

            for account in storage_accounts:
                result = self.optimize_storage_account(resource_group, account.name)
                results.append(result)
                
                if result['status'] == 'success':
                    total_savings['monthly'] += result['potential_savings']['monthly_savings']
                    total_savings['annual'] += result['potential_savings']['annual_savings']

            return {
                'status': 'success',
                'resource_group': resource_group,
                'account_count': len(results),
                'results': results,
                'total_potential_savings': total_savings,
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
        Analyze and optimize all storage accounts in the subscription.
        """
        try:
            # Get all resource groups
            resource_groups = self.analyzer.storage_client.resource_groups.list()
            
            results = []
            total_savings = {
                'monthly': 0,
                'annual': 0
            }

            for rg in resource_groups:
                result = self.optimize_resource_group(rg.name)
                results.append(result)
                
                if result['status'] == 'success':
                    total_savings['monthly'] += result['total_potential_savings']['monthly']
                    total_savings['annual'] += result['total_potential_savings']['annual']

            return {
                'status': 'success',
                'subscription_id': self.subscription_id,
                'resource_group_count': len(results),
                'results': results,
                'total_potential_savings': total_savings,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing subscription: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_optimization_summary(self, result: Dict) -> Dict:
        """
        Generate a summary of optimization findings.
        """
        try:
            if result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': 'Cannot generate summary from failed optimization'
                }

            summary = {
                'total_accounts_analyzed': 0,
                'accounts_with_recommendations': 0,
                'total_recommendations': 0,
                'recommendation_types': {},
                'potential_savings': {
                    'monthly': 0,
                    'annual': 0,
                    'currency': 'USD'
                },
                'high_impact_recommendations': []
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
            # Process individual account result
            summary['total_accounts_analyzed'] += 1
            
            if result.get('recommendations'):
                summary['accounts_with_recommendations'] += 1
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
                            'account': result['account_name'],
                            'type': rec_type,
                            'description': rec['description'],
                            'estimated_savings': rec.get('estimated_savings', 'N/A')
                        })
            
            # Add up potential savings
            if 'potential_savings' in result:
                summary['potential_savings']['monthly'] += result['potential_savings'].get('monthly_savings', 0)
                summary['potential_savings']['annual'] += result['potential_savings'].get('annual_savings', 0)
