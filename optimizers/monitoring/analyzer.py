from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class MonitoringAnalyzer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.monitor_client = MonitorManagementClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.web_client = WebSiteManagementClient(self.credential, subscription_id)
        self.storage_client = StorageManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)

        # Define monitoring thresholds
        self.thresholds = {
            'vm': {
                'cpu': {'warning': 80, 'critical': 90},
                'memory': {'warning': 85, 'critical': 95},
                'disk': {'warning': 85, 'critical': 95}
            },
            'app_service': {
                'cpu': {'warning': 75, 'critical': 85},
                'memory': {'warning': 80, 'critical': 90},
                'response_time': {'warning': 1000, 'critical': 2000}
            },
            'storage': {
                'latency': {'warning': 100, 'critical': 200},
                'availability': {'warning': 99.9, 'critical': 99}
            },
            'network': {
                'bandwidth': {'warning': 85, 'critical': 95},
                'latency': {'warning': 100, 'critical': 200}
            }
        }

    def analyze_resource_health(self, time_range_days: int = 7) -> Dict:
        """Analyze health and performance of resources."""
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=time_range_days)

            # Analyze different resource types
            analysis = {
                'virtual_machines': self._analyze_vm_health(start_time, end_time),
                'app_services': self._analyze_app_service_health(start_time, end_time),
                'storage_accounts': self._analyze_storage_health(start_time, end_time),
                'network_resources': self._analyze_network_health(start_time, end_time),
                'anomalies': {},
                'performance_trends': {},
                'availability_metrics': {}
            }

            # Detect anomalies
            analysis['anomalies'] = self._detect_anomalies(analysis)
            
            # Analyze performance trends
            analysis['performance_trends'] = self._analyze_performance_trends(analysis)
            
            # Calculate availability metrics
            analysis['availability_metrics'] = self._calculate_availability_metrics(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resource health: {str(e)}")
            return {}

    def _analyze_vm_health(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze Virtual Machine health metrics."""
        try:
            vm_health = {
                'health_metrics': [],
                'performance_issues': [],
                'availability_data': [],
                'resource_utilization': []
            }

            # Get all VMs in subscription
            vms = list(self.compute_client.virtual_machines.list_all())

            for vm in vms:
                # Get health metrics
                metrics = self._get_vm_health_metrics(vm.id, start_time, end_time)
                
                # Get diagnostic data
                diagnostics = self._get_vm_diagnostics(vm.id, start_time, end_time)
                
                # Analyze performance
                performance = self._analyze_vm_performance(metrics, diagnostics)
                
                # Check for issues
                issues = self._check_vm_health_issues(metrics, diagnostics)

                vm_health['health_metrics'].append({
                    'vm_id': vm.id,
                    'name': vm.name,
                    'metrics': metrics,
                    'diagnostics': diagnostics
                })

                if performance:
                    vm_health['resource_utilization'].append({
                        'vm_id': vm.id,
                        'name': vm.name,
                        'utilization': performance
                    })

                if issues:
                    vm_health['performance_issues'].append({
                        'vm_id': vm.id,
                        'name': vm.name,
                        'issues': issues
                    })

                # Calculate availability
                availability = self._calculate_vm_availability(metrics, diagnostics)
                vm_health['availability_data'].append({
                    'vm_id': vm.id,
                    'name': vm.name,
                    'availability': availability
                })

            return vm_health

        except Exception as e:
            logger.error(f"Error analyzing VM health: {str(e)}")
            return {}

    def _analyze_app_service_health(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze App Service health metrics."""
        try:
            app_health = {
                'health_metrics': [],
                'performance_issues': [],
                'availability_data': [],
                'resource_utilization': []
            }

            # Get all App Services
            web_apps = list(self.web_client.web_apps.list())

            for app in web_apps:
                # Get health metrics
                metrics = self._get_app_service_metrics(app.id, start_time, end_time)
                
                # Get diagnostic data
                diagnostics = self._get_app_diagnostics(app.id, start_time, end_time)
                
                # Analyze performance
                performance = self._analyze_app_performance(metrics, diagnostics)
                
                # Check for issues
                issues = self._check_app_health_issues(metrics, diagnostics)

                app_health['health_metrics'].append({
                    'app_id': app.id,
                    'name': app.name,
                    'metrics': metrics,
                    'diagnostics': diagnostics
                })

                if performance:
                    app_health['resource_utilization'].append({
                        'app_id': app.id,
                        'name': app.name,
                        'utilization': performance
                    })

                if issues:
                    app_health['performance_issues'].append({
                        'app_id': app.id,
                        'name': app.name,
                        'issues': issues
                    })

                # Calculate availability
                availability = self._calculate_app_availability(metrics, diagnostics)
                app_health['availability_data'].append({
                    'app_id': app.id,
                    'name': app.name,
                    'availability': availability
                })

            return app_health

        except Exception as e:
            logger.error(f"Error analyzing App Service health: {str(e)}")
            return {}

    def _analyze_storage_health(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze Storage Account health metrics."""
        try:
            storage_health = {
                'health_metrics': [],
                'performance_issues': [],
                'availability_data': [],
                'resource_utilization': []
            }

            # Get all storage accounts
            storage_accounts = list(self.storage_client.storage_accounts.list())

            for account in storage_accounts:
                # Get health metrics
                metrics = self._get_storage_metrics(account.id, start_time, end_time)
                
                # Get diagnostic data
                diagnostics = self._get_storage_diagnostics(account.id, start_time, end_time)
                
                # Analyze performance
                performance = self._analyze_storage_performance(metrics, diagnostics)
                
                # Check for issues
                issues = self._check_storage_health_issues(metrics, diagnostics)

                storage_health['health_metrics'].append({
                    'account_id': account.id,
                    'name': account.name,
                    'metrics': metrics,
                    'diagnostics': diagnostics
                })

                if performance:
                    storage_health['resource_utilization'].append({
                        'account_id': account.id,
                        'name': account.name,
                        'utilization': performance
                    })

                if issues:
                    storage_health['performance_issues'].append({
                        'account_id': account.id,
                        'name': account.name,
                        'issues': issues
                    })

                # Calculate availability
                availability = self._calculate_storage_availability(metrics, diagnostics)
                storage_health['availability_data'].append({
                    'account_id': account.id,
                    'name': account.name,
                    'availability': availability
                })

            return storage_health

        except Exception as e:
            logger.error(f"Error analyzing Storage health: {str(e)}")
            return {}

    def _analyze_network_health(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze Network resource health metrics."""
        try:
            network_health = {
                'health_metrics': [],
                'performance_issues': [],
                'availability_data': [],
                'resource_utilization': []
            }

            # Analyze different network resources
            network_health.update(self._analyze_load_balancers(start_time, end_time))
            network_health.update(self._analyze_application_gateways(start_time, end_time))
            network_health.update(self._analyze_virtual_networks(start_time, end_time))

            return network_health

        except Exception as e:
            logger.error(f"Error analyzing Network health: {str(e)}")
            return {}

    def _detect_anomalies(self, analysis: Dict) -> Dict:
        """Detect anomalies in resource metrics."""
        try:
            anomalies = {
                'vm_anomalies': self._detect_vm_anomalies(analysis['virtual_machines']),
                'app_anomalies': self._detect_app_anomalies(analysis['app_services']),
                'storage_anomalies': self._detect_storage_anomalies(analysis['storage_accounts']),
                'network_anomalies': self._detect_network_anomalies(analysis['network_resources'])
            }

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return {}

    def _analyze_performance_trends(self, analysis: Dict) -> Dict:
        """Analyze performance trends across resources."""
        try:
            trends = {
                'vm_trends': self._analyze_vm_trends(analysis['virtual_machines']),
                'app_trends': self._analyze_app_trends(analysis['app_services']),
                'storage_trends': self._analyze_storage_trends(analysis['storage_accounts']),
                'network_trends': self._analyze_network_trends(analysis['network_resources'])
            }

            return trends

        except Exception as e:
            logger.error(f"Error analyzing performance trends: {str(e)}")
            return {}

    def _calculate_availability_metrics(self, analysis: Dict) -> Dict:
        """Calculate availability metrics for all resources."""
        try:
            availability = {
                'overall_availability': 0,
                'resource_specific': {},
                'sla_compliance': {},
                'downtime_analysis': {}
            }

            # Calculate VM availability
            if 'virtual_machines' in analysis:
                vm_availability = self._calculate_resource_availability(
                    analysis['virtual_machines'].get('availability_data', [])
                )
                availability['resource_specific']['virtual_machines'] = vm_availability

            # Calculate App Service availability
            if 'app_services' in analysis:
                app_availability = self._calculate_resource_availability(
                    analysis['app_services'].get('availability_data', [])
                )
                availability['resource_specific']['app_services'] = app_availability

            # Calculate Storage availability
            if 'storage_accounts' in analysis:
                storage_availability = self._calculate_resource_availability(
                    analysis['storage_accounts'].get('availability_data', [])
                )
                availability['resource_specific']['storage_accounts'] = storage_availability

            # Calculate overall availability
            total_resources = sum(
                len(data) for data in availability['resource_specific'].values()
            )
            if total_resources > 0:
                availability['overall_availability'] = (
                    sum(
                        sum(resource['availability'] for resource in resources)
                        for resources in availability['resource_specific'].values()
                    ) / total_resources
                )

            # Calculate SLA compliance
            availability['sla_compliance'] = self._calculate_sla_compliance(
                availability['resource_specific']
            )

            # Analyze downtime
            availability['downtime_analysis'] = self._analyze_downtime(analysis)

            return availability

        except Exception as e:
            logger.error(f"Error calculating availability metrics: {str(e)}")
            return {}
