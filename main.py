from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.advisor import AdvisorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
import os
from dotenv import load_dotenv
import pandas as pd
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureCostOptimizer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Azure credentials
        self.credential = DefaultAzureCredential()
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        
        # Initialize subscription client
        self.subscription_client = SubscriptionClient(self.credential)
        
        # Get list of subscriptions if no specific subscription_id provided
        self.subscriptions = []
        if not self.subscription_id:
            logger.info("No subscription ID provided. Getting all accessible subscriptions...")
            try:
                for sub in self.subscription_client.subscriptions.list():
                    self.subscriptions.append({
                        'id': sub.subscription_id,
                        'name': sub.display_name,
                        'state': sub.state
                    })
                logger.info(f"Found {len(self.subscriptions)} accessible subscriptions")
            except Exception as e:
                logger.error(f"Error getting subscriptions: {str(e)}")
                raise
        else:
            self.subscriptions = [{
                'id': self.subscription_id,
                'name': 'Specified Subscription',
                'state': 'Enabled'
            }]

        # Initialize clients dictionary for each subscription
        self.clients = {}
        for sub in self.subscriptions:
            sub_id = sub['id']
            try:
                self.clients[sub_id] = {
                    'cost': CostManagementClient(self.credential, sub_id),
                    'monitor': MonitorManagementClient(self.credential, sub_id),
                    'advisor': AdvisorManagementClient(self.credential, sub_id),
                    'resource': ResourceManagementClient(self.credential, sub_id)
                }
            except Exception as e:
                logger.error(f"Error initializing clients for subscription {sub_id}: {str(e)}")
                continue

    def get_cost_analysis(self, timeframe='Last30Days'):
        """Get cost analysis for all subscriptions or specified subscription"""
        all_cost_data = []
        
        for sub in self.subscriptions:
            sub_id = sub['id']
            try:
                # Get cost data for each subscription
                scope = f"/subscriptions/{sub_id}"
                
                # Define time period
                today = datetime.utcnow()
                if timeframe == 'Last30Days':
                    from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
                    to_date = today.strftime('%Y-%m-%d')
                
                # Query cost data
                cost_data = self.clients[sub_id]['cost'].query.usage(
                    scope=scope,
                    parameters={
                        'type': 'ActualCost',
                        'timeframe': timeframe,
                        'dataset': {
                            'granularity': 'Daily',
                            'aggregation': {
                                'totalCost': {
                                    'name': 'Cost',
                                    'function': 'Sum'
                                }
                            },
                            'grouping': [
                                {'type': 'Dimension', 'name': 'ResourceGroup'},
                                {'type': 'Dimension', 'name': 'ResourceType'}
                            ]
                        }
                    }
                )
                
                all_cost_data.append({
                    'subscription_id': sub_id,
                    'subscription_name': sub['name'],
                    'cost_data': cost_data
                })
                
            except Exception as e:
                logger.error(f"Error getting cost analysis for subscription {sub_id}: {str(e)}")
                continue
        
        return all_cost_data

    def get_resource_utilization(self):
        """Get resource utilization metrics for all subscriptions"""
        all_utilization_data = []
        
        for sub in self.subscriptions:
            sub_id = sub['id']
            try:
                # Get list of VMs for this subscription
                vms = self.clients[sub_id]['resource'].resources.list(
                    filter="resourceType eq 'Microsoft.Compute/virtualMachines'"
                )
                
                sub_utilization_data = []
                for vm in vms:
                    # Get CPU and memory metrics
                    metrics = self.clients[sub_id]['monitor'].metrics.list(
                        resource_uri=vm.id,
                        timespan=f"{datetime.utcnow() - timedelta(days=7)}/{datetime.utcnow()}",
                        interval='PT1H',
                        metricnames='Percentage CPU,Available Memory Bytes',
                        aggregation='Average'
                    )
                    
                    sub_utilization_data.append({
                        'vm_name': vm.name,
                        'metrics': metrics
                    })
                
                all_utilization_data.append({
                    'subscription_id': sub_id,
                    'subscription_name': sub['name'],
                    'utilization_data': sub_utilization_data
                })
                
            except Exception as e:
                logger.error(f"Error getting resource utilization for subscription {sub_id}: {str(e)}")
                continue
        
        return all_utilization_data

    def get_advisor_recommendations(self):
        """Get Azure Advisor recommendations for all subscriptions"""
        all_recommendations = []
        
        for sub in self.subscriptions:
            sub_id = sub['id']
            try:
                recommendations = self.clients[sub_id]['advisor'].recommendations.list()
                all_recommendations.append({
                    'subscription_id': sub_id,
                    'subscription_name': sub['name'],
                    'recommendations': [rec.as_dict() for rec in recommendations]
                })
            except Exception as e:
                logger.error(f"Error getting advisor recommendations for subscription {sub_id}: {str(e)}")
                continue
        
        return all_recommendations

    def analyze_optimization_opportunities(self):
        """Analyze and return optimization opportunities for all subscriptions"""
        all_opportunities = {}
        
        for sub in self.subscriptions:
            sub_id = sub['id']
            all_opportunities[sub_id] = {
                'subscription_name': sub['name'],
                'opportunities': {
                    'cost_savings': [],
                    'performance_improvements': [],
                    'security_recommendations': []
                }
            }
            
            # Get advisor recommendations for this subscription
            try:
                recommendations = self.clients[sub_id]['advisor'].recommendations.list()
                for rec in recommendations:
                    rec_dict = rec.as_dict()
                    if rec_dict.get('category') == 'Cost':
                        all_opportunities[sub_id]['opportunities']['cost_savings'].append({
                            'description': rec_dict.get('shortDescription', {}).get('solution'),
                            'impact': rec_dict.get('impact'),
                            'resource': rec_dict.get('resourceId')
                        })
            except Exception as e:
                logger.error(f"Error analyzing recommendations for subscription {sub_id}: {str(e)}")
            
            # Analyze resource utilization for this subscription
            try:
                utilization = self.get_resource_utilization()
                for sub_data in utilization:
                    if sub_data['subscription_id'] == sub_id:
                        for vm_data in sub_data['utilization_data']:
                            if self._is_underutilized(vm_data):
                                all_opportunities[sub_id]['opportunities']['cost_savings'].append({
                                    'description': f"VM {vm_data['vm_name']} is underutilized. Consider downsizing or using spot instances.",
                                    'impact': 'Medium',
                                    'resource': vm_data['vm_name']
                                })
            except Exception as e:
                logger.error(f"Error analyzing utilization for subscription {sub_id}: {str(e)}")
        
        return all_opportunities

    def _is_underutilized(self, vm_data):
        """Check if a VM is underutilized"""
        # Implementation would analyze CPU, memory, and other metrics
        # This is a placeholder for the actual implementation
        return False

def main():
    optimizer = AzureCostOptimizer()
    
    # Get cost analysis
    logger.info("Getting cost analysis...")
    cost_data = optimizer.get_cost_analysis()
    
    # Get optimization opportunities
    logger.info("Analyzing optimization opportunities...")
    opportunities = optimizer.analyze_optimization_opportunities()
    
    # Log findings
    logger.info("Analysis complete. Found opportunities:")
    for sub_id, sub_data in opportunities.items():
        logger.info(f"\nSubscription: {sub_data['subscription_name']} ({sub_id})")
        for category, items in sub_data['opportunities'].items():
            if items:
                logger.info(f"\n{category.upper()}:")
                for item in items:
                    logger.info(f"- {item['description']}")

if __name__ == "__main__":
    main()
