from typing import Dict, List
import logging
from datetime import datetime
from .analyzer import ReservedInstanceAnalyzer
from .recommendations import RIRecommendationEngine

logger = logging.getLogger(__name__)

class ReservedInstanceOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = ReservedInstanceAnalyzer(subscription_id)
        self.recommender = RIRecommendationEngine()

    def optimize_reserved_instances(self, resource_group: str = None) -> Dict:
        """
        Analyze and optimize Reserved Instance usage.
        """
        try:
            # Get VM usage analysis
            analysis_results = self.analyzer.analyze_vm_usage(resource_group)
            if not analysis_results:
                return {
                    'status': 'error',
                    'message': f'Failed to analyze VM usage in subscription',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Get existing reservations
            existing_reservations = self.analyzer.get_existing_reservations()

            # Generate recommendations
            recommendations = self.recommender.generate_recommendations(analysis_results)

            return {
                'status': 'success',
                'scope': resource_group if resource_group else 'subscription',
                'analysis': analysis_results,
                'existing_reservations': existing_reservations,
                'recommendations': recommendations,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error optimizing reserved instances: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def get_optimization_summary(self, result: Dict) -> Dict:
        """
        Generate a summary of RI optimization findings.
        """
        try:
            if result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': 'Cannot generate summary from failed optimization'
                }

            summary = {
                'vms_analyzed': len(result['analysis']['analysis']),
                'recommendations_count': len([r for r in result['recommendations'] if r['type'] == 'vm_specific']),
                'existing_reservations': len(result['existing_reservations']),
                'potential_savings': self._calculate_total_savings(result['recommendations']),
                'recommendation_breakdown': self._get_recommendation_breakdown(result['recommendations']),
                'existing_ri_metrics': self._analyze_existing_ris(result['existing_reservations']),
                'implementation_timeline': self._generate_timeline(result['recommendations'])
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating optimization summary: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _calculate_total_savings(self, recommendations: List[Dict]) -> Dict:
        """Calculate total potential savings from recommendations."""
        try:
            total_savings = {
                'monthly': {
                    'standard': 0,
                    'upfront': 0
                },
                'annual': {
                    'standard': 0,
                    'upfront': 0
                },
                'three_year': {
                    'standard': 0,
                    'upfront': 0
                }
            }

            for rec in recommendations:
                if rec['type'] == 'vm_specific':
                    savings = rec['potential_savings']
                    total_savings['monthly']['standard'] += savings['standard']['monthly']
                    total_savings['monthly']['upfront'] += savings['upfront']['monthly']
                    total_savings['annual']['standard'] += savings['standard']['annual']
                    total_savings['annual']['upfront'] += savings['upfront']['annual']
                    
                    # Add to three year total if applicable
                    if rec['recommended_term'] == '3_year':
                        total_savings['three_year']['standard'] += savings['standard']['term_total']
                        total_savings['three_year']['upfront'] += savings['upfront']['term_total']

            return total_savings

        except Exception as e:
            logger.error(f"Error calculating total savings: {str(e)}")
            return {
                'monthly': {'standard': 0, 'upfront': 0},
                'annual': {'standard': 0, 'upfront': 0},
                'three_year': {'standard': 0, 'upfront': 0}
            }

    def _get_recommendation_breakdown(self, recommendations: List[Dict]) -> Dict:
        """Get breakdown of recommendations by various factors."""
        try:
            breakdown = {
                'by_term': {
                    '1_year': 0,
                    '3_year': 0
                },
                'by_confidence': {
                    'high': 0,    # score >= 0.8
                    'medium': 0,  # 0.6 <= score < 0.8
                    'low': 0      # score < 0.6
                },
                'by_vm_size': {},
                'by_resource_group': {}
            }

            for rec in recommendations:
                if rec['type'] == 'vm_specific':
                    # Count by term
                    breakdown['by_term'][rec['recommended_term']] += 1
                    
                    # Count by confidence
                    if rec['confidence_score'] >= 0.8:
                        breakdown['by_confidence']['high'] += 1
                    elif rec['confidence_score'] >= 0.6:
                        breakdown['by_confidence']['medium'] += 1
                    else:
                        breakdown['by_confidence']['low'] += 1
                    
                    # Count by VM size
                    vm_size = rec['vm_size']
                    breakdown['by_vm_size'][vm_size] = breakdown['by_vm_size'].get(vm_size, 0) + 1
                    
                    # Count by resource group
                    rg = rec['resource_group']
                    breakdown['by_resource_group'][rg] = breakdown['by_resource_group'].get(rg, 0) + 1

            return breakdown

        except Exception as e:
            logger.error(f"Error getting recommendation breakdown: {str(e)}")
            return {
                'by_term': {'1_year': 0, '3_year': 0},
                'by_confidence': {'high': 0, 'medium': 0, 'low': 0},
                'by_vm_size': {},
                'by_resource_group': {}
            }

    def _analyze_existing_ris(self, reservations: List[Dict]) -> Dict:
        """Analyze metrics for existing RIs."""
        try:
            metrics = {
                'total_count': len(reservations),
                'utilization': {
                    'high': 0,    # >= 80%
                    'medium': 0,  # 50-80%
                    'low': 0      # < 50%
                },
                'expiring_soon': 0,  # within 90 days
                'average_utilization': 0
            }

            if not reservations:
                return metrics

            total_utilization = 0
            for res in reservations:
                util_rate = res['utilization']['utilization_rate']
                total_utilization += util_rate
                
                # Count by utilization level
                if util_rate >= 0.8:
                    metrics['utilization']['high'] += 1
                elif util_rate >= 0.5:
                    metrics['utilization']['medium'] += 1
                else:
                    metrics['utilization']['low'] += 1
                
                # Check if expiring soon
                if (datetime.fromisoformat(res['expiration_date']) - datetime.utcnow()).days <= 90:
                    metrics['expiring_soon'] += 1

            metrics['average_utilization'] = round(total_utilization / len(reservations), 2)
            
            return metrics

        except Exception as e:
            logger.error(f"Error analyzing existing RIs: {str(e)}")
            return {
                'total_count': 0,
                'utilization': {'high': 0, 'medium': 0, 'low': 0},
                'expiring_soon': 0,
                'average_utilization': 0
            }

    def _generate_timeline(self, recommendations: List[Dict]) -> List[Dict]:
        """Generate implementation timeline for recommendations."""
        try:
            # Get implementation strategy from summary recommendation
            summary_rec = next((r for r in recommendations if r['type'] == 'summary'), None)
            if not summary_rec:
                return []

            return summary_rec['implementation_strategy']['phases']

        except Exception as e:
            logger.error(f"Error generating timeline: {str(e)}")
            return []
