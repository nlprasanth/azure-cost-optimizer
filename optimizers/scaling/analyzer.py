from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class ScalingAnalyzer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.monitor_client = MonitorManagementClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.web_client = WebSiteManagementClient(self.credential, subscription_id)
        self.aks_client = ContainerServiceClient(self.credential, subscription_id)

        # Define scaling thresholds
        self.thresholds = {
            'vm_scale_set': {
                'cpu': {'scale_out': 75, 'scale_in': 25},
                'memory': {'scale_out': 80, 'scale_in': 30}
            },
            'app_service': {
                'cpu': {'scale_out': 70, 'scale_in': 30},
                'memory': {'scale_out': 75, 'scale_in': 35},
                'requests': {'scale_out': 800, 'scale_in': 200}
            },
            'aks': {
                'cpu': {'scale_out': 75, 'scale_in': 25},
                'memory': {'scale_out': 80, 'scale_in': 30},
                'pods': {'scale_out': 80, 'scale_in': 30}
            }
        }

    def analyze_scaling_patterns(self, time_range_days: int = 30) -> Dict:
        """Analyze scaling patterns across different resource types."""
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=time_range_days)

            # Analyze different resource types
            analysis = {
                'vm_scale_sets': self._analyze_vmss_scaling(start_time, end_time),
                'app_services': self._analyze_app_service_scaling(start_time, end_time),
                'aks_clusters': self._analyze_aks_scaling(start_time, end_time),
                'workload_patterns': {},
                'scaling_efficiency': {},
                'cost_impact': {}
            }

            # Analyze workload patterns
            analysis['workload_patterns'] = self._analyze_workload_patterns(analysis)
            
            # Calculate scaling efficiency
            analysis['scaling_efficiency'] = self._calculate_scaling_efficiency(analysis)
            
            # Calculate cost impact
            analysis['cost_impact'] = self._calculate_scaling_cost_impact(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing scaling patterns: {str(e)}")
            return {}

    def _analyze_vmss_scaling(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze VM Scale Set scaling patterns."""
        try:
            vmss_analysis = {
                'scaling_metrics': [],
                'scaling_events': [],
                'optimization_opportunities': [],
                'performance_impact': []
            }

            # Get all VM Scale Sets
            vmss_list = list(self.compute_client.virtual_machine_scale_sets.list_all())

            for vmss in vmss_list:
                # Get scaling metrics
                metrics = self._get_vmss_metrics(vmss.id, start_time, end_time)
                
                # Get scaling events
                events = self._get_scaling_events(vmss.id, start_time, end_time)
                
                # Analyze current scaling rules
                current_rules = self._get_vmss_scaling_rules(vmss)
                
                # Calculate scaling efficiency
                efficiency = self._calculate_vmss_scaling_efficiency(metrics, events)
                
                # Generate scaling recommendations
                recommendations = self._generate_vmss_recommendations(
                    metrics, events, current_rules, efficiency
                )

                vmss_analysis['scaling_metrics'].append({
                    'vmss_id': vmss.id,
                    'name': vmss.name,
                    'metrics': metrics
                })

                vmss_analysis['scaling_events'].append({
                    'vmss_id': vmss.id,
                    'name': vmss.name,
                    'events': events
                })

                if recommendations:
                    vmss_analysis['optimization_opportunities'].append(recommendations)

                # Analyze performance impact
                performance_impact = self._analyze_vmss_performance_impact(
                    metrics, events
                )
                if performance_impact:
                    vmss_analysis['performance_impact'].append(performance_impact)

            return vmss_analysis

        except Exception as e:
            logger.error(f"Error analyzing VMSS scaling: {str(e)}")
            return {}

    def _analyze_app_service_scaling(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze App Service scaling patterns."""
        try:
            app_analysis = {
                'scaling_metrics': [],
                'scaling_events': [],
                'optimization_opportunities': [],
                'performance_impact': []
            }

            # Get all App Services
            web_apps = list(self.web_client.web_apps.list())

            for app in web_apps:
                # Get scaling metrics
                metrics = self._get_app_service_metrics(app.id, start_time, end_time)
                
                # Get scaling events
                events = self._get_scaling_events(app.id, start_time, end_time)
                
                # Get current scaling rules
                current_rules = self._get_app_service_scaling_rules(app)
                
                # Calculate scaling efficiency
                efficiency = self._calculate_app_service_scaling_efficiency(
                    metrics, events
                )
                
                # Generate scaling recommendations
                recommendations = self._generate_app_service_recommendations(
                    metrics, events, current_rules, efficiency
                )

                app_analysis['scaling_metrics'].append({
                    'app_id': app.id,
                    'name': app.name,
                    'metrics': metrics
                })

                app_analysis['scaling_events'].append({
                    'app_id': app.id,
                    'name': app.name,
                    'events': events
                })

                if recommendations:
                    app_analysis['optimization_opportunities'].append(recommendations)

                # Analyze performance impact
                performance_impact = self._analyze_app_service_performance_impact(
                    metrics, events
                )
                if performance_impact:
                    app_analysis['performance_impact'].append(performance_impact)

            return app_analysis

        except Exception as e:
            logger.error(f"Error analyzing App Service scaling: {str(e)}")
            return {}

    def _analyze_aks_scaling(self, start_time: datetime, end_time: datetime) -> Dict:
        """Analyze AKS cluster scaling patterns."""
        try:
            aks_analysis = {
                'scaling_metrics': [],
                'scaling_events': [],
                'optimization_opportunities': [],
                'performance_impact': []
            }

            # Get all AKS clusters
            clusters = list(self.aks_client.managed_clusters.list())

            for cluster in clusters:
                # Get scaling metrics
                metrics = self._get_aks_metrics(cluster.id, start_time, end_time)
                
                # Get scaling events
                events = self._get_scaling_events(cluster.id, start_time, end_time)
                
                # Get current scaling rules
                current_rules = self._get_aks_scaling_rules(cluster)
                
                # Calculate scaling efficiency
                efficiency = self._calculate_aks_scaling_efficiency(metrics, events)
                
                # Generate scaling recommendations
                recommendations = self._generate_aks_recommendations(
                    metrics, events, current_rules, efficiency
                )

                aks_analysis['scaling_metrics'].append({
                    'cluster_id': cluster.id,
                    'name': cluster.name,
                    'metrics': metrics
                })

                aks_analysis['scaling_events'].append({
                    'cluster_id': cluster.id,
                    'name': cluster.name,
                    'events': events
                })

                if recommendations:
                    aks_analysis['optimization_opportunities'].append(recommendations)

                # Analyze performance impact
                performance_impact = self._analyze_aks_performance_impact(
                    metrics, events
                )
                if performance_impact:
                    aks_analysis['performance_impact'].append(performance_impact)

            return aks_analysis

        except Exception as e:
            logger.error(f"Error analyzing AKS scaling: {str(e)}")
            return {}

    def _analyze_workload_patterns(self, analysis: Dict) -> Dict:
        """Analyze workload patterns across all resources."""
        try:
            patterns = {
                'daily_patterns': self._analyze_daily_patterns(analysis),
                'weekly_patterns': self._analyze_weekly_patterns(analysis),
                'seasonal_patterns': self._analyze_seasonal_patterns(analysis),
                'correlation_analysis': self._analyze_metric_correlations(analysis)
            }

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing workload patterns: {str(e)}")
            return {}

    def _calculate_scaling_efficiency(self, analysis: Dict) -> Dict:
        """Calculate scaling efficiency metrics."""
        try:
            efficiency = {
                'overall_efficiency': 0,
                'resource_specific': {},
                'cost_efficiency': {},
                'performance_efficiency': {}
            }

            # Calculate VMSS efficiency
            if 'vm_scale_sets' in analysis:
                vmss_efficiency = self._calculate_resource_scaling_efficiency(
                    analysis['vm_scale_sets']
                )
                efficiency['resource_specific']['vmss'] = vmss_efficiency

            # Calculate App Service efficiency
            if 'app_services' in analysis:
                app_efficiency = self._calculate_resource_scaling_efficiency(
                    analysis['app_services']
                )
                efficiency['resource_specific']['app_services'] = app_efficiency

            # Calculate AKS efficiency
            if 'aks_clusters' in analysis:
                aks_efficiency = self._calculate_resource_scaling_efficiency(
                    analysis['aks_clusters']
                )
                efficiency['resource_specific']['aks'] = aks_efficiency

            # Calculate overall efficiency
            total_resources = sum(len(v.get('scaling_metrics', [])) for v in analysis.values() if isinstance(v, dict))
            if total_resources > 0:
                efficiency['overall_efficiency'] = (
                    sum(eff['overall'] for eff in efficiency['resource_specific'].values()) 
                    / len(efficiency['resource_specific'])
                )

            return efficiency

        except Exception as e:
            logger.error(f"Error calculating scaling efficiency: {str(e)}")
            return {}

    def _calculate_scaling_cost_impact(self, analysis: Dict) -> Dict:
        """Calculate cost impact of current scaling patterns."""
        try:
            cost_impact = {
                'total_impact': 0,
                'resource_specific': {},
                'optimization_potential': {},
                'historical_analysis': {}
            }

            # Calculate VMSS cost impact
            if 'vm_scale_sets' in analysis:
                vmss_cost = self._calculate_resource_cost_impact(
                    analysis['vm_scale_sets']
                )
                cost_impact['resource_specific']['vmss'] = vmss_cost

            # Calculate App Service cost impact
            if 'app_services' in analysis:
                app_cost = self._calculate_resource_cost_impact(
                    analysis['app_services']
                )
                cost_impact['resource_specific']['app_services'] = app_cost

            # Calculate AKS cost impact
            if 'aks_clusters' in analysis:
                aks_cost = self._calculate_resource_cost_impact(
                    analysis['aks_clusters']
                )
                cost_impact['resource_specific']['aks'] = aks_cost

            # Calculate total impact
            cost_impact['total_impact'] = sum(
                cost['total'] for cost in cost_impact['resource_specific'].values()
            )

            # Calculate optimization potential
            cost_impact['optimization_potential'] = self._calculate_optimization_potential(
                analysis, cost_impact
            )

            return cost_impact

        except Exception as e:
            logger.error(f"Error calculating cost impact: {str(e)}")
            return {}

    def _analyze_daily_patterns(self, analysis: Dict) -> Dict:
        """Analyze daily workload patterns."""
        try:
            patterns = {
                'peak_hours': [],
                'low_usage_hours': [],
                'consistent_patterns': []
            }

            # Analyze metrics across all resources
            all_metrics = []
            for resource_type in ['vm_scale_sets', 'app_services', 'aks_clusters']:
                if resource_type in analysis:
                    for resource in analysis[resource_type].get('scaling_metrics', []):
                        metrics = resource.get('metrics', {})
                        if metrics:
                            all_metrics.append(self._extract_hourly_patterns(metrics))

            if all_metrics:
                # Identify peak hours
                peak_hours = self._identify_peak_hours(all_metrics)
                patterns['peak_hours'] = peak_hours

                # Identify low usage hours
                low_hours = self._identify_low_usage_hours(all_metrics)
                patterns['low_usage_hours'] = low_hours

                # Identify consistent patterns
                consistent = self._identify_consistent_patterns(all_metrics)
                patterns['consistent_patterns'] = consistent

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing daily patterns: {str(e)}")
            return {}

    def _analyze_weekly_patterns(self, analysis: Dict) -> Dict:
        """Analyze weekly workload patterns."""
        try:
            patterns = {
                'weekday_patterns': {},
                'weekend_patterns': {},
                'weekly_trends': []
            }

            # Analyze metrics across all resources
            all_metrics = []
            for resource_type in ['vm_scale_sets', 'app_services', 'aks_clusters']:
                if resource_type in analysis:
                    for resource in analysis[resource_type].get('scaling_metrics', []):
                        metrics = resource.get('metrics', {})
                        if metrics:
                            all_metrics.append(self._extract_daily_patterns(metrics))

            if all_metrics:
                # Analyze weekday patterns
                weekday_patterns = self._analyze_weekday_patterns(all_metrics)
                patterns['weekday_patterns'] = weekday_patterns

                # Analyze weekend patterns
                weekend_patterns = self._analyze_weekend_patterns(all_metrics)
                patterns['weekend_patterns'] = weekend_patterns

                # Identify weekly trends
                weekly_trends = self._identify_weekly_trends(all_metrics)
                patterns['weekly_trends'] = weekly_trends

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing weekly patterns: {str(e)}")
            return {}

    def _analyze_seasonal_patterns(self, analysis: Dict) -> Dict:
        """Analyze seasonal workload patterns."""
        try:
            patterns = {
                'monthly_patterns': {},
                'quarterly_patterns': {},
                'seasonal_trends': []
            }

            # Analyze metrics across all resources
            all_metrics = []
            for resource_type in ['vm_scale_sets', 'app_services', 'aks_clusters']:
                if resource_type in analysis:
                    for resource in analysis[resource_type].get('scaling_metrics', []):
                        metrics = resource.get('metrics', {})
                        if metrics:
                            all_metrics.append(self._extract_monthly_patterns(metrics))

            if all_metrics:
                # Analyze monthly patterns
                monthly_patterns = self._analyze_monthly_patterns(all_metrics)
                patterns['monthly_patterns'] = monthly_patterns

                # Analyze quarterly patterns
                quarterly_patterns = self._analyze_quarterly_patterns(all_metrics)
                patterns['quarterly_patterns'] = quarterly_patterns

                # Identify seasonal trends
                seasonal_trends = self._identify_seasonal_trends(all_metrics)
                patterns['seasonal_trends'] = seasonal_trends

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {str(e)}")
            return {}
