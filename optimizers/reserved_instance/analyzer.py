from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.reservations import AzureReservationAPI
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class ReservedInstanceAnalyzer:
    def __init__(self, subscription_id: str):
        self.credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.reservation_client = AzureReservationAPI(self.credential)
        self.consumption_client = ConsumptionManagementClient(self.credential, self.subscription_id)

        # RI term options and their discounts (example values)
        self.ri_terms = {
            '1_year': {
                'discount': 0.40,  # 40% discount
                'upfront_discount': 0.45  # 45% discount with upfront payment
            },
            '3_year': {
                'discount': 0.60,  # 60% discount
                'upfront_discount': 0.65  # 65% discount with upfront payment
            }
        }

    def analyze_vm_usage(self, resource_group: str = None) -> Dict:
        """Analyze VM usage patterns for RI opportunities."""
        try:
            # Get VM usage data
            vms = self._get_vms(resource_group)
            usage_data = self._get_usage_data()
            
            # Analyze each VM
            vm_analysis = []
            for vm in vms:
                analysis = self._analyze_single_vm(vm, usage_data)
                if analysis:
                    vm_analysis.append(analysis)

            return {
                'vm_count': len(vm_analysis),
                'analysis': vm_analysis,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing VM usage: {str(e)}")
            return None

    def _get_vms(self, resource_group: str = None) -> List:
        """Get list of VMs to analyze."""
        try:
            if resource_group:
                return list(self.compute_client.virtual_machines.list(resource_group))
            return list(self.compute_client.virtual_machines.list_all())

        except Exception as e:
            logger.error(f"Error getting VMs: {str(e)}")
            return []

    def _get_usage_data(self) -> Dict:
        """Get usage data for the past 90 days."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=90)

            # Get consumption data
            usage = self.consumption_client.usage_details.list(
                scope=f'/subscriptions/{self.subscription_id}',
                expand='properties',
                filter=f"properties/usageStart ge '{start_time.strftime('%Y-%m-%d')}' and properties/usageEnd le '{end_time.strftime('%Y-%m-%d')}'"
            )

            usage_data = {}
            for item in usage:
                if item.instance_id:
                    if item.instance_id not in usage_data:
                        usage_data[item.instance_id] = []
                    usage_data[item.instance_id].append({
                        'date': item.usage_start,
                        'quantity': item.quantity,
                        'cost': item.cost
                    })

            return usage_data

        except Exception as e:
            logger.error(f"Error getting usage data: {str(e)}")
            return {}

    def _analyze_single_vm(self, vm, usage_data: Dict) -> Dict:
        """Analyze usage patterns for a single VM."""
        try:
            vm_id = vm.id.lower()
            usage = usage_data.get(vm_id, [])

            if not usage:
                return None

            # Convert usage data to pandas DataFrame for analysis
            df = pd.DataFrame(usage)
            
            # Calculate key metrics
            daily_hours = df.groupby(df['date'].dt.date)['quantity'].sum()
            
            analysis = {
                'vm_name': vm.name,
                'vm_size': vm.hardware_profile.vm_size,
                'resource_group': vm.id.split('/')[4],
                'usage_metrics': {
                    'average_daily_hours': daily_hours.mean(),
                    'usage_consistency': self._calculate_usage_consistency(daily_hours),
                    'total_cost_90_days': df['cost'].sum(),
                    'weekday_usage': self._analyze_weekday_usage(df),
                    'hourly_pattern': self._analyze_hourly_pattern(df)
                }
            }

            # Add RI suitability score
            analysis['ri_suitability'] = self._calculate_ri_suitability(analysis['usage_metrics'])

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing VM {vm.name}: {str(e)}")
            return None

    def _calculate_usage_consistency(self, daily_hours: pd.Series) -> float:
        """Calculate how consistent the VM usage is."""
        try:
            # Calculate coefficient of variation (lower is more consistent)
            cv = daily_hours.std() / daily_hours.mean() if daily_hours.mean() > 0 else float('inf')
            
            # Convert to a 0-1 score (1 is most consistent)
            consistency = 1 / (1 + cv)
            
            return round(consistency, 2)

        except Exception as e:
            logger.error(f"Error calculating usage consistency: {str(e)}")
            return 0.0

    def _analyze_weekday_usage(self, df: pd.DataFrame) -> Dict:
        """Analyze usage patterns by day of week."""
        try:
            weekday_usage = df.groupby(df['date'].dt.dayofweek)['quantity'].mean()
            
            return {
                'weekday_avg': weekday_usage[0:5].mean(),
                'weekend_avg': weekday_usage[5:7].mean(),
                'pattern': 'consistent' if abs(weekday_usage[0:5].mean() - weekday_usage[5:7].mean()) < 2 else 'weekday_heavy'
            }

        except Exception as e:
            logger.error(f"Error analyzing weekday usage: {str(e)}")
            return {
                'weekday_avg': 0,
                'weekend_avg': 0,
                'pattern': 'unknown'
            }

    def _analyze_hourly_pattern(self, df: pd.DataFrame) -> Dict:
        """Analyze usage patterns by hour of day."""
        try:
            hourly_usage = df.groupby(df['date'].dt.hour)['quantity'].mean()
            
            business_hours = hourly_usage[9:17].mean()  # 9 AM to 5 PM
            non_business_hours = pd.concat([hourly_usage[0:9], hourly_usage[17:24]]).mean()
            
            return {
                'business_hours_avg': business_hours,
                'non_business_hours_avg': non_business_hours,
                'pattern': 'business_hours' if business_hours > non_business_hours * 1.5 else 'consistent'
            }

        except Exception as e:
            logger.error(f"Error analyzing hourly pattern: {str(e)}")
            return {
                'business_hours_avg': 0,
                'non_business_hours_avg': 0,
                'pattern': 'unknown'
            }

    def _calculate_ri_suitability(self, metrics: Dict) -> Dict:
        """Calculate RI suitability score and recommended term."""
        try:
            # Base score factors
            consistency_weight = 0.4
            usage_hours_weight = 0.3
            pattern_weight = 0.3

            # Calculate component scores
            consistency_score = metrics['usage_consistency']
            
            usage_hours_score = min(metrics['average_daily_hours'] / 24.0, 1.0)
            
            pattern_score = 1.0
            if metrics['weekday_usage']['pattern'] == 'weekday_heavy':
                pattern_score *= 0.7
            if metrics['hourly_pattern']['pattern'] == 'business_hours':
                pattern_score *= 0.8

            # Calculate final score
            final_score = (
                consistency_score * consistency_weight +
                usage_hours_score * usage_hours_weight +
                pattern_score * pattern_weight
            )

            # Determine recommended term
            if final_score >= 0.8:
                recommended_term = '3_year'
            elif final_score >= 0.6:
                recommended_term = '1_year'
            else:
                recommended_term = None

            return {
                'score': round(final_score, 2),
                'recommended_term': recommended_term,
                'components': {
                    'consistency_score': round(consistency_score, 2),
                    'usage_hours_score': round(usage_hours_score, 2),
                    'pattern_score': round(pattern_score, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error calculating RI suitability: {str(e)}")
            return {
                'score': 0,
                'recommended_term': None,
                'components': {
                    'consistency_score': 0,
                    'usage_hours_score': 0,
                    'pattern_score': 0
                }
            }

    def get_existing_reservations(self) -> List[Dict]:
        """Get existing reserved instances."""
        try:
            reservations = self.reservation_client.reservation_order.list()
            
            processed_reservations = []
            for res in reservations:
                processed_reservations.append({
                    'name': res.display_name,
                    'term': res.term,
                    'scope': res.scope,
                    'quantity': res.quantity,
                    'sku': res.sku,
                    'expiration_date': res.expiry_date,
                    'utilization': self._get_reservation_utilization(res.name)
                })

            return processed_reservations

        except Exception as e:
            logger.error(f"Error getting existing reservations: {str(e)}")
            return []

    def _get_reservation_utilization(self, reservation_id: str) -> Dict:
        """Get utilization metrics for a reservation."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)

            utilization = self.reservation_client.reservation.get_reservation_utilization(
                reservation_id=reservation_id,
                filter=f"properties/usageDate ge '{start_time.strftime('%Y-%m-%d')}' and properties/usageDate le '{end_time.strftime('%Y-%m-%d')}'"
            )

            total_hours = 0
            used_hours = 0
            for util in utilization:
                total_hours += util.total_reserved_quantity
                used_hours += util.in_use_quantity

            return {
                'utilization_rate': round(used_hours / total_hours if total_hours > 0 else 0, 2),
                'total_hours': total_hours,
                'used_hours': used_hours
            }

        except Exception as e:
            logger.error(f"Error getting reservation utilization: {str(e)}")
            return {
                'utilization_rate': 0,
                'total_hours': 0,
                'used_hours': 0
            }
