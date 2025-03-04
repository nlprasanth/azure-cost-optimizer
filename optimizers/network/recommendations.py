from typing import Dict, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NetworkOptimizationRecommender:
    def __init__(self):
        # Thresholds for recommendations
        self.thresholds = {
            'unused_ip_days': 7,
            'lb_min_backend_count': 2,
            'lb_min_traffic_mbps': 1,
            'bandwidth_cdn_threshold_gb': 1024,  # 1TB
            'bandwidth_er_threshold_gb': 5120,   # 5TB
            'vnet_min_utilization': 0.4
        }

    def get_recommendations(self, network_analysis: Dict) -> List[Dict]:
        """Generate network optimization recommendations."""
        try:
            recommendations = []

            # Analyze different components
            ip_recs = self._get_ip_recommendations(network_analysis.get('public_ips', {}))
            recommendations.extend(ip_recs)

            lb_recs = self._get_lb_recommendations(network_analysis.get('load_balancers', {}))
            recommendations.extend(lb_recs)

            bandwidth_recs = self._get_bandwidth_recommendations(network_analysis.get('bandwidth_usage', {}))
            recommendations.extend(bandwidth_recs)

            vnet_recs = self._get_vnet_recommendations(network_analysis.get('virtual_networks', {}))
            recommendations.extend(vnet_recs)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating network recommendations: {str(e)}")
            return []

    def _get_ip_recommendations(self, ip_analysis: Dict) -> List[Dict]:
        """Generate recommendations for public IP optimization."""
        try:
            recommendations = []

            if not ip_analysis:
                return recommendations

            # Check for unused public IPs
            if ip_analysis['unused_ips'] > 0:
                recommendations.append({
                    'type': 'public_ip',
                    'action': 'remove_unused_ips',
                    'impact': 'medium',
                    'description': f'Remove {ip_analysis["unused_ips"]} unused public IP(s)',
                    'details': {
                        'unused_count': ip_analysis['unused_ips'],
                        'estimated_savings': f'${ip_analysis["unused_ips"] * 0.004 * 730:.2f}/month'  # 730 hours per month
                    },
                    'implementation_risk': 'low'
                })

            # Check for static IPs that could be dynamic
            static_ips = [ip for ip in ip_analysis['details'] if ip['allocation_method'] == 'Static']
            convertible_ips = [ip for ip in static_ips if not self._requires_static_ip(ip)]
            
            if convertible_ips:
                recommendations.append({
                    'type': 'public_ip',
                    'action': 'convert_to_dynamic',
                    'impact': 'low',
                    'description': f'Convert {len(convertible_ips)} static IP(s) to dynamic allocation',
                    'details': {
                        'convertible_ips': [ip['name'] for ip in convertible_ips],
                        'estimated_savings': f'${len(convertible_ips) * 0.002 * 730:.2f}/month'
                    },
                    'implementation_risk': 'medium'
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating IP recommendations: {str(e)}")
            return []

    def _get_lb_recommendations(self, lb_analysis: Dict) -> List[Dict]:
        """Generate recommendations for load balancer optimization."""
        try:
            recommendations = []

            if not lb_analysis:
                return recommendations

            # Check for underutilized load balancers
            if lb_analysis['underutilized'] > 0:
                recommendations.append({
                    'type': 'load_balancer',
                    'action': 'optimize_underutilized',
                    'impact': 'medium',
                    'description': f'Optimize {lb_analysis["underutilized"]} underutilized load balancer(s)',
                    'details': {
                        'underutilized_count': lb_analysis['underutilized'],
                        'suggested_actions': [
                            'Consolidate backend pools',
                            'Consider downgrading to Basic tier',
                            'Remove unused rules and probes'
                        ]
                    },
                    'implementation_risk': 'medium'
                })

            # Check for Basic tier LBs that might need Standard features
            basic_lbs = [lb for lb in lb_analysis['details'] if lb['sku'] == 'Basic']
            upgradeable_lbs = [lb for lb in basic_lbs if self._needs_standard_features(lb)]
            
            if upgradeable_lbs:
                recommendations.append({
                    'type': 'load_balancer',
                    'action': 'upgrade_to_standard',
                    'impact': 'high',
                    'description': f'Upgrade {len(upgradeable_lbs)} load balancer(s) to Standard tier for better features',
                    'details': {
                        'load_balancers': [lb['name'] for lb in upgradeable_lbs],
                        'benefits': [
                            'Zone redundancy',
                            'Better SLA',
                            'Advanced monitoring'
                        ]
                    },
                    'implementation_risk': 'medium'
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating LB recommendations: {str(e)}")
            return []

    def _get_bandwidth_recommendations(self, bandwidth_analysis: Dict) -> List[Dict]:
        """Generate recommendations for bandwidth optimization."""
        try:
            recommendations = []

            if not bandwidth_analysis:
                return recommendations

            # Check if CDN would be beneficial
            if bandwidth_analysis['total_egress_gb'] > self.thresholds['bandwidth_cdn_threshold_gb']:
                recommendations.append({
                    'type': 'bandwidth',
                    'action': 'implement_cdn',
                    'impact': 'high',
                    'description': 'Implement Azure CDN to reduce egress costs',
                    'details': {
                        'current_egress_gb': bandwidth_analysis['total_egress_gb'],
                        'estimated_savings': '40-60% on egress costs',
                        'benefits': [
                            'Reduced latency',
                            'Lower egress costs',
                            'Better user experience'
                        ]
                    },
                    'implementation_risk': 'low'
                })

            # Check if ExpressRoute would be cost-effective
            if bandwidth_analysis['total_egress_gb'] > self.thresholds['bandwidth_er_threshold_gb']:
                recommendations.append({
                    'type': 'bandwidth',
                    'action': 'consider_expressroute',
                    'impact': 'high',
                    'description': 'Consider ExpressRoute for high-bandwidth scenarios',
                    'details': {
                        'current_egress_gb': bandwidth_analysis['total_egress_gb'],
                        'benefits': [
                            'Predictable costs',
                            'Better performance',
                            'Private connectivity'
                        ]
                    },
                    'implementation_risk': 'high'
                })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating bandwidth recommendations: {str(e)}")
            return []

    def _get_vnet_recommendations(self, vnet_analysis: Dict) -> List[Dict]:
        """Generate recommendations for virtual network optimization."""
        try:
            recommendations = []

            if not vnet_analysis:
                return recommendations

            # Analyze subnet utilization
            for vnet in vnet_analysis['details']:
                # Check for potential subnet consolidation
                if len(vnet['subnets']) > 3:  # Arbitrary threshold
                    recommendations.append({
                        'type': 'vnet',
                        'action': 'optimize_subnets',
                        'impact': 'medium',
                        'description': f'Optimize subnet design in VNet {vnet["name"]}',
                        'details': {
                            'current_subnet_count': len(vnet['subnets']),
                            'suggested_actions': [
                                'Consolidate similar workload subnets',
                                'Review subnet sizing',
                                'Implement proper CIDR planning'
                            ]
                        },
                        'implementation_risk': 'high'
                    })

                # Check for missing service endpoints
                subnets_without_endpoints = [s for s in vnet['subnets'] if not s['service_endpoints']]
                if subnets_without_endpoints:
                    recommendations.append({
                        'type': 'vnet',
                        'action': 'add_service_endpoints',
                        'impact': 'medium',
                        'description': f'Implement service endpoints in VNet {vnet["name"]}',
                        'details': {
                            'affected_subnets': [s['name'] for s in subnets_without_endpoints],
                            'benefits': [
                                'Improved security',
                                'Optimal routing',
                                'Reduced public bandwidth'
                            ]
                        },
                        'implementation_risk': 'low'
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating VNet recommendations: {str(e)}")
            return []

    def _requires_static_ip(self, ip_details: Dict) -> bool:
        """Determine if a public IP requires static allocation."""
        # This would typically check the associated resource type
        # and its requirements
        return False

    def _needs_standard_features(self, lb_details: Dict) -> bool:
        """Determine if a load balancer needs Standard tier features."""
        # Check if the LB needs features only available in Standard tier
        return (
            lb_details['frontend_ip_count'] > 1 or
            lb_details['metrics']['total_packets'] > 1000000 or
            lb_details['metrics']['peak_bytes_per_second'] > 100 * 1024 * 1024  # 100 Mbps
        )

    def calculate_savings(self, network_analysis: Dict, recommendations: List[Dict]) -> Dict:
        """Calculate potential savings from recommendations."""
        try:
            savings = {
                'monthly_savings': 0,
                'annual_savings': 0,
                'one_time_savings': 0,
                'implementation_costs': 0,
                'breakdown': {
                    'public_ip': 0,
                    'load_balancer': 0,
                    'bandwidth': 0,
                    'other': 0
                }
            }

            for rec in recommendations:
                if rec['type'] == 'public_ip':
                    if 'estimated_savings' in rec['details']:
                        monthly = float(rec['details']['estimated_savings'].replace('$', '').split('/')[0])
                        savings['monthly_savings'] += monthly
                        savings['breakdown']['public_ip'] += monthly

                elif rec['type'] == 'bandwidth':
                    if 'estimated_savings' in rec['details']:
                        # Parse percentage savings
                        percentage = float(rec['details']['estimated_savings'].split('-')[0]) / 100
                        current_cost = network_analysis['bandwidth_usage']['cost_analysis']['total_cost']
                        monthly = current_cost * percentage
                        savings['monthly_savings'] += monthly
                        savings['breakdown']['bandwidth'] += monthly

            # Calculate annual savings
            savings['annual_savings'] = savings['monthly_savings'] * 12

            return savings

        except Exception as e:
            logger.error(f"Error calculating savings: {str(e)}")
            return {
                'monthly_savings': 0,
                'annual_savings': 0,
                'one_time_savings': 0,
                'implementation_costs': 0,
                'breakdown': {
                    'public_ip': 0,
                    'load_balancer': 0,
                    'bandwidth': 0,
                    'other': 0
                }
            }
