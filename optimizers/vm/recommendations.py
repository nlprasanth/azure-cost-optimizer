from typing import Dict, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class VMOptimizationRecommender:
    def __init__(self):
        # VM size categories and their typical use cases
        self.vm_categories = {
            'compute_optimized': ['F2s_v2', 'F4s_v2', 'F8s_v2', 'F16s_v2'],
            'memory_optimized': ['E2s_v3', 'E4s_v3', 'E8s_v3', 'E16s_v3'],
            'general_purpose': ['D2s_v3', 'D4s_v3', 'D8s_v3', 'D16s_v3'],
            'burstable': ['B1s', 'B2s', 'B2ms', 'B4ms']
        }

        # Cost ratios for different commitment terms (example values)
        self.commitment_savings = {
            'pay_as_you_go': 1.0,
            'reserved_1_year': 0.6,  # 40% savings
            'reserved_3_year': 0.4,  # 60% savings
            'spot': 0.2,             # 80% savings
        }

    def get_size_recommendations(self, vm_analysis: Dict) -> List[Dict]:
        """Generate size recommendations based on VM analysis."""
        try:
            recommendations = []
            metrics = vm_analysis['metrics']
            current_size = vm_analysis['vm_size']

            # Analyze CPU utilization
            cpu_metrics = metrics['cpu']
            memory_metrics = metrics['memory']

            # Right-sizing recommendations
            size_rec = self._get_size_recommendation(cpu_metrics, memory_metrics, current_size)
            if size_rec:
                recommendations.append(size_rec)

            # Commitment recommendations
            commit_rec = self._get_commitment_recommendation(cpu_metrics, memory_metrics)
            if commit_rec:
                recommendations.append(commit_rec)

            # Schedule recommendations
            schedule_rec = self._get_schedule_recommendation(cpu_metrics)
            if schedule_rec:
                recommendations.append(schedule_rec)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _get_size_recommendation(self, cpu_metrics: Dict, memory_metrics: Dict, current_size: str) -> Dict:
        """Determine if VM should be resized based on utilization patterns."""
        try:
            cpu_avg = cpu_metrics['average']
            cpu_peak = cpu_metrics['peak']
            memory_avg = memory_metrics['average']
            memory_peak = memory_metrics['peak']

            # Define utilization thresholds
            LOW_UTIL = 20
            MEDIUM_UTIL = 40
            HIGH_UTIL = 80

            if cpu_avg < LOW_UTIL and memory_avg < LOW_UTIL:
                # Significant underutilization
                if current_size.startswith(('D', 'E', 'F')):
                    return {
                        'type': 'rightsizing',
                        'action': 'downsize',
                        'current_size': current_size,
                        'recommended_size': self._get_smaller_size(current_size),
                        'reason': f'Low utilization (CPU: {cpu_avg:.1f}%, Memory: {memory_avg:.1f}%)',
                        'estimated_savings': '40-60%',
                        'priority': 'high',
                        'implementation_risk': 'low'
                    }
            elif cpu_avg > HIGH_UTIL or memory_avg > HIGH_UTIL:
                # Resource constraint
                return {
                    'type': 'rightsizing',
                    'action': 'upsize',
                    'current_size': current_size,
                    'recommended_size': self._get_larger_size(current_size),
                    'reason': f'High utilization (CPU: {cpu_avg:.1f}%, Memory: {memory_avg:.1f}%)',
                    'estimated_savings': 'performance improvement',
                    'priority': 'high',
                    'implementation_risk': 'medium'
                }

            return None

        except Exception as e:
            logger.error(f"Error in size recommendation: {str(e)}")
            return None

    def _get_commitment_recommendation(self, cpu_metrics: Dict, memory_metrics: Dict) -> Dict:
        """Determine if VM is suitable for reserved instances or spot instances."""
        try:
            cpu_avg = cpu_metrics['average']
            cpu_std = cpu_metrics['std_dev']
            
            # Reserved Instance criteria
            if cpu_avg > 40 and cpu_std < 15:
                return {
                    'type': 'commitment',
                    'action': 'reserved_instance',
                    'term': '1_year' if cpu_avg < 60 else '3_year',
                    'reason': f'Stable utilization pattern (CPU avg: {cpu_avg:.1f}%, STD: {cpu_std:.1f}%)',
                    'estimated_savings': '40-60%',
                    'priority': 'medium',
                    'implementation_risk': 'low'
                }
            
            # Spot Instance criteria
            if cpu_avg < 60 and cpu_std < 20:
                return {
                    'type': 'commitment',
                    'action': 'spot_instance',
                    'reason': f'Suitable for interruption (CPU avg: {cpu_avg:.1f}%, STD: {cpu_std:.1f}%)',
                    'estimated_savings': '60-80%',
                    'priority': 'medium',
                    'implementation_risk': 'medium'
                }

            return None

        except Exception as e:
            logger.error(f"Error in commitment recommendation: {str(e)}")
            return None

    def _get_schedule_recommendation(self, cpu_metrics: Dict) -> Dict:
        """Determine if VM should be scheduled for start/stop."""
        try:
            # This would typically analyze hourly/daily patterns
            # Placeholder implementation
            return {
                'type': 'scheduling',
                'action': 'auto_shutdown',
                'schedule': '7pm-7am',
                'reason': 'Low utilization during non-business hours',
                'estimated_savings': '30-40%',
                'priority': 'medium',
                'implementation_risk': 'low'
            }

        except Exception as e:
            logger.error(f"Error in schedule recommendation: {str(e)}")
            return None

    def _get_smaller_size(self, current_size: str) -> str:
        """Get next smaller VM size."""
        # Simplified implementation - would need complete VM size mapping
        size_mapping = {
            'Standard_D4s_v3': 'Standard_D2s_v3',
            'Standard_D8s_v3': 'Standard_D4s_v3',
            'Standard_D16s_v3': 'Standard_D8s_v3'
        }
        return size_mapping.get(current_size, current_size)

    def _get_larger_size(self, current_size: str) -> str:
        """Get next larger VM size."""
        # Simplified implementation - would need complete VM size mapping
        size_mapping = {
            'Standard_D2s_v3': 'Standard_D4s_v3',
            'Standard_D4s_v3': 'Standard_D8s_v3',
            'Standard_D8s_v3': 'Standard_D16s_v3'
        }
        return size_mapping.get(current_size, current_size)

    def calculate_savings(self, current_size: str, recommended_action: Dict) -> Dict:
        """Calculate potential savings for a recommendation."""
        try:
            # This would typically call Azure Retail Prices API
            # Placeholder implementation
            base_cost = 100  # Example monthly cost
            
            if recommended_action['type'] == 'rightsizing':
                savings_percent = 0.4  # 40% savings for downsizing
            elif recommended_action['type'] == 'commitment':
                if recommended_action['action'] == 'reserved_instance':
                    savings_percent = 0.6  # 60% savings for RI
                else:  # spot instance
                    savings_percent = 0.8  # 80% savings for spot
            else:  # scheduling
                savings_percent = 0.3  # 30% savings for scheduling

            monthly_savings = base_cost * savings_percent
            annual_savings = monthly_savings * 12

            return {
                'current_monthly_cost': base_cost,
                'estimated_monthly_savings': monthly_savings,
                'estimated_annual_savings': annual_savings,
                'savings_percentage': savings_percent * 100
            }

        except Exception as e:
            logger.error(f"Error calculating savings: {str(e)}")
            return None
