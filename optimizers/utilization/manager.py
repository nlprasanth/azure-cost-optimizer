from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.storage_client = StorageManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)

    def resize_vm(self, resource_group: str, vm_name: str, new_size: str) -> bool:
        """Resize a virtual machine."""
        try:
            # Get VM
            vm = self.compute_client.virtual_machines.get(resource_group, vm_name)
            
            # Update size
            vm.hardware_profile.vm_size = new_size
            
            # Start the resize operation
            poller = self.compute_client.virtual_machines.begin_update(
                resource_group,
                vm_name,
                vm
            )
            
            # Wait for completion
            result = poller.result()
            
            return True

        except Exception as e:
            logger.error(f"Error resizing VM {vm_name}: {str(e)}")
            return False

    def stop_vm(self, resource_group: str, vm_name: str, deallocate: bool = True) -> bool:
        """Stop a virtual machine."""
        try:
            if deallocate:
                poller = self.compute_client.virtual_machines.begin_deallocate(
                    resource_group,
                    vm_name
                )
            else:
                poller = self.compute_client.virtual_machines.begin_power_off(
                    resource_group,
                    vm_name
                )
            
            poller.result()
            return True

        except Exception as e:
            logger.error(f"Error stopping VM {vm_name}: {str(e)}")
            return False

    def start_vm(self, resource_group: str, vm_name: str) -> bool:
        """Start a virtual machine."""
        try:
            poller = self.compute_client.virtual_machines.begin_start(
                resource_group,
                vm_name
            )
            
            poller.result()
            return True

        except Exception as e:
            logger.error(f"Error starting VM {vm_name}: {str(e)}")
            return False

    def update_storage_tier(self, resource_group: str, account_name: str, new_tier: str) -> bool:
        """Update storage account tier."""
        try:
            # Get storage account
            account = self.storage_client.storage_accounts.get_properties(
                resource_group,
                account_name
            )
            
            # Update tier
            parameters = {
                'sku': {
                    'name': account.sku.name,
                    'tier': new_tier
                }
            }
            
            # Start the update operation
            result = self.storage_client.storage_accounts.update(
                resource_group,
                account_name,
                parameters
            )
            
            return True

        except Exception as e:
            logger.error(f"Error updating storage tier for {account_name}: {str(e)}")
            return False

    def update_disk_size(self, resource_group: str, disk_name: str, new_size_gb: int) -> bool:
        """Update managed disk size."""
        try:
            # Get disk
            disk = self.compute_client.disks.get(resource_group, disk_name)
            
            # Update size
            disk.disk_size_gb = new_size_gb
            
            # Start the update operation
            poller = self.compute_client.disks.begin_update(
                resource_group,
                disk_name,
                disk
            )
            
            poller.result()
            return True

        except Exception as e:
            logger.error(f"Error updating disk size for {disk_name}: {str(e)}")
            return False

    def update_network_tier(self, resource_group: str, resource_name: str, resource_type: str, new_tier: str) -> bool:
        """Update network resource tier."""
        try:
            if resource_type == 'publicIPAddress':
                # Get public IP
                public_ip = self.network_client.public_ip_addresses.get(
                    resource_group,
                    resource_name
                )
                
                # Update tier
                public_ip.sku.tier = new_tier
                
                # Start the update operation
                poller = self.network_client.public_ip_addresses.begin_create_or_update(
                    resource_group,
                    resource_name,
                    public_ip
                )
                
                poller.result()
                return True
                
            elif resource_type == 'loadBalancer':
                # Get load balancer
                lb = self.network_client.load_balancers.get(
                    resource_group,
                    resource_name
                )
                
                # Update tier
                lb.sku.tier = new_tier
                
                # Start the update operation
                poller = self.network_client.load_balancers.begin_create_or_update(
                    resource_group,
                    resource_name,
                    lb
                )
                
                poller.result()
                return True

            return False

        except Exception as e:
            logger.error(f"Error updating network tier for {resource_name}: {str(e)}")
            return False

    def create_auto_shutdown_schedule(self, resource_group: str, vm_name: str, 
                                    shutdown_time: str, timezone: str) -> bool:
        """Create auto-shutdown schedule for a VM."""
        try:
            # Create schedule parameters
            schedule_name = f"{vm_name}-shutdown-schedule"
            target_resource_id = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
            
            schedule_parameters = {
                'location': 'Global',
                'properties': {
                    'targetResourceId': target_resource_id,
                    'status': 'Enabled',
                    'taskType': 'ComputeVirtualMachineShutdownTask',
                    'dailyRecurrence': {'time': shutdown_time},
                    'timeZoneId': timezone,
                    'notificationSettings': {
                        'status': 'Enabled',
                        'timeInMinutes': 30
                    }
                }
            }
            
            # Create the schedule
            result = self.resource_client.resources.begin_create_or_update(
                resource_group_name=resource_group,
                resource_provider_namespace='Microsoft.DevTestLab',
                parent_resource_path='',
                resource_type='schedules',
                resource_name=schedule_name,
                api_version='2018-09-15',
                parameters=schedule_parameters
            )
            
            result.result()
            return True

        except Exception as e:
            logger.error(f"Error creating shutdown schedule for VM {vm_name}: {str(e)}")
            return False

    def create_auto_start_schedule(self, resource_group: str, vm_name: str, 
                                 start_time: str, timezone: str) -> bool:
        """Create auto-start schedule for a VM."""
        try:
            # Create schedule parameters
            schedule_name = f"{vm_name}-start-schedule"
            target_resource_id = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
            
            schedule_parameters = {
                'location': 'Global',
                'properties': {
                    'targetResourceId': target_resource_id,
                    'status': 'Enabled',
                    'taskType': 'ComputeVirtualMachineStartTask',
                    'dailyRecurrence': {'time': start_time},
                    'timeZoneId': timezone
                }
            }
            
            # Create the schedule
            result = self.resource_client.resources.begin_create_or_update(
                resource_group_name=resource_group,
                resource_provider_namespace='Microsoft.DevTestLab',
                parent_resource_path='',
                resource_type='schedules',
                resource_name=schedule_name,
                api_version='2018-09-15',
                parameters=schedule_parameters
            )
            
            result.result()
            return True

        except Exception as e:
            logger.error(f"Error creating start schedule for VM {vm_name}: {str(e)}")
            return False

    def create_backup_policy(self, resource_group: str, resource_name: str, 
                           resource_type: str, backup_config: Dict) -> bool:
        """Create or update backup policy for a resource."""
        try:
            # Implementation depends on resource type and backup service used
            # This is a placeholder for the actual implementation
            return True

        except Exception as e:
            logger.error(f"Error creating backup policy for {resource_name}: {str(e)}")
            return False

    def create_alert_rule(self, resource_group: str, resource_name: str, 
                         metric_name: str, threshold: float, 
                         operator: str, window_size: str) -> bool:
        """Create metric alert rule for a resource."""
        try:
            # Create alert rule parameters
            rule_name = f"{resource_name}-{metric_name}-alert"
            
            alert_parameters = {
                'location': 'global',
                'properties': {
                    'description': f'Alert when {metric_name} {operator} {threshold}',
                    'severity': 2,
                    'enabled': True,
                    'scopes': [f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{resource_name}"],
                    'evaluationFrequency': 'PT5M',
                    'windowSize': window_size,
                    'criteria': {
                        'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria',
                        'allOf': [
                            {
                                'name': 'Metric1',
                                'metricName': metric_name,
                                'operator': operator,
                                'threshold': threshold,
                                'timeAggregation': 'Average'
                            }
                        ]
                    }
                }
            }
            
            # Create the alert rule
            result = self.resource_client.resources.begin_create_or_update(
                resource_group_name=resource_group,
                resource_provider_namespace='Microsoft.Insights',
                parent_resource_path='',
                resource_type='metricAlerts',
                resource_name=rule_name,
                api_version='2018-03-01',
                parameters=alert_parameters
            )
            
            result.result()
            return True

        except Exception as e:
            logger.error(f"Error creating alert rule for {resource_name}: {str(e)}")
            return False

    def apply_resource_locks(self, resource_group: str, resource_name: str, 
                           lock_level: str) -> bool:
        """Apply resource locks to prevent accidental deletion or modification."""
        try:
            # Create lock parameters
            lock_name = f"{resource_name}-lock"
            
            lock_parameters = {
                'level': lock_level,
                'notes': f'Resource lock applied by Utilization Optimizer'
            }
            
            # Create the lock
            result = self.resource_client.management_locks.create_or_update_at_resource_level(
                resource_group_name=resource_group,
                resource_provider_namespace='Microsoft.Compute',
                parent_resource_path='',
                resource_type='virtualMachines',
                resource_name=resource_name,
                lock_name=lock_name,
                parameters=lock_parameters
            )
            
            return True

        except Exception as e:
            logger.error(f"Error applying resource lock for {resource_name}: {str(e)}")
            return False
