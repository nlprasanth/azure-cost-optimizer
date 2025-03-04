from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.alertsmanagement import AlertsManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

class MonitoringManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.monitor_client = MonitorManagementClient(self.credential, subscription_id)
        self.alerts_client = AlertsManagementClient(self.credential, subscription_id)

    def configure_monitoring(self, resource_id: str, config: Dict) -> Dict:
        """Configure monitoring settings for a resource."""
        try:
            # Configure diagnostic settings
            diagnostic_settings = self._configure_diagnostic_settings(
                resource_id, 
                config.get('diagnostic_settings', {})
            )

            # Configure alert rules
            alert_rules = self._configure_alert_rules(
                resource_id, 
                config.get('alert_rules', {})
            )

            # Configure auto-scale settings
            autoscale_settings = self._configure_autoscale_settings(
                resource_id, 
                config.get('autoscale_settings', {})
            )

            return {
                'diagnostic_settings': diagnostic_settings,
                'alert_rules': alert_rules,
                'autoscale_settings': autoscale_settings
            }

        except Exception as e:
            logger.error(f"Error configuring monitoring: {str(e)}")
            return {}

    def manage_alerts(self, resource_group: str, alert_config: Dict) -> Dict:
        """Manage alert rules and notifications."""
        try:
            result = {
                'created_rules': [],
                'updated_rules': [],
                'deleted_rules': []
            }

            # Create new alert rules
            if 'create' in alert_config:
                for rule in alert_config['create']:
                    created_rule = self._create_alert_rule(
                        resource_group,
                        rule
                    )
                    if created_rule:
                        result['created_rules'].append(created_rule)

            # Update existing alert rules
            if 'update' in alert_config:
                for rule in alert_config['update']:
                    updated_rule = self._update_alert_rule(
                        resource_group,
                        rule['rule_id'],
                        rule
                    )
                    if updated_rule:
                        result['updated_rules'].append(updated_rule)

            # Delete alert rules
            if 'delete' in alert_config:
                for rule_id in alert_config['delete']:
                    deleted = self._delete_alert_rule(
                        resource_group,
                        rule_id
                    )
                    if deleted:
                        result['deleted_rules'].append(rule_id)

            return result

        except Exception as e:
            logger.error(f"Error managing alerts: {str(e)}")
            return {}

    def configure_diagnostic_settings(self, resource_id: str, settings: Dict) -> Dict:
        """Configure diagnostic settings for a resource."""
        try:
            # Get existing diagnostic settings
            existing_settings = self.monitor_client.diagnostic_settings.list(resource_id)

            # Create or update diagnostic settings
            diagnostic_setting = {
                'storage_account_id': settings.get('storage_account_id'),
                'workspace_id': settings.get('workspace_id'),
                'event_hub_authorization_rule_id': settings.get('event_hub_auth_rule_id'),
                'event_hub_name': settings.get('event_hub_name'),
                'metrics': settings.get('metrics', []),
                'logs': settings.get('logs', [])
            }

            # Update or create diagnostic settings
            if list(existing_settings):
                result = self.monitor_client.diagnostic_settings.update(
                    resource_id,
                    list(existing_settings)[0].name,
                    diagnostic_setting
                )
            else:
                result = self.monitor_client.diagnostic_settings.create_or_update(
                    resource_id,
                    'default',
                    diagnostic_setting
                )

            return {
                'resource_id': resource_id,
                'settings': result.as_dict()
            }

        except Exception as e:
            logger.error(f"Error configuring diagnostic settings: {str(e)}")
            return {}

    def configure_autoscale_settings(self, resource_id: str, settings: Dict) -> Dict:
        """Configure autoscale settings for a resource."""
        try:
            autoscale_setting = {
                'location': settings['location'],
                'profiles': settings.get('profiles', []),
                'notifications': settings.get('notifications', []),
                'enabled': settings.get('enabled', True),
                'target_resource_uri': resource_id
            }

            # Create or update autoscale settings
            result = self.monitor_client.autoscale_settings.create_or_update(
                settings['resource_group'],
                settings['setting_name'],
                autoscale_setting
            )

            return {
                'resource_id': resource_id,
                'settings': result.as_dict()
            }

        except Exception as e:
            logger.error(f"Error configuring autoscale settings: {str(e)}")
            return {}

    def _create_alert_rule(self, resource_group: str, rule_config: Dict) -> Dict:
        """Create a new alert rule."""
        try:
            alert_rule = {
                'location': rule_config['location'],
                'severity': rule_config.get('severity', 2),
                'enabled': rule_config.get('enabled', True),
                'scopes': rule_config['scopes'],
                'condition': rule_config['condition'],
                'action_groups': rule_config.get('action_groups', []),
                'description': rule_config.get('description', '')
            }

            result = self.monitor_client.alert_rules.create_or_update(
                resource_group,
                rule_config['name'],
                alert_rule
            )

            return result.as_dict()

        except Exception as e:
            logger.error(f"Error creating alert rule: {str(e)}")
            return {}

    def _update_alert_rule(self, resource_group: str, rule_id: str, 
                          rule_config: Dict) -> Dict:
        """Update an existing alert rule."""
        try:
            # Get existing rule
            existing_rule = self.monitor_client.alert_rules.get(
                resource_group,
                rule_id
            )

            # Update rule properties
            updated_rule = existing_rule.as_dict()
            updated_rule.update(rule_config)

            result = self.monitor_client.alert_rules.create_or_update(
                resource_group,
                rule_id,
                updated_rule
            )

            return result.as_dict()

        except Exception as e:
            logger.error(f"Error updating alert rule: {str(e)}")
            return {}

    def _delete_alert_rule(self, resource_group: str, rule_id: str) -> bool:
        """Delete an alert rule."""
        try:
            self.monitor_client.alert_rules.delete(
                resource_group,
                rule_id
            )
            return True

        except Exception as e:
            logger.error(f"Error deleting alert rule: {str(e)}")
            return False

    def _configure_diagnostic_settings(self, resource_id: str, 
                                    settings: Dict) -> Dict:
        """Configure diagnostic settings for a resource."""
        try:
            diagnostic_setting = {
                'storage_account_id': settings.get('storage_account_id'),
                'workspace_id': settings.get('workspace_id'),
                'event_hub_authorization_rule_id': settings.get('event_hub_auth_rule_id'),
                'event_hub_name': settings.get('event_hub_name'),
                'metrics': settings.get('metrics', []),
                'logs': settings.get('logs', [])
            }

            result = self.monitor_client.diagnostic_settings.create_or_update(
                resource_id,
                'default',
                diagnostic_setting
            )

            return result.as_dict()

        except Exception as e:
            logger.error(f"Error configuring diagnostic settings: {str(e)}")
            return {}

    def _configure_alert_rules(self, resource_id: str, rules: Dict) -> Dict:
        """Configure alert rules for a resource."""
        try:
            result = {
                'created': [],
                'updated': [],
                'failed': []
            }

            for rule in rules:
                rule['scopes'] = [resource_id]
                try:
                    alert_rule = self._create_alert_rule(
                        rule['resource_group'],
                        rule
                    )
                    if alert_rule:
                        result['created'].append(alert_rule)
                    else:
                        result['failed'].append(rule['name'])
                except Exception as e:
                    logger.error(f"Error creating alert rule {rule['name']}: {str(e)}")
                    result['failed'].append(rule['name'])

            return result

        except Exception as e:
            logger.error(f"Error configuring alert rules: {str(e)}")
            return {}

    def _configure_autoscale_settings(self, resource_id: str, 
                                    settings: Dict) -> Dict:
        """Configure autoscale settings for a resource."""
        try:
            if not settings:
                return {}

            settings['target_resource_uri'] = resource_id
            result = self.configure_autoscale_settings(resource_id, settings)
            return result

        except Exception as e:
            logger.error(f"Error configuring autoscale settings: {str(e)}")
            return {}
