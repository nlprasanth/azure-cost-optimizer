from typing import Dict, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StorageOptimizationRecommender:
    def __init__(self):
        # Storage tier thresholds (in days)
        self.tier_thresholds = {
            'hot_to_cool': 30,      # Move to Cool if not accessed in 30 days
            'cool_to_archive': 180,  # Move to Archive if not accessed in 180 days
        }

        # Storage tier pricing (example values per GB per month)
        self.tier_pricing = {
            'Premium': 0.15,
            'Hot': 0.0184,
            'Cool': 0.01,
            'Archive': 0.00099
        }

    def get_recommendations(self, storage_analysis: Dict) -> List[Dict]:
        """Generate storage optimization recommendations."""
        try:
            recommendations = []

            # Get basic storage info
            metrics = storage_analysis.get('metrics', {})
            blob_analytics = storage_analysis.get('blob_analytics', {})
            current_tier = storage_analysis.get('current_tier')

            # Tier optimization recommendations
            tier_recs = self._get_tier_recommendations(blob_analytics, current_tier)
            recommendations.extend(tier_recs)

            # Lifecycle policy recommendations
            lifecycle_recs = self._get_lifecycle_recommendations(blob_analytics)
            recommendations.extend(lifecycle_recs)

            # Redundancy recommendations
            redundancy_recs = self._get_redundancy_recommendations(storage_analysis)
            recommendations.extend(redundancy_recs)

            # Capacity optimization recommendations
            capacity_recs = self._get_capacity_recommendations(metrics)
            recommendations.extend(capacity_recs)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating storage recommendations: {str(e)}")
            return []

    def _get_tier_recommendations(self, blob_analytics: Dict, current_tier: str) -> List[Dict]:
        """Generate storage tier optimization recommendations."""
        try:
            recommendations = []
            
            if not blob_analytics or 'containers' not in blob_analytics:
                return recommendations

            total_size = 0
            cool_candidate_size = 0
            archive_candidate_size = 0

            for container in blob_analytics['containers']:
                total_size += container['total_size']
                last_modified = container['last_modified_distribution']
                
                # Calculate sizes for different age brackets
                cool_candidate_size += (last_modified['last_month'] + 
                                     last_modified['last_year'] + 
                                     last_modified['older'])
                
                archive_candidate_size += (last_modified['last_year'] + 
                                        last_modified['older'])

            # Generate tier recommendations
            if current_tier == 'Hot' and cool_candidate_size > 0.5 * total_size:
                recommendations.append({
                    'type': 'storage_tier',
                    'action': 'move_to_cool',
                    'impact': 'medium',
                    'description': f'Move {cool_candidate_size//(1024*1024*1024)}GB of infrequently accessed data to Cool tier',
                    'estimated_savings': f'{(cool_candidate_size//(1024*1024*1024)) * (self.tier_pricing["Hot"] - self.tier_pricing["Cool"]):.2f} USD/month',
                    'implementation_risk': 'low'
                })

            if current_tier in ['Hot', 'Cool'] and archive_candidate_size > 0.3 * total_size:
                recommendations.append({
                    'type': 'storage_tier',
                    'action': 'move_to_archive',
                    'impact': 'high',
                    'description': f'Move {archive_candidate_size//(1024*1024*1024)}GB of rarely accessed data to Archive tier',
                    'estimated_savings': f'{(archive_candidate_size//(1024*1024*1024)) * (self.tier_pricing["Hot"] - self.tier_pricing["Archive"]):.2f} USD/month',
                    'implementation_risk': 'medium'
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating tier recommendations: {str(e)}")
            return []

    def _get_lifecycle_recommendations(self, blob_analytics: Dict) -> List[Dict]:
        """Generate lifecycle management recommendations."""
        try:
            recommendations = []

            if not blob_analytics or 'containers' not in blob_analytics:
                return recommendations

            for container in blob_analytics['containers']:
                last_modified = container['last_modified_distribution']
                
                # Check if container needs lifecycle policy
                if (last_modified['last_year'] + last_modified['older']) > 0.3 * container['blob_count']:
                    recommendations.append({
                        'type': 'lifecycle_policy',
                        'action': 'implement_lifecycle',
                        'impact': 'high',
                        'description': f'Implement lifecycle policy for container {container["name"]}',
                        'details': {
                            'move_to_cool': f'After {self.tier_thresholds["hot_to_cool"]} days',
                            'move_to_archive': f'After {self.tier_thresholds["cool_to_archive"]} days'
                        },
                        'implementation_risk': 'low'
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating lifecycle recommendations: {str(e)}")
            return []

    def _get_redundancy_recommendations(self, storage_analysis: Dict) -> List[Dict]:
        """Generate redundancy optimization recommendations."""
        try:
            recommendations = []
            current_replication = storage_analysis.get('current_replication', '')
            access_patterns = storage_analysis.get('access_patterns', {})

            # Check if current redundancy level might be excessive
            if current_replication == 'GRS' and not self._needs_geo_redundancy(access_patterns):
                recommendations.append({
                    'type': 'redundancy',
                    'action': 'reduce_redundancy',
                    'impact': 'medium',
                    'description': 'Consider switching from GRS to LRS for non-critical data',
                    'estimated_savings': '~40% on storage costs',
                    'implementation_risk': 'medium'
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating redundancy recommendations: {str(e)}")
            return []

    def _get_capacity_recommendations(self, metrics: Dict) -> List[Dict]:
        """Generate capacity optimization recommendations."""
        try:
            recommendations = []
            
            if not metrics or 'used_capacity' not in metrics:
                return recommendations

            capacity_trend = metrics['used_capacity'].get('trend', 'stable')
            
            if capacity_trend == 'increasing':
                recommendations.append({
                    'type': 'capacity',
                    'action': 'optimize_capacity',
                    'impact': 'medium',
                    'description': 'Implement data retention policies to manage growing storage usage',
                    'details': {
                        'current_trend': 'Increasing',
                        'suggested_actions': [
                            'Implement retention policies',
                            'Clean up temporary data',
                            'Archive old data'
                        ]
                    },
                    'implementation_risk': 'low'
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating capacity recommendations: {str(e)}")
            return []

    def _needs_geo_redundancy(self, access_patterns: Dict) -> bool:
        """Determine if geo-redundancy is needed based on access patterns."""
        # This would typically involve more complex analysis
        # For now, using a simple heuristic
        return False

    def calculate_savings(self, storage_analysis: Dict, recommendations: List[Dict]) -> Dict:
        """Calculate potential savings from recommendations."""
        try:
            monthly_savings = 0
            implementation_costs = 0

            for rec in recommendations:
                if rec['type'] == 'storage_tier':
                    # Extract numeric value from estimated_savings string
                    savings_str = rec['estimated_savings'].split()[0]
                    monthly_savings += float(savings_str)
                elif rec['type'] == 'redundancy':
                    # Estimate redundancy savings
                    current_size = storage_analysis['metrics']['used_capacity']['total']
                    monthly_savings += current_size * 0.4  # 40% savings estimate

            return {
                'monthly_savings': monthly_savings,
                'annual_savings': monthly_savings * 12,
                'implementation_costs': implementation_costs,
                'payback_period_months': implementation_costs / monthly_savings if monthly_savings > 0 else 0,
                'currency': 'USD'
            }

        except Exception as e:
            logger.error(f"Error calculating savings: {str(e)}")
            return {
                'monthly_savings': 0,
                'annual_savings': 0,
                'implementation_costs': 0,
                'payback_period_months': 0,
                'currency': 'USD'
            }
