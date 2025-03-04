from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ScalingManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.web_client = WebSiteManagementClient(self.credential, subscription_id)
        self.aks_client = ContainerServiceClient(self.credential, subscription_id)
        self.monitor_client = MonitorManagementClient(self.credential, subscription_id)

    def update_vmss_scaling_rules(self, resource_group: str, vmss_name: str, 
                                scaling_rules: Dict) -> bool:
        """Update VM Scale Set auto-scaling rules."""
        try:
            # Get current VMSS
            vmss = self.compute_client.virtual_machine_scale_sets.get(
                resource_group,
                vmss_name
            )

            # Update auto-scaling profile
            profile = {
                'name': 'default',
                'capacity': {
                    'minimum': scaling_rules['capacity']['minimum'],
                    'maximum': scaling_rules['capacity']['maximum'],
                    'default': scaling_rules['capacity']['default']
                },
                'rules': []
            }

            # Add scale-out rules
            for rule in scaling_rules.get('scale_out_rules', []):
                profile['rules'].append({
                    'metricTrigger': {
                        'metricName': rule['metric_name'],
                        'metricResourceUri': vmss.id,
                        'timeGrain': rule['time_grain'],
                        'statistic': rule['statistic'],
                        'timeWindow': rule['time_window'],
                        'timeAggregation': rule['time_aggregation'],
                        'operator': rule['operator'],
                        'threshold': rule['threshold']
                    },
                    'scaleAction': {
                        'direction': 'Increase',
                        'type': rule['action_type'],
                        'value': str(rule['action_value']),
                        'cooldown': rule['cooldown']
                    }
                })

            # Add scale-in rules
            for rule in scaling_rules.get('scale_in_rules', []):
                profile['rules'].append({
                    'metricTrigger': {
                        'metricName': rule['metric_name'],
                        'metricResourceUri': vmss.id,
                        'timeGrain': rule['time_grain'],
                        'statistic': rule['statistic'],
                        'timeWindow': rule['time_window'],
                        'timeAggregation': rule['time_aggregation'],
                        'operator': rule['operator'],
                        'threshold': rule['threshold']
                    },
                    'scaleAction': {
                        'direction': 'Decrease',
                        'type': rule['action_type'],
                        'value': str(rule['action_value']),
                        'cooldown': rule['cooldown']
                    }
                })

            # Update auto-scaling settings
            self.monitor_client.autoscale_settings.create_or_update(
                resource_group,
                f"{vmss_name}-autoscale",
                {
                    'location': vmss.location,
                    'properties': {
                        'enabled': True,
                        'targetResourceUri': vmss.id,
                        'profiles': [profile]
                    }
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error updating VMSS scaling rules for {vmss_name}: {str(e)}")
            return False

    def update_app_service_scaling_rules(self, resource_group: str, app_name: str, 
                                       scaling_rules: Dict) -> bool:
        """Update App Service auto-scaling rules."""
        try:
            # Get current App Service
            app = self.web_client.web_apps.get(resource_group, app_name)

            # Update auto-scaling profile
            profile = {
                'name': 'default',
                'capacity': {
                    'minimum': scaling_rules['capacity']['minimum'],
                    'maximum': scaling_rules['capacity']['maximum'],
                    'default': scaling_rules['capacity']['default']
                },
                'rules': []
            }

            # Add scale-out rules
            for rule in scaling_rules.get('scale_out_rules', []):
                profile['rules'].append({
                    'metricTrigger': {
                        'metricName': rule['metric_name'],
                        'metricResourceUri': app.id,
                        'timeGrain': rule['time_grain'],
                        'statistic': rule['statistic'],
                        'timeWindow': rule['time_window'],
                        'timeAggregation': rule['time_aggregation'],
                        'operator': rule['operator'],
                        'threshold': rule['threshold']
                    },
                    'scaleAction': {
                        'direction': 'Increase',
                        'type': rule['action_type'],
                        'value': str(rule['action_value']),
                        'cooldown': rule['cooldown']
                    }
                })

            # Add scale-in rules
            for rule in scaling_rules.get('scale_in_rules', []):
                profile['rules'].append({
                    'metricTrigger': {
                        'metricName': rule['metric_name'],
                        'metricResourceUri': app.id,
                        'timeGrain': rule['time_grain'],
                        'statistic': rule['statistic'],
                        'timeWindow': rule['time_window'],
                        'timeAggregation': rule['time_aggregation'],
                        'operator': rule['operator'],
                        'threshold': rule['threshold']
                    },
                    'scaleAction': {
                        'direction': 'Decrease',
                        'type': rule['action_type'],
                        'value': str(rule['action_value']),
                        'cooldown': rule['cooldown']
                    }
                })

            # Update auto-scaling settings
            self.monitor_client.autoscale_settings.create_or_update(
                resource_group,
                f"{app_name}-autoscale",
                {
                    'location': app.location,
                    'properties': {
                        'enabled': True,
                        'targetResourceUri': app.id,
                        'profiles': [profile]
                    }
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error updating App Service scaling rules for {app_name}: {str(e)}")
            return False

    def update_aks_scaling_rules(self, resource_group: str, cluster_name: str, 
                               scaling_rules: Dict) -> bool:
        """Update AKS cluster auto-scaling rules."""
        try:
            # Get current cluster
            cluster = self.aks_client.managed_clusters.get(
                resource_group,
                cluster_name
            )

            # Update node pool auto-scaling settings
            for node_pool in scaling_rules.get('node_pools', []):
                self.aks_client.agent_pools.begin_create_or_update(
                    resource_group,
                    cluster_name,
                    node_pool['name'],
                    {
                        'enableAutoScaling': True,
                        'minCount': node_pool['min_count'],
                        'maxCount': node_pool['max_count'],
                        'count': node_pool['count']
                    }
                ).result()

            # Update HPA settings if provided
            if 'hpa_settings' in scaling_rules:
                self._update_hpa_settings(
                    resource_group,
                    cluster_name,
                    scaling_rules['hpa_settings']
                )

            return True

        except Exception as e:
            logger.error(f"Error updating AKS scaling rules for {cluster_name}: {str(e)}")
            return False

    def create_scheduled_scaling_profile(self, resource_group: str, resource_name: str,
                                      resource_type: str, schedule: Dict) -> bool:
        """Create scheduled scaling profile."""
        try:
            # Get resource ID based on type
            resource_id = self._get_resource_id(
                resource_group, resource_name, resource_type
            )

            # Create schedule profile
            profile = {
                'name': schedule['name'],
                'capacity': {
                    'minimum': schedule['capacity']['minimum'],
                    'maximum': schedule['capacity']['maximum'],
                    'default': schedule['capacity']['default']
                },
                'fixedDate': {
                    'timeZone': schedule['timezone'],
                    'start': schedule['start_time'],
                    'end': schedule['end_time']
                } if schedule.get('type') == 'fixed' else None,
                'recurrence': {
                    'frequency': schedule['frequency'],
                    'schedule': {
                        'days': schedule['days'],
                        'hours': schedule['hours'],
                        'minutes': schedule['minutes']
                    }
                } if schedule.get('type') == 'recurring' else None
            }

            # Update auto-scaling settings
            self.monitor_client.autoscale_settings.create_or_update(
                resource_group,
                f"{resource_name}-{schedule['name']}-schedule",
                {
                    'location': 'global',
                    'properties': {
                        'enabled': True,
                        'targetResourceUri': resource_id,
                        'profiles': [profile]
                    }
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error creating scheduled scaling profile for {resource_name}: {str(e)}")
            return False

    def create_predictive_scaling_profile(self, resource_group: str, resource_name: str,
                                        resource_type: str, prediction_config: Dict) -> bool:
        """Create predictive scaling profile."""
        try:
            # Get resource ID based on type
            resource_id = self._get_resource_id(
                resource_group, resource_name, resource_type
            )

            # Create predictive profile
            profile = {
                'name': 'predictive-scaling',
                'capacity': {
                    'minimum': prediction_config['capacity']['minimum'],
                    'maximum': prediction_config['capacity']['maximum'],
                    'default': prediction_config['capacity']['default']
                },
                'predictiveAutoscale': {
                    'lookAheadTime': prediction_config['look_ahead_time'],
                    'scalingMode': prediction_config['scaling_mode']
                }
            }

            # Update auto-scaling settings
            self.monitor_client.autoscale_settings.create_or_update(
                resource_group,
                f"{resource_name}-predictive-scaling",
                {
                    'location': 'global',
                    'properties': {
                        'enabled': True,
                        'targetResourceUri': resource_id,
                        'profiles': [profile]
                    }
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error creating predictive scaling profile for {resource_name}: {str(e)}")
            return False

    def create_scaling_notification(self, resource_group: str, resource_name: str,
                                 resource_type: str, notification_config: Dict) -> bool:
        """Create scaling event notification."""
        try:
            # Get resource ID based on type
            resource_id = self._get_resource_id(
                resource_group, resource_name, resource_type
            )

            # Create notification
            notification = {
                'email': {
                    'sendToSubscriptionAdministrator': notification_config.get('notify_admin', False),
                    'sendToSubscriptionCoAdministrators': notification_config.get('notify_coadmin', False),
                    'customEmails': notification_config.get('custom_emails', [])
                },
                'webhooks': [
                    {'serviceUri': uri} for uri in notification_config.get('webhooks', [])
                ]
            }

            # Update auto-scaling settings with notification
            self.monitor_client.autoscale_settings.create_or_update(
                resource_group,
                f"{resource_name}-scaling-notification",
                {
                    'location': 'global',
                    'properties': {
                        'enabled': True,
                        'targetResourceUri': resource_id,
                        'notifications': [notification]
                    }
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error creating scaling notification for {resource_name}: {str(e)}")
            return False

    def _get_resource_id(self, resource_group: str, resource_name: str, 
                        resource_type: str) -> str:
        """Get resource ID based on type."""
        try:
            if resource_type == 'vmss':
                resource = self.compute_client.virtual_machine_scale_sets.get(
                    resource_group, resource_name
                )
            elif resource_type == 'app_service':
                resource = self.web_client.web_apps.get(
                    resource_group, resource_name
                )
            elif resource_type == 'aks':
                resource = self.aks_client.managed_clusters.get(
                    resource_group, resource_name
                )
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")

            return resource.id

        except Exception as e:
            logger.error(f"Error getting resource ID: {str(e)}")
            return ""

    def _update_hpa_settings(self, resource_group: str, cluster_name: str, 
                           hpa_settings: Dict) -> bool:
        """Update Horizontal Pod Autoscaler settings."""
        try:
            # This is a placeholder for the actual HPA update implementation
            # The actual implementation would involve using the Kubernetes API
            return True

        except Exception as e:
            logger.error(f"Error updating HPA settings for {cluster_name}: {str(e)}")
            return False
