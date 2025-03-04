from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import Budget, BudgetTimePeriod, BudgetFilter, Notification
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class BudgetManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.cost_client = CostManagementClient(self.credential)

    def create_budget(self, config: Dict) -> Dict:
        """Create a new budget."""
        try:
            scope = f'/subscriptions/{self.subscription_id}'
            
            # Create budget time period
            time_period = BudgetTimePeriod(
                start_date=config['start_date'],
                end_date=config.get('end_date')
            )

            # Create budget filters if specified
            filters = None
            if config.get('filters'):
                filters = BudgetFilter(
                    resource_groups=config['filters'].get('resource_groups', []),
                    resources=config['filters'].get('resources', []),
                    meters=config['filters'].get('meters', []),
                    tags=config['filters'].get('tags', {})
                )

            # Create notifications
            notifications = {}
            for notif in config.get('notifications', []):
                notifications[notif['name']] = Notification(
                    enabled=True,
                    operator=notif['operator'],
                    threshold=notif['threshold'],
                    contact_emails=notif['contact_emails'],
                    contact_roles=notif.get('contact_roles', []),
                    contact_groups=notif.get('contact_groups', [])
                )

            # Create budget
            budget = Budget(
                category='Cost',
                amount=config['amount'],
                time_grain=config.get('time_grain', 'Monthly'),
                time_period=time_period,
                filters=filters,
                notifications=notifications
            )

            # Create budget in Azure
            result = self.cost_client.budgets.create_or_update(
                scope=scope,
                budget_name=config['name'],
                parameters=budget
            )

            return self._process_budget_response(result)

        except Exception as e:
            logger.error(f"Error creating budget: {str(e)}")
            return None

    def update_budget(self, budget_name: str, updates: Dict) -> Dict:
        """Update an existing budget."""
        try:
            scope = f'/subscriptions/{self.subscription_id}'
            
            # Get existing budget
            existing_budget = self.cost_client.budgets.get(scope, budget_name)
            if not existing_budget:
                return None

            # Update amount if specified
            if 'amount' in updates:
                existing_budget.amount = updates['amount']

            # Update time period if specified
            if 'time_period' in updates:
                existing_budget.time_period = BudgetTimePeriod(
                    start_date=updates['time_period'].get('start_date', existing_budget.time_period.start_date),
                    end_date=updates['time_period'].get('end_date', existing_budget.time_period.end_date)
                )

            # Update filters if specified
            if 'filters' in updates:
                existing_budget.filters = BudgetFilter(
                    resource_groups=updates['filters'].get('resource_groups', []),
                    resources=updates['filters'].get('resources', []),
                    meters=updates['filters'].get('meters', []),
                    tags=updates['filters'].get('tags', {})
                )

            # Update notifications if specified
            if 'notifications' in updates:
                for notif in updates['notifications']:
                    existing_budget.notifications[notif['name']] = Notification(
                        enabled=True,
                        operator=notif['operator'],
                        threshold=notif['threshold'],
                        contact_emails=notif['contact_emails'],
                        contact_roles=notif.get('contact_roles', []),
                        contact_groups=notif.get('contact_groups', [])
                    )

            # Update budget in Azure
            result = self.cost_client.budgets.create_or_update(
                scope=scope,
                budget_name=budget_name,
                parameters=existing_budget
            )

            return self._process_budget_response(result)

        except Exception as e:
            logger.error(f"Error updating budget: {str(e)}")
            return None

    def delete_budget(self, budget_name: str) -> bool:
        """Delete a budget."""
        try:
            scope = f'/subscriptions/{self.subscription_id}'
            self.cost_client.budgets.delete(scope, budget_name)
            return True

        except Exception as e:
            logger.error(f"Error deleting budget: {str(e)}")
            return False

    def get_budget(self, budget_name: str) -> Dict:
        """Get details of a specific budget."""
        try:
            scope = f'/subscriptions/{self.subscription_id}'
            budget = self.cost_client.budgets.get(scope, budget_name)
            return self._process_budget_response(budget)

        except Exception as e:
            logger.error(f"Error getting budget: {str(e)}")
            return None

    def list_budgets(self) -> List[Dict]:
        """List all budgets."""
        try:
            scope = f'/subscriptions/{self.subscription_id}'
            budgets = self.cost_client.budgets.list(scope)
            return [self._process_budget_response(budget) for budget in budgets]

        except Exception as e:
            logger.error(f"Error listing budgets: {str(e)}")
            return []

    def _process_budget_response(self, budget) -> Dict:
        """Process budget response into a standardized format."""
        try:
            return {
                'name': budget.name,
                'amount': budget.amount,
                'time_grain': budget.time_grain,
                'time_period': {
                    'start_date': budget.time_period.start_date,
                    'end_date': budget.time_period.end_date
                },
                'filters': {
                    'resource_groups': budget.filters.resource_groups if budget.filters else [],
                    'resources': budget.filters.resources if budget.filters else [],
                    'meters': budget.filters.meters if budget.filters else [],
                    'tags': budget.filters.tags if budget.filters else {}
                } if budget.filters else None,
                'notifications': [
                    {
                        'name': name,
                        'enabled': notif.enabled,
                        'operator': notif.operator,
                        'threshold': notif.threshold,
                        'contact_emails': notif.contact_emails,
                        'contact_roles': notif.contact_roles,
                        'contact_groups': notif.contact_groups
                    }
                    for name, notif in budget.notifications.items()
                ] if budget.notifications else []
            }

        except Exception as e:
            logger.error(f"Error processing budget response: {str(e)}")
            return {}

    def create_default_notifications(self, budget_name: str) -> bool:
        """Create default notification thresholds for a budget."""
        try:
            default_notifications = [
                {
                    'name': 'warning',
                    'operator': 'GreaterThan',
                    'threshold': 80,
                    'contact_emails': []
                },
                {
                    'name': 'critical',
                    'operator': 'GreaterThan',
                    'threshold': 90,
                    'contact_emails': []
                },
                {
                    'name': 'exceeded',
                    'operator': 'GreaterThan',
                    'threshold': 100,
                    'contact_emails': []
                }
            ]

            return self.update_budget(budget_name, {'notifications': default_notifications}) is not None

        except Exception as e:
            logger.error(f"Error creating default notifications: {str(e)}")
            return False

    def validate_budget_config(self, config: Dict) -> Tuple[bool, str]:
        """Validate budget configuration."""
        try:
            required_fields = ['name', 'amount', 'start_date']
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"

            # Validate amount
            if not isinstance(config['amount'], (int, float)) or config['amount'] <= 0:
                return False, "Amount must be a positive number"

            # Validate dates
            try:
                start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
                if 'end_date' in config:
                    end_date = datetime.strptime(config['end_date'], '%Y-%m-%d')
                    if end_date <= start_date:
                        return False, "End date must be after start date"
            except ValueError:
                return False, "Invalid date format. Use YYYY-MM-DD"

            # Validate time grain
            if 'time_grain' in config and config['time_grain'] not in ['Monthly', 'Quarterly', 'Annually']:
                return False, "Invalid time_grain. Must be Monthly, Quarterly, or Annually"

            # Validate notifications
            if 'notifications' in config:
                for notif in config['notifications']:
                    if 'name' not in notif or 'threshold' not in notif or 'contact_emails' not in notif:
                        return False, "Invalid notification configuration"
                    if not isinstance(notif['threshold'], (int, float)) or notif['threshold'] < 0:
                        return False, "Notification threshold must be a positive number"

            return True, "Configuration is valid"

        except Exception as e:
            logger.error(f"Error validating budget config: {str(e)}")
            return False, f"Error validating configuration: {str(e)}"
