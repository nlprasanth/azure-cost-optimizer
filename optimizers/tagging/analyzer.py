from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import TagDetails
from azure.identity import DefaultAzureCredential
import pandas as pd
from collections import defaultdict
import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

class TaggingAnalyzer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)

        # Standard tag categories
        self.tag_categories = {
            'ownership': ['owner', 'team', 'department', 'contact'],
            'technical': ['environment', 'application', 'service', 'role'],
            'business': ['project', 'cost-center', 'business-unit', 'customer'],
            'security': ['security-level', 'compliance', 'data-classification'],
            'automation': ['auto-shutdown', 'backup-policy', 'maintenance-window'],
            'lifecycle': ['created-by', 'created-date', 'expiry-date', 'temporary']
        }

        # Required tags (customize as needed)
        self.required_tags = ['environment', 'owner', 'cost-center', 'project']

    def analyze_resource_tags(self) -> Dict:
        """Analyze resource tagging across the subscription."""
        try:
            # Get all resources
            resources = list(self.resource_client.resources.list())
            
            # Get subscription level tags
            subscription_tags = self._get_subscription_tags()
            
            # Analyze tags
            analysis = {
                'resource_count': len(resources),
                'tag_coverage': self._analyze_tag_coverage(resources),
                'tag_consistency': self._analyze_tag_consistency(resources),
                'tag_categories': self._analyze_tag_categories(resources),
                'subscription_tags': subscription_tags,
                'compliance': self._analyze_compliance(resources),
                'tag_patterns': self._analyze_tag_patterns(resources),
                'value_standardization': self._analyze_value_standardization(resources)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing resource tags: {str(e)}")
            return None

    def _get_subscription_tags(self) -> Dict:
        """Get subscription level tags."""
        try:
            subscription_scope = f'/subscriptions/{self.subscription_id}'
            tags = self.resource_client.tags.list()
            
            return {
                'count': len(tags.value),
                'tags': {tag.tag_name: tag.values for tag in tags.value},
                'predefined_values': {
                    tag.tag_name: [value.tag_value for value in tag.values]
                    for tag in tags.value if tag.values
                }
            }

        except Exception as e:
            logger.error(f"Error getting subscription tags: {str(e)}")
            return {}

    def _analyze_tag_coverage(self, resources: List) -> Dict:
        """Analyze tag coverage across resources."""
        try:
            total_resources = len(resources)
            if total_resources == 0:
                return {}

            coverage = {
                'tagged_resources': 0,
                'untagged_resources': 0,
                'average_tags_per_resource': 0,
                'tag_distribution': {},
                'resource_types': defaultdict(lambda: {'tagged': 0, 'untagged': 0})
            }

            total_tags = 0
            for resource in resources:
                tags = resource.tags or {}
                resource_type = resource.type.split('/')[-1]
                
                if tags:
                    coverage['tagged_resources'] += 1
                    coverage['resource_types'][resource_type]['tagged'] += 1
                else:
                    coverage['untagged_resources'] += 1
                    coverage['resource_types'][resource_type]['untagged'] += 1
                
                total_tags += len(tags)
                
                # Track tag count distribution
                tag_count = len(tags)
                coverage['tag_distribution'][tag_count] = coverage['tag_distribution'].get(tag_count, 0) + 1

            coverage['average_tags_per_resource'] = total_tags / total_resources
            coverage['coverage_percentage'] = (coverage['tagged_resources'] / total_resources) * 100

            return coverage

        except Exception as e:
            logger.error(f"Error analyzing tag coverage: {str(e)}")
            return {}

    def _analyze_tag_consistency(self, resources: List) -> Dict:
        """Analyze consistency of tag usage."""
        try:
            consistency = {
                'tag_frequency': defaultdict(int),
                'value_frequency': defaultdict(lambda: defaultdict(int)),
                'case_inconsistencies': defaultdict(set),
                'format_inconsistencies': defaultdict(set)
            }

            for resource in resources:
                tags = resource.tags or {}
                for key, value in tags.items():
                    # Track tag frequency
                    consistency['tag_frequency'][key.lower()] += 1
                    
                    # Track value frequency
                    consistency['value_frequency'][key.lower()][value.lower()] += 1
                    
                    # Check for case inconsistencies in keys
                    consistency['case_inconsistencies'][key.lower()].add(key)
                    
                    # Check for format inconsistencies in values
                    if self._is_date_format(value):
                        consistency['format_inconsistencies'][key.lower()].add('date')
                    elif self._is_email_format(value):
                        consistency['format_inconsistencies'][key.lower()].add('email')

            # Convert defaultdict to regular dict for serialization
            return {
                'tag_frequency': dict(consistency['tag_frequency']),
                'value_frequency': {k: dict(v) for k, v in consistency['value_frequency'].items()},
                'case_inconsistencies': {
                    k: list(v) for k, v in consistency['case_inconsistencies'].items() 
                    if len(v) > 1
                },
                'format_inconsistencies': {
                    k: list(v) for k, v in consistency['format_inconsistencies'].items()
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing tag consistency: {str(e)}")
            return {}

    def _analyze_tag_categories(self, resources: List) -> Dict:
        """Analyze tags by category."""
        try:
            categories = {
                category: {
                    'coverage': 0,
                    'missing_tags': [],
                    'used_tags': set()
                }
                for category in self.tag_categories
            }

            for resource in resources:
                tags = resource.tags or {}
                for category, expected_tags in self.tag_categories.items():
                    present_tags = [
                        tag for tag in expected_tags 
                        if any(t.lower() in tag.lower() for t in tags.keys())
                    ]
                    categories[category]['used_tags'].update(present_tags)
                    
                    if present_tags:
                        categories[category]['coverage'] += 1

            # Calculate percentages and format results
            total_resources = len(resources)
            for category in categories:
                categories[category]['coverage'] = (
                    categories[category]['coverage'] / total_resources * 100
                    if total_resources > 0 else 0
                )
                categories[category]['missing_tags'] = [
                    tag for tag in self.tag_categories[category]
                    if tag not in categories[category]['used_tags']
                ]
                categories[category]['used_tags'] = list(categories[category]['used_tags'])

            return categories

        except Exception as e:
            logger.error(f"Error analyzing tag categories: {str(e)}")
            return {}

    def _analyze_compliance(self, resources: List) -> Dict:
        """Analyze compliance with required tags."""
        try:
            compliance = {
                'overall_compliance': 0,
                'non_compliant_resources': [],
                'missing_required_tags': defaultdict(list),
                'compliance_by_type': defaultdict(lambda: {'compliant': 0, 'non_compliant': 0})
            }

            compliant_resources = 0
            for resource in resources:
                tags = resource.tags or {}
                resource_type = resource.type.split('/')[-1]
                
                # Check for required tags
                missing_tags = [
                    tag for tag in self.required_tags 
                    if not any(t.lower() == tag.lower() for t in tags.keys())
                ]
                
                if not missing_tags:
                    compliant_resources += 1
                    compliance['compliance_by_type'][resource_type]['compliant'] += 1
                else:
                    compliance['non_compliant_resources'].append({
                        'id': resource.id,
                        'name': resource.name,
                        'type': resource_type,
                        'missing_tags': missing_tags
                    })
                    compliance['compliance_by_type'][resource_type]['non_compliant'] += 1
                    
                    # Track missing tags
                    for tag in missing_tags:
                        compliance['missing_required_tags'][tag].append(resource.name)

            total_resources = len(resources)
            compliance['overall_compliance'] = (
                compliant_resources / total_resources * 100 
                if total_resources > 0 else 0
            )

            return compliance

        except Exception as e:
            logger.error(f"Error analyzing compliance: {str(e)}")
            return {}

    def _analyze_tag_patterns(self, resources: List) -> Dict:
        """Analyze common tag patterns and combinations."""
        try:
            patterns = {
                'common_combinations': defaultdict(int),
                'co_occurrence': defaultdict(lambda: defaultdict(int)),
                'resource_type_patterns': defaultdict(lambda: defaultdict(int))
            }

            for resource in resources:
                tags = resource.tags or {}
                resource_type = resource.type.split('/')[-1]
                
                # Analyze tag combinations
                tag_set = frozenset(tags.keys())
                if tag_set:
                    patterns['common_combinations'][tag_set] += 1
                
                # Analyze tag co-occurrence
                for tag1 in tags:
                    for tag2 in tags:
                        if tag1 < tag2:  # Avoid counting both (a,b) and (b,a)
                            patterns['co_occurrence'][tag1][tag2] += 1
                
                # Analyze patterns by resource type
                patterns['resource_type_patterns'][resource_type][tag_set] += 1

            # Convert to serializable format
            return {
                'common_combinations': [
                    {'tags': list(tags), 'count': count}
                    for tags, count in sorted(
                        patterns['common_combinations'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]  # Top 10 combinations
                ],
                'co_occurrence': {
                    tag1: dict(co_tags)
                    for tag1, co_tags in patterns['co_occurrence'].items()
                },
                'resource_type_patterns': {
                    r_type: [
                        {'tags': list(tags), 'count': count}
                        for tags, count in sorted(
                            patterns.items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:5]  # Top 5 patterns per resource type
                    ]
                    for r_type, patterns in patterns['resource_type_patterns'].items()
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing tag patterns: {str(e)}")
            return {}

    def _analyze_value_standardization(self, resources: List) -> Dict:
        """Analyze standardization of tag values."""
        try:
            standardization = {
                'value_formats': defaultdict(lambda: defaultdict(int)),
                'value_lengths': defaultdict(list),
                'special_characters': defaultdict(set),
                'case_variations': defaultdict(set)
            }

            for resource in resources:
                tags = resource.tags or {}
                for key, value in tags.items():
                    # Analyze value format
                    if self._is_date_format(value):
                        standardization['value_formats'][key]['date'] += 1
                    elif self._is_email_format(value):
                        standardization['value_formats'][key]['email'] += 1
                    elif value.isdigit():
                        standardization['value_formats'][key]['numeric'] += 1
                    else:
                        standardization['value_formats'][key]['text'] += 1

                    # Track value lengths
                    standardization['value_lengths'][key].append(len(value))

                    # Track special characters
                    special_chars = set(c for c in value if not c.isalnum() and not c.isspace())
                    if special_chars:
                        standardization['special_characters'][key].update(special_chars)

                    # Track case variations
                    standardization['case_variations'][key].add(self._get_case_type(value))

            # Process value lengths
            value_length_stats = {}
            for key, lengths in standardization['value_lengths'].items():
                value_length_stats[key] = {
                    'min': min(lengths),
                    'max': max(lengths),
                    'avg': sum(lengths) / len(lengths)
                }

            return {
                'value_formats': {
                    k: dict(v) for k, v in standardization['value_formats'].items()
                },
                'value_lengths': value_length_stats,
                'special_characters': {
                    k: list(v) for k, v in standardization['special_characters'].items()
                },
                'case_variations': {
                    k: list(v) for k, v in standardization['case_variations'].items()
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing value standardization: {str(e)}")
            return {}

    def _is_date_format(self, value: str) -> bool:
        """Check if value appears to be a date."""
        try:
            # Simple check for common date formats
            date_indicators = ['/', '-', 'date', 'created', 'modified', 'expires']
            return any(indicator in value.lower() for indicator in date_indicators)
        except:
            return False

    def _is_email_format(self, value: str) -> bool:
        """Check if value appears to be an email."""
        try:
            return '@' in value and '.' in value.split('@')[1]
        except:
            return False

    def _get_case_type(self, value: str) -> str:
        """Determine the case type of a string."""
        if value.isupper():
            return 'UPPER'
        elif value.islower():
            return 'lower'
        elif value.istitle():
            return 'Title'
        elif '_' in value and value.islower():
            return 'snake_case'
        elif '-' in value and value.islower():
            return 'kebab-case'
        elif ''.join(c for c in value if c.isalpha()).istitle():
            return 'PascalCase'
        elif value[0].islower() and ''.join(c for c in value if c.isalpha())[1:].istitle():
            return 'camelCase'
        return 'mixed'
