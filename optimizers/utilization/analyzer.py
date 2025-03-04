from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class UtilizationAnalyzer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.monitor_client = MonitorManagementClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.storage_client = StorageManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)

        # Define utilization thresholds
        self.thresholds = {
            'vm': {
                'cpu': {'low': 20, 'high': 80},
                'memory': {'low': 30, 'high': 85},
                'disk': {'low': 25, 'high': 85}
            },
            'storage': {
                'blob': {'low': 30, 'high': 80},
                'file': {'low': 30, 'high': 80},
                'table': {'low': 30, 'high': 80}
            },
            'database': {
                'dtu': {'low': 25, 'high': 80},
                'storage': {'low': 30, 'high': 85}
            }
        }

    def analyze_resource_utilization(self, time_range_days: int = 30) -> Dict:
        """Analyze resource utilization across the subscription."""
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=time_range_days)

            # Analyze different resource types
            analysis = {
                'virtual_machines': self._analyze_vm_utilization(start_time, end_time),
                'storage_accounts': self._analyze_storage_utilization(start_time, end_time),
                'network_resources': self._analyze_network_utilization(start_time, end_time),
                'overall_statistics': {},
                'utilization_patterns': {},
                'cost_impact': {}
            }

            # Calculate overall statistics
            analysis['overall_statistics'] = self._calculate_overall_statistics(analysis)
            
            # Analyze utilization patterns
            analysis['utilization_patterns'] = self._analyze_utilization_patterns(analysis)
            
            # Calculate potential cost impact
            analysis['cost_impact'] = self._calculate_cost_impact(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resource utilization: {str(e)}")
            return {}

    def _analyze_vm_utilization(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze Virtual Machine utilization."""
        try:
            vm_analysis = {
                'utilization_metrics': [],
                'underutilized_vms': [],
                'overutilized_vms': [],
                'right_size_candidates': [],
                'stop_candidates': []
            }

            # Get all VMs in subscription
            vms = list(self.compute_client.virtual_machines.list_all())

            for vm in vms:
                metrics = self._get_vm_metrics(vm.id, start_time, end_time)
                
                vm_analysis['utilization_metrics'].append({
                    'vm_id': vm.id,
                    'name': vm.name,
                    'metrics': metrics
                })

                # Analyze metrics against thresholds
                if self._is_underutilized(metrics, self.thresholds['vm']):
                    vm_analysis['underutilized_vms'].append({
                        'vm_id': vm.id,
                        'name': vm.name,
                        'metrics': metrics,
                        'recommendation': self._generate_vm_recommendation(vm, metrics)
                    })
                elif self._is_overutilized(metrics, self.thresholds['vm']):
                    vm_analysis['overutilized_vms'].append({
                        'vm_id': vm.id,
                        'name': vm.name,
                        'metrics': metrics,
                        'recommendation': self._generate_vm_recommendation(vm, metrics)
                    })

                # Check for right-sizing opportunities
                if self._is_rightsizing_candidate(vm, metrics):
                    vm_analysis['right_size_candidates'].append({
                        'vm_id': vm.id,
                        'name': vm.name,
                        'current_size': vm.hardware_profile.vm_size,
                        'recommended_size': self._recommend_vm_size(vm, metrics),
                        'potential_savings': self._calculate_vm_savings(vm, metrics)
                    })

                # Check for stop candidates
                if self._is_stop_candidate(metrics):
                    vm_analysis['stop_candidates'].append({
                        'vm_id': vm.id,
                        'name': vm.name,
                        'last_active': self._get_last_active_time(metrics),
                        'potential_savings': self._calculate_vm_savings(vm, metrics)
                    })

            return vm_analysis

        except Exception as e:
            logger.error(f"Error analyzing VM utilization: {str(e)}")
            return {}

    def _analyze_storage_utilization(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze Storage Account utilization."""
        try:
            storage_analysis = {
                'utilization_metrics': [],
                'underutilized_accounts': [],
                'overutilized_accounts': [],
                'optimization_candidates': [],
                'tier_recommendations': []
            }

            # Get all storage accounts
            storage_accounts = list(self.storage_client.storage_accounts.list())

            for account in storage_accounts:
                metrics = self._get_storage_metrics(account.id, start_time, end_time)
                
                storage_analysis['utilization_metrics'].append({
                    'account_id': account.id,
                    'name': account.name,
                    'metrics': metrics
                })

                # Analyze metrics against thresholds
                if self._is_underutilized(metrics, self.thresholds['storage']):
                    storage_analysis['underutilized_accounts'].append({
                        'account_id': account.id,
                        'name': account.name,
                        'metrics': metrics,
                        'recommendation': self._generate_storage_recommendation(account, metrics)
                    })
                elif self._is_overutilized(metrics, self.thresholds['storage']):
                    storage_analysis['overutilized_accounts'].append({
                        'account_id': account.id,
                        'name': account.name,
                        'metrics': metrics,
                        'recommendation': self._generate_storage_recommendation(account, metrics)
                    })

                # Check for tier optimization opportunities
                tier_recommendation = self._analyze_storage_tier(account, metrics)
                if tier_recommendation:
                    storage_analysis['tier_recommendations'].append(tier_recommendation)

                # Check for optimization candidates
                if self._is_storage_optimization_candidate(account, metrics):
                    storage_analysis['optimization_candidates'].append({
                        'account_id': account.id,
                        'name': account.name,
                        'current_tier': account.sku.tier,
                        'recommended_tier': self._recommend_storage_tier(account, metrics),
                        'potential_savings': self._calculate_storage_savings(account, metrics)
                    })

            return storage_analysis

        except Exception as e:
            logger.error(f"Error analyzing storage utilization: {str(e)}")
            return {}

    def _analyze_network_utilization(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze Network resource utilization."""
        try:
            network_analysis = {
                'utilization_metrics': [],
                'underutilized_resources': [],
                'overutilized_resources': [],
                'optimization_candidates': []
            }

            # Analyze different network resource types
            network_analysis.update(self._analyze_load_balancers(start_time, end_time))
            network_analysis.update(self._analyze_public_ips(start_time, end_time))
            network_analysis.update(self._analyze_network_gateways(start_time, end_time))

            return network_analysis

        except Exception as e:
            logger.error(f"Error analyzing network utilization: {str(e)}")
            return {}

    def _get_vm_metrics(self, resource_id: str, start_time: datetime, end_time: datetime) -> Dict:
        """Get VM metrics from Azure Monitor."""
        try:
            metrics = {}
            metric_names = ['Percentage CPU', 'Available Memory Bytes', 'Disk Read Bytes', 'Disk Write Bytes']
            
            for metric_name in metric_names:
                response = self.monitor_client.metrics.list(
                    resource_id,
                    timespan=f"{start_time}/{end_time}",
                    interval='PT1H',
                    metricnames=metric_name,
                    aggregation='Average'
                )

                if response.value:
                    metrics[metric_name] = {
                        'values': [point.average for point in response.value[0].timeseries[0].data if point.average is not None],
                        'average': np.mean([point.average for point in response.value[0].timeseries[0].data if point.average is not None]),
                        'max': np.max([point.average for point in response.value[0].timeseries[0].data if point.average is not None]),
                        'min': np.min([point.average for point in response.value[0].timeseries[0].data if point.average is not None])
                    }

            return metrics

        except Exception as e:
            logger.error(f"Error getting VM metrics: {str(e)}")
            return {}

    def _get_storage_metrics(self, resource_id: str, start_time: datetime, end_time: datetime) -> Dict:
        """Get Storage Account metrics from Azure Monitor."""
        try:
            metrics = {}
            metric_names = ['UsedCapacity', 'Transactions', 'Availability']
            
            for metric_name in metric_names:
                response = self.monitor_client.metrics.list(
                    resource_id,
                    timespan=f"{start_time}/{end_time}",
                    interval='PT1H',
                    metricnames=metric_name,
                    aggregation='Average'
                )

                if response.value:
                    metrics[metric_name] = {
                        'values': [point.average for point in response.value[0].timeseries[0].data if point.average is not None],
                        'average': np.mean([point.average for point in response.value[0].timeseries[0].data if point.average is not None]),
                        'max': np.max([point.average for point in response.value[0].timeseries[0].data if point.average is not None]),
                        'min': np.min([point.average for point in response.value[0].timeseries[0].data if point.average is not None])
                    }

            return metrics

        except Exception as e:
            logger.error(f"Error getting storage metrics: {str(e)}")
            return {}

    def _is_underutilized(self, metrics: Dict, thresholds: Dict) -> bool:
        """Check if resource is underutilized based on metrics."""
        try:
            for metric_name, metric_data in metrics.items():
                metric_type = metric_name.lower().split()[0]
                if metric_type in thresholds:
                    if metric_data['average'] < thresholds[metric_type]['low']:
                        return True
            return False

        except Exception as e:
            logger.error(f"Error checking underutilization: {str(e)}")
            return False

    def _is_overutilized(self, metrics: Dict, thresholds: Dict) -> bool:
        """Check if resource is overutilized based on metrics."""
        try:
            for metric_name, metric_data in metrics.items():
                metric_type = metric_name.lower().split()[0]
                if metric_type in thresholds:
                    if metric_data['average'] > thresholds[metric_type]['high']:
                        return True
            return False

        except Exception as e:
            logger.error(f"Error checking overutilization: {str(e)}")
            return False

    def _is_rightsizing_candidate(self, vm: object, metrics: Dict) -> bool:
        """Check if VM is a candidate for rightsizing."""
        try:
            cpu_metrics = metrics.get('Percentage CPU', {})
            memory_metrics = metrics.get('Available Memory Bytes', {})
            
            return (
                cpu_metrics.get('average', 100) < self.thresholds['vm']['cpu']['low'] and
                memory_metrics.get('average', 0) > (1 - self.thresholds['vm']['memory']['low']/100)
            )

        except Exception as e:
            logger.error(f"Error checking rightsizing candidate: {str(e)}")
            return False

    def _is_stop_candidate(self, metrics: Dict) -> bool:
        """Check if VM is a candidate for stopping."""
        try:
            cpu_metrics = metrics.get('Percentage CPU', {})
            return cpu_metrics.get('average', 100) < 5  # Very low CPU usage

        except Exception as e:
            logger.error(f"Error checking stop candidate: {str(e)}")
            return False

    def _calculate_overall_statistics(self, analysis: Dict) -> Dict:
        """Calculate overall utilization statistics."""
        try:
            stats = {
                'total_resources': {
                    'vms': len(analysis['virtual_machines'].get('utilization_metrics', [])),
                    'storage': len(analysis['storage_accounts'].get('utilization_metrics', [])),
                    'network': len(analysis['network_resources'].get('utilization_metrics', []))
                },
                'optimization_opportunities': {
                    'underutilized': len(analysis['virtual_machines'].get('underutilized_vms', [])) +
                                   len(analysis['storage_accounts'].get('underutilized_accounts', [])) +
                                   len(analysis['network_resources'].get('underutilized_resources', [])),
                    'overutilized': len(analysis['virtual_machines'].get('overutilized_vms', [])) +
                                  len(analysis['storage_accounts'].get('overutilized_accounts', [])) +
                                  len(analysis['network_resources'].get('overutilized_resources', [])),
                    'rightsizing': len(analysis['virtual_machines'].get('right_size_candidates', [])),
                    'stop_candidates': len(analysis['virtual_machines'].get('stop_candidates', []))
                },
                'potential_savings': self._calculate_total_potential_savings(analysis)
            }

            return stats

        except Exception as e:
            logger.error(f"Error calculating overall statistics: {str(e)}")
            return {}

    def _analyze_utilization_patterns(self, analysis: Dict) -> Dict:
        """Analyze resource utilization patterns."""
        try:
            patterns = {
                'time_based_patterns': self._analyze_time_patterns(analysis),
                'resource_correlations': self._analyze_resource_correlations(analysis),
                'usage_trends': self._analyze_usage_trends(analysis)
            }

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing utilization patterns: {str(e)}")
            return {}

    def _calculate_cost_impact(self, analysis: Dict) -> Dict:
        """Calculate potential cost impact of optimizations."""
        try:
            impact = {
                'total_potential_savings': 0,
                'savings_by_category': {
                    'vm_rightsizing': self._sum_savings(analysis['virtual_machines'].get('right_size_candidates', [])),
                    'vm_shutdown': self._sum_savings(analysis['virtual_machines'].get('stop_candidates', [])),
                    'storage_optimization': self._sum_savings(analysis['storage_accounts'].get('optimization_candidates', []))
                },
                'implementation_costs': self._estimate_implementation_costs(analysis),
                'roi_analysis': self._calculate_roi(analysis)
            }

            impact['total_potential_savings'] = sum(impact['savings_by_category'].values())
            return impact

        except Exception as e:
            logger.error(f"Error calculating cost impact: {str(e)}")
            return {}
