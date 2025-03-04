from typing import Dict, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RIRecommendationEngine:
    def __init__(self):
        # Standard RI discounts (example values)
        self.ri_discounts = {
            '1_year': {
                'standard': 0.40,  # 40% discount
                'upfront': 0.45    # 45% discount with upfront payment
            },
            '3_year': {
                'standard': 0.60,  # 60% discount
                'upfront': 0.65    # 65% discount with upfront payment
            }
        }

    def generate_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Generate RI recommendations based on analysis results."""
        try:
            recommendations = []
            
            for vm in analysis_results['analysis']:
                if self._should_recommend_ri(vm):
                    recommendation = self._create_ri_recommendation(vm)
                    if recommendation:
                        recommendations.append(recommendation)

            # Add summary recommendation
            if recommendations:
                summary = self._create_summary_recommendation(recommendations)
                recommendations.append(summary)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating RI recommendations: {str(e)}")
            return []

    def _should_recommend_ri(self, vm_analysis: Dict) -> bool:
        """Determine if RI should be recommended for a VM."""
        try:
            suitability = vm_analysis['ri_suitability']
            
            # Basic criteria for RI recommendation
            return (
                suitability['score'] >= 0.6 and  # Good suitability score
                vm_analysis['usage_metrics']['average_daily_hours'] >= 12 and  # At least 12 hours daily usage
                vm_analysis['usage_metrics']['usage_consistency'] >= 0.7  # Consistent usage
            )

        except Exception as e:
            logger.error(f"Error checking RI recommendation criteria: {str(e)}")
            return False

    def _create_ri_recommendation(self, vm_analysis: Dict) -> Dict:
        """Create detailed RI recommendation for a VM."""
        try:
            suitability = vm_analysis['ri_suitability']
            usage_metrics = vm_analysis['usage_metrics']
            
            # Get recommended term and calculate savings
            term = suitability['recommended_term']
            if not term:
                return None
                
            # Calculate potential savings
            current_monthly_cost = usage_metrics['total_cost_90_days'] / 3  # Convert 90-day cost to monthly
            
            standard_discount = self.ri_discounts[term]['standard']
            upfront_discount = self.ri_discounts[term]['upfront']
            
            standard_savings = current_monthly_cost * standard_discount
            upfront_savings = current_monthly_cost * upfront_discount

            recommendation = {
                'type': 'vm_specific',
                'vm_name': vm_analysis['vm_name'],
                'vm_size': vm_analysis['vm_size'],
                'resource_group': vm_analysis['resource_group'],
                'confidence_score': suitability['score'],
                'recommended_term': term,
                'current_cost': {
                    'monthly': current_monthly_cost,
                    'annual': current_monthly_cost * 12
                },
                'potential_savings': {
                    'standard': {
                        'monthly': standard_savings,
                        'annual': standard_savings * 12,
                        'term_total': standard_savings * (12 if term == '1_year' else 36)
                    },
                    'upfront': {
                        'monthly': upfront_savings,
                        'annual': upfront_savings * 12,
                        'term_total': upfront_savings * (12 if term == '1_year' else 36)
                    }
                },
                'usage_patterns': {
                    'average_daily_hours': usage_metrics['average_daily_hours'],
                    'consistency': usage_metrics['usage_consistency'],
                    'weekday_pattern': usage_metrics['weekday_usage']['pattern'],
                    'hourly_pattern': usage_metrics['hourly_pattern']['pattern']
                },
                'justification': self._generate_justification(vm_analysis),
                'implementation_steps': self._generate_implementation_steps(vm_analysis),
                'risks': self._assess_risks(vm_analysis)
            }

            return recommendation

        except Exception as e:
            logger.error(f"Error creating RI recommendation: {str(e)}")
            return None

    def _create_summary_recommendation(self, recommendations: List[Dict]) -> Dict:
        """Create a summary recommendation for all VMs."""
        try:
            total_current_monthly = sum(r['current_cost']['monthly'] for r in recommendations if r['type'] == 'vm_specific')
            total_standard_savings = sum(r['potential_savings']['standard']['monthly'] for r in recommendations if r['type'] == 'vm_specific')
            total_upfront_savings = sum(r['potential_savings']['upfront']['monthly'] for r in recommendations if r['type'] == 'vm_specific')

            return {
                'type': 'summary',
                'vm_count': len([r for r in recommendations if r['type'] == 'vm_specific']),
                'total_current_cost': {
                    'monthly': total_current_monthly,
                    'annual': total_current_monthly * 12
                },
                'total_potential_savings': {
                    'standard': {
                        'monthly': total_standard_savings,
                        'annual': total_standard_savings * 12
                    },
                    'upfront': {
                        'monthly': total_upfront_savings,
                        'annual': total_upfront_savings * 12
                    }
                },
                'recommendation_distribution': {
                    '1_year': len([r for r in recommendations if r['type'] == 'vm_specific' and r['recommended_term'] == '1_year']),
                    '3_year': len([r for r in recommendations if r['type'] == 'vm_specific' and r['recommended_term'] == '3_year'])
                },
                'implementation_strategy': self._generate_implementation_strategy(recommendations)
            }

        except Exception as e:
            logger.error(f"Error creating summary recommendation: {str(e)}")
            return None

    def _generate_justification(self, vm_analysis: Dict) -> str:
        """Generate justification for the RI recommendation."""
        try:
            metrics = vm_analysis['usage_metrics']
            suitability = vm_analysis['ri_suitability']
            
            justification = [
                f"VM shows consistent usage (consistency score: {suitability['components']['consistency_score']})",
                f"High average daily utilization ({metrics['average_daily_hours']:.1f} hours/day)",
            ]
            
            if metrics['weekday_usage']['pattern'] == 'consistent':
                justification.append("Consistent usage across weekdays and weekends")
            
            if metrics['hourly_pattern']['pattern'] == 'consistent':
                justification.append("Consistent usage throughout the day")
                
            return " | ".join(justification)

        except Exception as e:
            logger.error(f"Error generating justification: {str(e)}")
            return "Recommendation based on usage analysis"

    def _generate_implementation_steps(self, vm_analysis: Dict) -> List[str]:
        """Generate implementation steps for the RI recommendation."""
        try:
            return [
                f"Review current usage patterns for VM '{vm_analysis['vm_name']}'",
                "Calculate exact RI requirements based on VM size and usage",
                "Select appropriate RI term and payment option",
                "Purchase RI through Azure portal or API",
                "Monitor RI utilization after purchase",
                "Set up alerts for any significant changes in usage patterns"
            ]

        except Exception as e:
            logger.error(f"Error generating implementation steps: {str(e)}")
            return ["Review and purchase appropriate RI through Azure portal"]

    def _assess_risks(self, vm_analysis: Dict) -> List[Dict]:
        """Assess potential risks for the RI recommendation."""
        try:
            risks = []
            metrics = vm_analysis['usage_metrics']
            
            if metrics['weekday_usage']['pattern'] == 'weekday_heavy':
                risks.append({
                    'type': 'usage_pattern',
                    'description': 'Significant difference between weekday and weekend usage',
                    'mitigation': 'Consider shorter term RI or smaller commitment'
                })
                
            if metrics['hourly_pattern']['pattern'] == 'business_hours':
                risks.append({
                    'type': 'usage_pattern',
                    'description': 'Usage primarily during business hours',
                    'mitigation': 'Evaluate start/stop automation for non-business hours'
                })
                
            if metrics['usage_consistency'] < 0.8:
                risks.append({
                    'type': 'consistency',
                    'description': 'Usage patterns show some variability',
                    'mitigation': 'Monitor usage patterns closely before committing to long-term RI'
                })
                
            return risks

        except Exception as e:
            logger.error(f"Error assessing risks: {str(e)}")
            return []

    def _generate_implementation_strategy(self, recommendations: List[Dict]) -> Dict:
        """Generate overall implementation strategy."""
        try:
            vm_recommendations = [r for r in recommendations if r['type'] == 'vm_specific']
            
            # Sort recommendations by confidence score
            sorted_recs = sorted(vm_recommendations, key=lambda x: x['confidence_score'], reverse=True)
            
            # Group by priority
            high_priority = [r for r in sorted_recs if r['confidence_score'] >= 0.8]
            medium_priority = [r for r in sorted_recs if 0.6 <= r['confidence_score'] < 0.8]
            
            return {
                'phases': [
                    {
                        'name': 'Phase 1 - High Confidence RIs',
                        'timeframe': '1-2 weeks',
                        'vm_count': len(high_priority),
                        'description': 'Implement RIs for VMs with highest confidence scores and consistent usage patterns'
                    },
                    {
                        'name': 'Phase 2 - Medium Confidence RIs',
                        'timeframe': '2-4 weeks',
                        'vm_count': len(medium_priority),
                        'description': 'Review and implement RIs for VMs with good but not optimal usage patterns'
                    }
                ],
                'prerequisites': [
                    'Review and validate current VM sizing',
                    'Ensure budget approval for RI commitment',
                    'Set up monitoring for VM usage patterns',
                    'Create process for regular RI utilization review'
                ]
            }

        except Exception as e:
            logger.error(f"Error generating implementation strategy: {str(e)}")
            return {
                'phases': [],
                'prerequisites': []
            }
