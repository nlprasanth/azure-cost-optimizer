from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class VMAnalyzer:
    def __init__(self, subscription_id: str):
        self.credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.monitor_client = MonitorManagementClient(self.credential, self.subscription_id)

        # VM size mappings for easy comparison
        self.size_hierarchy = {
            'Standard_B': 1,  # Burstable
            'Standard_D': 2,  # General purpose
            'Standard_E': 3,  # Memory optimized
            'Standard_F': 4,  # Compute optimized
            'Standard_G': 5,  # Previous gen
            'Standard_M': 6,  # Memory optimized
        }

    def get_vm_metrics(self, vm_id: str, days: int = 30) -> Dict:
        """Get VM performance metrics for analysis."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            timespan = f"{start_time}/{end_time}"
            
            metrics = {
                'cpu': self._get_metric(vm_id, 'Percentage CPU', timespan),
                'memory': self._get_metric(vm_id, 'Available Memory Bytes', timespan),
                'disk_read': self._get_metric(vm_id, 'Disk Read Bytes', timespan),
                'disk_write': self._get_metric(vm_id, 'Disk Write Bytes', timespan),
                'network_in': self._get_metric(vm_id, 'Network In Total', timespan),
                'network_out': self._get_metric(vm_id, 'Network Out Total', timespan)
            }
            
            return self._process_metrics(metrics)
        except Exception as e:
            logger.error(f"Error getting VM metrics: {str(e)}")
            return None

    def _get_metric(self, resource_id: str, metric_name: str, timespan: str) -> List[float]:
        """Get specific metric data for a VM."""
        try:
            metrics_data = self.monitor_client.metrics.list(
                resource_id,
                timespan=timespan,
                interval='PT1H',  # 1-hour intervals
                metricnames=metric_name,
                aggregation='Average'
            )
            
            if metrics_data.value:
                return [point.average for point in metrics_data.value[0].timeseries[0].data if point.average is not None]
            return []
        except Exception as e:
            logger.error(f"Error getting metric {metric_name}: {str(e)}")
            return []

    def _process_metrics(self, metrics: Dict) -> Dict:
        """Process raw metrics into useful statistics."""
        processed = {}
        for metric, values in metrics.items():
            if values:
                df = pd.Series(values)
                processed[metric] = {
                    'average': df.mean(),
                    'peak': df.max(),
                    'p95': df.quantile(0.95),
                    'p99': df.quantile(0.99),
                    'std_dev': df.std()
                }
            else:
                processed[metric] = {
                    'average': 0,
                    'peak': 0,
                    'p95': 0,
                    'p99': 0,
                    'std_dev': 0
                }
        return processed

    def analyze_vm_usage(self, vm_name: str, resource_group: str) -> Dict:
        """Analyze VM usage patterns and identify optimization opportunities."""
        try:
            # Get VM details
            vm = self.compute_client.virtual_machines.get(resource_group, vm_name)
            vm_id = vm.id
            
            # Get VM metrics
            metrics = self.get_vm_metrics(vm_id)
            if not metrics:
                return None
            
            # Analyze usage patterns
            analysis = {
                'vm_name': vm_name,
                'vm_size': vm.hardware_profile.vm_size,
                'metrics': metrics,
                'recommendations': self._generate_recommendations(vm, metrics)
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing VM usage: {str(e)}")
            return None

    def _generate_recommendations(self, vm, metrics: Dict) -> List[Dict]:
        """Generate optimization recommendations based on VM usage patterns."""
        recommendations = []
        
        # CPU utilization analysis
        cpu_avg = metrics['cpu']['average']
        cpu_peak = metrics['cpu']['peak']
        
        if cpu_avg < 20 and cpu_peak < 40:
            recommendations.append({
                'type': 'downsizing',
                'priority': 'high',
                'description': f'VM is significantly underutilized (avg CPU: {cpu_avg:.1f}%). Consider downsizing or using B-series VM.',
                'estimated_savings': '30-50%'
            })
        elif cpu_avg < 40 and cpu_peak < 60:
            recommendations.append({
                'type': 'downsizing',
                'priority': 'medium',
                'description': f'VM is moderately underutilized (avg CPU: {cpu_avg:.1f}%). Consider moving to a smaller instance.',
                'estimated_savings': '20-30%'
            })
        
        # Memory utilization analysis
        memory_avg = metrics['memory']['average']
        if memory_avg > 90:
            recommendations.append({
                'type': 'upsizing',
                'priority': 'high',
                'description': f'High memory utilization (avg: {memory_avg:.1f}%). Consider upgrading to a memory-optimized instance.',
                'estimated_savings': 'performance improvement'
            })
        
        # Analyze for spot instance opportunity
        if cpu_avg < 60 and cpu_peak < 80:
            recommendations.append({
                'type': 'spot_instance',
                'priority': 'medium',
                'description': 'Usage pattern suitable for spot instances. Consider converting to spot VM for significant cost savings.',
                'estimated_savings': '60-80%'
            })
        
        # Reserved Instance analysis
        if cpu_avg > 40 or memory_avg > 40:
            recommendations.append({
                'type': 'reserved_instance',
                'priority': 'medium',
                'description': 'Consistent usage pattern detected. Consider Reserved Instance for 1 or 3 years.',
                'estimated_savings': '40-60%'
            })
        
        return recommendations

    def get_cost_comparison(self, current_size: str, recommended_size: str) -> Dict:
        """Compare costs between current and recommended VM sizes."""
        # This would typically call Azure Retail Prices API or use a pricing database
        # Placeholder implementation
        return {
            'current_cost': 100,  # Example value
            'recommended_cost': 70,  # Example value
            'savings_percentage': 30,
            'monthly_savings': 30
        }
