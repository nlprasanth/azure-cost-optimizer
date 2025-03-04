from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class StorageAnalyzer:
    def __init__(self, subscription_id: str):
        self.credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        self.storage_client = StorageManagementClient(self.credential, self.subscription_id)
        self.monitor_client = MonitorManagementClient(self.credential, self.subscription_id)

        # Storage tier pricing (example values per GB per month)
        self.tier_pricing = {
            'Premium': 0.15,
            'Hot': 0.0184,
            'Cool': 0.01,
            'Archive': 0.00099
        }

    def analyze_storage_account(self, resource_group: str, account_name: str) -> Dict:
        """Analyze a storage account for optimization opportunities."""
        try:
            # Get storage account details
            account = self.storage_client.storage_accounts.get_properties(
                resource_group,
                account_name
            )

            # Get metrics
            metrics = self._get_storage_metrics(account.id)

            # Get blob analytics
            blob_analytics = self._analyze_blobs(account)

            # Analyze access patterns
            access_patterns = self._analyze_access_patterns(account.id)

            return {
                'account_name': account_name,
                'resource_group': resource_group,
                'metrics': metrics,
                'blob_analytics': blob_analytics,
                'access_patterns': access_patterns,
                'current_tier': account.sku.tier,
                'current_replication': account.sku.name.split('_')[1],
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing storage account {account_name}: {str(e)}")
            return None

    def _get_storage_metrics(self, resource_id: str) -> Dict:
        """Get storage metrics for analysis."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            timespan = f"{start_time}/{end_time}"

            metrics = {
                'transactions': self._get_metric(resource_id, 'Transactions', timespan),
                'ingress': self._get_metric(resource_id, 'Ingress', timespan),
                'egress': self._get_metric(resource_id, 'Egress', timespan),
                'used_capacity': self._get_metric(resource_id, 'UsedCapacity', timespan)
            }

            return self._process_metrics(metrics)

        except Exception as e:
            logger.error(f"Error getting storage metrics: {str(e)}")
            return None

    def _get_metric(self, resource_id: str, metric_name: str, timespan: str) -> List[float]:
        """Get specific metric data."""
        try:
            metrics_data = self.monitor_client.metrics.list(
                resource_id,
                timespan=timespan,
                interval='P1D',  # Daily intervals
                metricnames=metric_name,
                aggregation='Total'
            )

            if metrics_data.value:
                return [point.total for point in metrics_data.value[0].timeseries[0].data if point.total is not None]
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
                    'total': df.sum(),
                    'average': df.mean(),
                    'peak': df.max(),
                    'trend': self._calculate_trend(df)
                }
            else:
                processed[metric] = {
                    'total': 0,
                    'average': 0,
                    'peak': 0,
                    'trend': 'stable'
                }
        return processed

    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction from time series data."""
        if len(series) < 2:
            return 'stable'
        
        # Calculate simple linear regression slope
        x = range(len(series))
        slope = pd.np.polyfit(x, series, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'

    def _analyze_blobs(self, account) -> Dict:
        """Analyze blob storage patterns and usage."""
        try:
            # Get connection string (in production, use Key Vault)
            keys = self.storage_client.storage_accounts.list_keys(
                account.resource_group_name,
                account.name
            )
            conn_string = f"DefaultEndpointsProtocol=https;AccountName={account.name};AccountKey={keys.keys[0].value};EndpointSuffix=core.windows.net"
            
            blob_service = BlobServiceClient.from_connection_string(conn_string)
            
            containers = blob_service.list_containers()
            container_stats = []

            for container in containers:
                container_client = blob_service.get_container_client(container.name)
                blobs = container_client.list_blobs()
                
                container_data = {
                    'name': container.name,
                    'blob_count': 0,
                    'total_size': 0,
                    'last_modified_distribution': {
                        'last_24h': 0,
                        'last_week': 0,
                        'last_month': 0,
                        'last_year': 0,
                        'older': 0
                    }
                }

                for blob in blobs:
                    container_data['blob_count'] += 1
                    container_data['total_size'] += blob.size
                    
                    # Analyze last modified distribution
                    age = datetime.utcnow() - blob.last_modified
                    if age < timedelta(days=1):
                        container_data['last_modified_distribution']['last_24h'] += 1
                    elif age < timedelta(days=7):
                        container_data['last_modified_distribution']['last_week'] += 1
                    elif age < timedelta(days=30):
                        container_data['last_modified_distribution']['last_month'] += 1
                    elif age < timedelta(days=365):
                        container_data['last_modified_distribution']['last_year'] += 1
                    else:
                        container_data['last_modified_distribution']['older'] += 1

                container_stats.append(container_data)

            return {
                'container_count': len(container_stats),
                'containers': container_stats
            }

        except Exception as e:
            logger.error(f"Error analyzing blobs: {str(e)}")
            return None

    def _analyze_access_patterns(self, resource_id: str) -> Dict:
        """Analyze storage access patterns."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            timespan = f"{start_time}/{end_time}"

            # Get hourly access patterns
            hourly_metrics = self.monitor_client.metrics.list(
                resource_id,
                timespan=timespan,
                interval='PT1H',
                metricnames='Transactions',
                aggregation='Total'
            )

            # Process hourly patterns
            hourly_pattern = [0] * 24
            if hourly_metrics.value:
                for point in hourly_metrics.value[0].timeseries[0].data:
                    if point.total is not None:
                        hour = point.timestamp.hour
                        hourly_pattern[hour] += point.total

            return {
                'hourly_pattern': hourly_pattern,
                'peak_hour': hourly_pattern.index(max(hourly_pattern)),
                'off_peak_hours': [i for i, v in enumerate(hourly_pattern) if v < sum(hourly_pattern)/len(hourly_pattern)/2]
            }

        except Exception as e:
            logger.error(f"Error analyzing access patterns: {str(e)}")
            return None
