from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    def __init__(self, subscription_id: str):
        self.credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        self.network_client = NetworkManagementClient(self.credential, self.subscription_id)
        self.monitor_client = MonitorManagementClient(self.credential, self.subscription_id)

        # Network service pricing (example values)
        self.pricing = {
            'bandwidth': {
                'ingress': 0.0,  # Ingress is typically free
                'egress': {
                    'zone1': 0.087,  # Per GB for first 10TB
                    'zone2': 0.083,  # Per GB for next 40TB
                    'zone3': 0.07    # Per GB for next 100TB
                }
            },
            'public_ip': {
                'static': 0.004,  # Per hour
                'dynamic': 0.002   # Per hour
            },
            'load_balancer': {
                'standard': 0.025,  # Per hour
                'basic': 0.0     # Free
            }
        }

    def analyze_network_resources(self, resource_group: str) -> Dict:
        """Analyze network resources and their usage patterns."""
        try:
            # Analyze different network components
            public_ips = self._analyze_public_ips(resource_group)
            load_balancers = self._analyze_load_balancers(resource_group)
            vnets = self._analyze_virtual_networks(resource_group)
            bandwidth = self._analyze_bandwidth_usage(resource_group)
            
            return {
                'resource_group': resource_group,
                'public_ips': public_ips,
                'load_balancers': load_balancers,
                'virtual_networks': vnets,
                'bandwidth_usage': bandwidth,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing network resources: {str(e)}")
            return None

    def _analyze_public_ips(self, resource_group: str) -> Dict:
        """Analyze public IP addresses usage."""
        try:
            public_ips = self.network_client.public_ip_addresses.list(resource_group)
            
            analysis = {
                'total_count': 0,
                'static_ips': 0,
                'dynamic_ips': 0,
                'unused_ips': 0,
                'details': []
            }

            for ip in public_ips:
                analysis['total_count'] += 1
                
                ip_details = {
                    'name': ip.name,
                    'allocation_method': ip.public_ip_allocation_method,
                    'sku': ip.sku.name if ip.sku else 'Basic',
                    'associated_resource': self._get_associated_resource(ip)
                }

                if ip.public_ip_allocation_method == 'Static':
                    analysis['static_ips'] += 1
                else:
                    analysis['dynamic_ips'] += 1

                if not ip_details['associated_resource']:
                    analysis['unused_ips'] += 1

                analysis['details'].append(ip_details)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing public IPs: {str(e)}")
            return None

    def _analyze_load_balancers(self, resource_group: str) -> Dict:
        """Analyze load balancer configuration and usage."""
        try:
            load_balancers = self.network_client.load_balancers.list(resource_group)
            
            analysis = {
                'total_count': 0,
                'standard_tier': 0,
                'basic_tier': 0,
                'underutilized': 0,
                'details': []
            }

            for lb in load_balancers:
                analysis['total_count'] += 1
                
                # Analyze load balancer details
                lb_details = {
                    'name': lb.name,
                    'sku': lb.sku.name,
                    'frontend_ip_count': len(lb.frontend_ip_configurations) if lb.frontend_ip_configurations else 0,
                    'backend_pool_count': len(lb.backend_address_pools) if lb.backend_address_pools else 0,
                    'rules_count': len(lb.load_balancing_rules) if lb.load_balancing_rules else 0,
                    'metrics': self._get_lb_metrics(lb.id)
                }

                if lb.sku.name == 'Standard':
                    analysis['standard_tier'] += 1
                else:
                    analysis['basic_tier'] += 1

                # Check for underutilization
                if self._is_lb_underutilized(lb_details):
                    analysis['underutilized'] += 1

                analysis['details'].append(lb_details)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing load balancers: {str(e)}")
            return None

    def _analyze_virtual_networks(self, resource_group: str) -> Dict:
        """Analyze virtual networks configuration."""
        try:
            vnets = self.network_client.virtual_networks.list(resource_group)
            
            analysis = {
                'total_count': 0,
                'subnet_count': 0,
                'address_space_usage': [],
                'details': []
            }

            for vnet in vnets:
                analysis['total_count'] += 1
                
                vnet_details = {
                    'name': vnet.name,
                    'address_space': [space for space in vnet.address_space.address_prefixes],
                    'subnet_count': len(vnet.subnets) if vnet.subnets else 0,
                    'subnets': self._analyze_subnets(vnet.subnets) if vnet.subnets else [],
                    'peerings': self._analyze_peerings(vnet.virtual_network_peerings) if vnet.virtual_network_peerings else []
                }

                analysis['subnet_count'] += vnet_details['subnet_count']
                analysis['details'].append(vnet_details)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing virtual networks: {str(e)}")
            return None

    def _analyze_bandwidth_usage(self, resource_group: str) -> Dict:
        """Analyze bandwidth usage patterns."""
        try:
            # Get all network interfaces in the resource group
            nics = self.network_client.network_interfaces.list(resource_group)
            
            analysis = {
                'total_ingress_gb': 0,
                'total_egress_gb': 0,
                'peak_bandwidth_mbps': 0,
                'average_bandwidth_mbps': 0,
                'cost_analysis': {
                    'ingress_cost': 0,  # Usually free
                    'egress_cost': 0
                },
                'hourly_patterns': [],
                'details': []
            }

            for nic in nics:
                metrics = self._get_bandwidth_metrics(nic.id)
                if metrics:
                    analysis['total_ingress_gb'] += metrics['total_ingress_gb']
                    analysis['total_egress_gb'] += metrics['total_egress_gb']
                    analysis['peak_bandwidth_mbps'] = max(
                        analysis['peak_bandwidth_mbps'],
                        metrics['peak_bandwidth_mbps']
                    )
                    analysis['details'].append({
                        'nic_name': nic.name,
                        'metrics': metrics
                    })

            # Calculate costs
            analysis['cost_analysis'] = self._calculate_bandwidth_costs(
                analysis['total_egress_gb']
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing bandwidth usage: {str(e)}")
            return None

    def _get_associated_resource(self, ip) -> str:
        """Get the resource associated with a public IP."""
        if hasattr(ip, 'ip_configuration') and ip.ip_configuration:
            return ip.ip_configuration.id.split('/')[-1]
        return None

    def _get_lb_metrics(self, lb_id: str) -> Dict:
        """Get load balancer performance metrics."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            timespan = f"{start_time}/{end_time}"

            metrics = self.monitor_client.metrics.list(
                lb_id,
                timespan=timespan,
                interval='PT1H',
                metricnames='DipAvailability,VipAvailability,ByteCount,PacketCount',
                aggregation='Average,Maximum'
            )

            return self._process_lb_metrics(metrics)

        except Exception as e:
            logger.error(f"Error getting LB metrics: {str(e)}")
            return None

    def _get_bandwidth_metrics(self, nic_id: str) -> Dict:
        """Get bandwidth usage metrics for a network interface."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            timespan = f"{start_time}/{end_time}"

            metrics = self.monitor_client.metrics.list(
                nic_id,
                timespan=timespan,
                interval='PT1H',
                metricnames='BytesInOut',
                aggregation='Total,Maximum'
            )

            return self._process_bandwidth_metrics(metrics)

        except Exception as e:
            logger.error(f"Error getting bandwidth metrics: {str(e)}")
            return None

    def _process_lb_metrics(self, metrics) -> Dict:
        """Process load balancer metrics into useful statistics."""
        processed = {
            'availability': 0,
            'total_bytes': 0,
            'total_packets': 0,
            'peak_bytes_per_second': 0
        }

        for metric in metrics.value:
            if metric.name.value == 'DipAvailability':
                processed['availability'] = sum(p.average for p in metric.timeseries[0].data if p.average is not None) / len(metric.timeseries[0].data)
            elif metric.name.value == 'ByteCount':
                processed['total_bytes'] = sum(p.total for p in metric.timeseries[0].data if p.total is not None)
                processed['peak_bytes_per_second'] = max(p.maximum for p in metric.timeseries[0].data if p.maximum is not None)
            elif metric.name.value == 'PacketCount':
                processed['total_packets'] = sum(p.total for p in metric.timeseries[0].data if p.total is not None)

        return processed

    def _process_bandwidth_metrics(self, metrics) -> Dict:
        """Process bandwidth metrics into useful statistics."""
        processed = {
            'total_ingress_gb': 0,
            'total_egress_gb': 0,
            'peak_bandwidth_mbps': 0,
            'average_bandwidth_mbps': 0
        }

        if metrics.value:
            bytes_data = [p.total for p in metrics.value[0].timeseries[0].data if p.total is not None]
            max_bytes = max(p.maximum for p in metrics.value[0].timeseries[0].data if p.maximum is not None)
            
            processed['total_ingress_gb'] = sum(bytes_data) / (2 * 1024 * 1024 * 1024)  # Divide by 2 as BytesInOut combines both
            processed['total_egress_gb'] = processed['total_ingress_gb']  # Simplified assumption
            processed['peak_bandwidth_mbps'] = max_bytes * 8 / (1024 * 1024)  # Convert bytes/sec to Mbps
            processed['average_bandwidth_mbps'] = (sum(bytes_data) / len(bytes_data)) * 8 / (1024 * 1024)

        return processed

    def _is_lb_underutilized(self, lb_details: Dict) -> bool:
        """Determine if a load balancer is underutilized."""
        if not lb_details.get('metrics'):
            return False

        # Consider a load balancer underutilized if:
        # 1. Less than 2 backend pools
        # 2. Less than 1000 packets per day on average
        # 3. Less than 1MB/s peak bandwidth
        return (
            lb_details['backend_pool_count'] < 2 or
            lb_details['metrics']['total_packets'] < 1000 * 30 or
            lb_details['metrics']['peak_bytes_per_second'] < 1024 * 1024
        )

    def _analyze_subnets(self, subnets) -> List[Dict]:
        """Analyze subnet configuration and usage."""
        subnet_analysis = []
        for subnet in subnets:
            subnet_analysis.append({
                'name': subnet.name,
                'address_prefix': subnet.address_prefix,
                'network_security_group': bool(subnet.network_security_group),
                'route_table': bool(subnet.route_table),
                'service_endpoints': [ep.service for ep in subnet.service_endpoints] if subnet.service_endpoints else []
            })
        return subnet_analysis

    def _analyze_peerings(self, peerings) -> List[Dict]:
        """Analyze virtual network peerings."""
        peering_analysis = []
        for peering in peerings:
            peering_analysis.append({
                'name': peering.name,
                'remote_network': peering.remote_virtual_network.id,
                'use_remote_gateways': peering.use_remote_gateways,
                'allow_forwarded_traffic': peering.allow_forwarded_traffic,
                'state': peering.peering_state
            })
        return peering_analysis

    def _calculate_bandwidth_costs(self, total_egress_gb: float) -> Dict:
        """Calculate bandwidth costs based on usage."""
        cost = 0
        remaining_gb = total_egress_gb

        # First 10TB
        if remaining_gb > 0:
            tier1_gb = min(remaining_gb, 10 * 1024)  # 10TB in GB
            cost += tier1_gb * self.pricing['bandwidth']['egress']['zone1']
            remaining_gb -= tier1_gb

        # Next 40TB
        if remaining_gb > 0:
            tier2_gb = min(remaining_gb, 40 * 1024)  # 40TB in GB
            cost += tier2_gb * self.pricing['bandwidth']['egress']['zone2']
            remaining_gb -= tier2_gb

        # Remaining
        if remaining_gb > 0:
            cost += remaining_gb * self.pricing['bandwidth']['egress']['zone3']

        return {
            'total_cost': cost,
            'cost_per_gb': cost / total_egress_gb if total_egress_gb > 0 else 0
        }
