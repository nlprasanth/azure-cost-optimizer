from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

class CostManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.consumption_client = ConsumptionManagementClient(self.credential, subscription_id)
        self.cost_client = CostManagementClient(self.credential)
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)

    def manage_budgets(self, budget_config: Dict) -> Dict:
        """Manage budget configurations."""
        try:
            result = {
                'created': [],
                'updated': [],
                'deleted': []
            }

            # Create new budgets
            if 'create' in budget_config:
                for budget in budget_config['create']:
                    created = self._create_budget(budget)
                    if created:
                        result['created'].append(created)

            # Update existing budgets
            if 'update' in budget_config:
                for budget in budget_config['update']:
                    updated = self._update_budget(budget)
                    if updated:
                        result['updated'].append(updated)

            # Delete budgets
            if 'delete' in budget_config:
                for budget_name in budget_config['delete']:
                    deleted = self._delete_budget(budget_name)
                    if deleted:
                        result['deleted'].append(budget_name)

            return result

        except Exception as e:
            logger.error(f"Error managing budgets: {str(e)}")
            return {}

    def configure_cost_alerts(self, alert_config: Dict) -> Dict:
        """Configure cost alerts."""
        try:
            result = {
                'created': [],
                'updated': [],
                'deleted': []
            }

            # Create new alerts
            if 'create' in alert_config:
                for alert in alert_config['create']:
                    created = self._create_cost_alert(alert)
                    if created:
                        result['created'].append(created)

            # Update existing alerts
            if 'update' in alert_config:
                for alert in alert_config['update']:
                    updated = self._update_cost_alert(alert)
                    if updated:
                        result['updated'].append(updated)

            # Delete alerts
            if 'delete' in alert_config:
                for alert_name in alert_config['delete']:
                    deleted = self._delete_cost_alert(alert_name)
                    if deleted:
                        result['deleted'].append(alert_name)

            return result

        except Exception as e:
            logger.error(f"Error configuring cost alerts: {str(e)}")
            return {}

    def apply_cost_policies(self, policy_config: Dict) -> Dict:
        """Apply cost management policies."""
        try:
            result = {
                'applied': [],
                'failed': []
            }

            for policy in policy_config.get('policies', []):
                try:
                    # Apply policy
                    applied = self._apply_cost_policy(policy)
                    if applied:
                        result['applied'].append(policy['name'])
                    else:
                        result['failed'].append(policy['name'])
                except Exception as e:
                    logger.error(f"Error applying policy {policy['name']}: {str(e)}")
                    result['failed'].append(policy['name'])

            return result

        except Exception as e:
            logger.error(f"Error applying cost policies: {str(e)}")
            return {}

    def _create_budget(self, budget_config: Dict) -> Dict:
        """Create a new budget."""
        try:
            budget_name = budget_config['name']
            budget_properties = {
                'category': budget_config.get('category', 'Cost'),
                'amount': budget_config['amount'],
                'time_grain': budget_config.get('time_grain', 'Monthly'),
                'time_period': {
                    'start_date': budget_config['start_date'],
                    'end_date': budget_config.get('end_date')
                },
                'notifications': budget_config.get('notifications', {})
            }

            result = self.consumption_client.budgets.create_or_update(
                budget_name,
                budget_properties
            )

            return result.as_dict()

        except Exception as e:
            logger.error(f"Error creating budget: {str(e)}")
            return {}

    def _update_budget(self, budget_config: Dict) -> Dict:
        """Update an existing budget."""
        try:
            budget_name = budget_config['name']
            
            # Get existing budget
            existing_budget = self.consumption_client.budgets.get(budget_name)
            
            # Update properties
            updated_properties = existing_budget.as_dict()
            updated_properties.update(budget_config)

            result = self.consumption_client.budgets.create_or_update(
                budget_name,
                updated_properties
            )

            return result.as_dict()

        except Exception as e:
            logger.error(f"Error updating budget: {str(e)}")
            return {}

    def _delete_budget(self, budget_name: str) -> bool:
        """Delete a budget."""
        try:
            self.consumption_client.budgets.delete(budget_name)
            return True

        except Exception as e:
            logger.error(f"Error deleting budget: {str(e)}")
            return False

    def _create_cost_alert(self, alert_config: Dict) -> Dict:
        """Create a new cost alert."""
        try:
            alert_properties = {
                'definition': {
                    'name': alert_config['name'],
                    'description': alert_config.get('description', ''),
                    'enabled': alert_config.get('enabled', True),
                    'type': 'Cost',
                    'criteria': alert_config['criteria']
                },
                'actions': alert_config.get('actions', [])
            }

            result = self.cost_client.alerts.create_or_update(
                alert_config['resource_group'],
                alert_config['name'],
                alert_properties
            )

            return result.as_dict()

        except Exception as e:
            logger.error(f"Error creating cost alert: {str(e)}")
            return {}

    def _update_cost_alert(self, alert_config: Dict) -> Dict:
        """Update an existing cost alert."""
        try:
            # Get existing alert
            existing_alert = self.cost_client.alerts.get(
                alert_config['resource_group'],
                alert_config['name']
            )
            
            # Update properties
            updated_properties = existing_alert.as_dict()
            updated_properties['definition'].update(alert_config.get('definition', {}))
            updated_properties['actions'] = alert_config.get('actions', 
                                                           updated_properties['actions'])

            result = self.cost_client.alerts.create_or_update(
                alert_config['resource_group'],
                alert_config['name'],
                updated_properties
            )

            return result.as_dict()

        except Exception as e:
            logger.error(f"Error updating cost alert: {str(e)}")
            return {}

    def _delete_cost_alert(self, alert_name: str) -> bool:
        """Delete a cost alert."""
        try:
            self.cost_client.alerts.delete(alert_name)
            return True

        except Exception as e:
            logger.error(f"Error deleting cost alert: {str(e)}")
            return False

    def _apply_cost_policy(self, policy: Dict) -> bool:
        """Apply a cost management policy."""
        try:
            policy_assignment = {
                'properties': {
                    'displayName': policy['display_name'],
                    'description': policy.get('description', ''),
                    'metadata': policy.get('metadata', {}),
                    'parameters': policy.get('parameters', {}),
                    'nonComplianceMessages': policy.get('non_compliance_messages', [])
                }
            }

            result = self.resource_client.policy_assignments.create(
                policy['scope'],
                policy['name'],
                policy_assignment
            )

            return bool(result)

        except Exception as e:
            logger.error(f"Error applying cost policy: {str(e)}")
            return False

    def configure_cost_exports(self, export_config: Dict) -> Dict:
        """Configure automated cost exports."""
        try:
            result = {
                'configured': [],
                'failed': []
            }

            for export in export_config.get('exports', []):
                try:
                    # Configure export
                    export_result = self._configure_cost_export(export)
                    if export_result:
                        result['configured'].append(export['name'])
                    else:
                        result['failed'].append(export['name'])
                except Exception as e:
                    logger.error(f"Error configuring export {export['name']}: {str(e)}")
                    result['failed'].append(export['name'])

            return result

        except Exception as e:
            logger.error(f"Error configuring cost exports: {str(e)}")
            return {}

    def _configure_cost_export(self, export_config: Dict) -> bool:
        """Configure a single cost export."""
        try:
            export_properties = {
                'format': export_config.get('format', 'Csv'),
                'deliveryInfo': {
                    'destination': {
                        'resourceId': export_config['destination_resource_id'],
                        'container': export_config.get('container', 'exports'),
                        'rootFolderPath': export_config.get('folder_path', '/costs')
                    }
                },
                'schedule': {
                    'recurrence': export_config.get('recurrence', 'Daily'),
                    'recurrencePeriod': {
                        'from': export_config['start_date'],
                        'to': export_config.get('end_date')
                    }
                },
                'definition': {
                    'type': 'Usage',
                    'timeframe': export_config.get('timeframe', 'MonthToDate'),
                    'dataset': {
                        'granularity': export_config.get('granularity', 'Daily'),
                        'aggregation': export_config.get('aggregation', {}),
                        'grouping': export_config.get('grouping', [])
                    }
                }
            }

            result = self.cost_client.exports.create_or_update(
                export_config['scope'],
                export_config['name'],
                export_properties
            )

            return bool(result)

        except Exception as e:
            logger.error(f"Error configuring cost export: {str(e)}")
            return False
