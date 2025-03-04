from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import TagsPatchResource, TagsResource
from azure.identity import DefaultAzureCredential
import logging
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

class TagManager:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)

    def apply_tags(self, resource_id: str, tags: Dict[str, str], merge: bool = True) -> bool:
        """Apply tags to a resource."""
        try:
            # Get existing tags if merging
            if merge:
                resource = self.resource_client.resources.get_by_id(resource_id, '2021-04-01')
                existing_tags = resource.tags or {}
                tags = {**existing_tags, **tags}  # Merge existing with new tags

            # Update resource tags
            parameters = TagsPatchResource(
                operation='Merge' if merge else 'Replace',
                properties=TagsResource(tags=tags)
            )

            self.resource_client.tags.update_at_scope(resource_id, parameters)
            return True

        except Exception as e:
            logger.error(f"Error applying tags to resource {resource_id}: {str(e)}")
            return False

    def apply_bulk_tags(self, resources: List[Dict], tags: Dict[str, str], merge: bool = True) -> Dict:
        """Apply tags to multiple resources."""
        try:
            results = {
                'successful': [],
                'failed': []
            }

            for resource in resources:
                success = self.apply_tags(resource['id'], tags, merge)
                if success:
                    results['successful'].append(resource['id'])
                else:
                    results['failed'].append(resource['id'])

            return results

        except Exception as e:
            logger.error(f"Error applying bulk tags: {str(e)}")
            return {'successful': [], 'failed': []}

    def remove_tags(self, resource_id: str, tag_names: List[str]) -> bool:
        """Remove specific tags from a resource."""
        try:
            # Get existing tags
            resource = self.resource_client.resources.get_by_id(resource_id, '2021-04-01')
            existing_tags = resource.tags or {}

            # Remove specified tags
            updated_tags = {
                k: v for k, v in existing_tags.items()
                if k not in tag_names
            }

            # Update resource tags
            parameters = TagsPatchResource(
                operation='Replace',
                properties=TagsResource(tags=updated_tags)
            )

            self.resource_client.tags.update_at_scope(resource_id, parameters)
            return True

        except Exception as e:
            logger.error(f"Error removing tags from resource {resource_id}: {str(e)}")
            return False

    def standardize_tags(self, resource_id: str, standardization_rules: Dict) -> bool:
        """Standardize tags according to defined rules."""
        try:
            # Get existing tags
            resource = self.resource_client.resources.get_by_id(resource_id, '2021-04-01')
            existing_tags = resource.tags or {}

            # Apply standardization rules
            standardized_tags = {}
            for key, value in existing_tags.items():
                # Standardize key
                std_key = self._standardize_key(key, standardization_rules)
                
                # Standardize value
                std_value = self._standardize_value(value, standardization_rules)
                
                standardized_tags[std_key] = std_value

            # Update resource tags
            return self.apply_tags(resource_id, standardized_tags, merge=False)

        except Exception as e:
            logger.error(f"Error standardizing tags for resource {resource_id}: {str(e)}")
            return False

    def _standardize_key(self, key: str, rules: Dict) -> str:
        """Standardize tag key according to rules."""
        try:
            std_key = key.lower()  # Convert to lowercase

            # Apply key mappings if defined
            if 'key_mappings' in rules:
                std_key = rules['key_mappings'].get(std_key, std_key)

            # Apply key format
            if 'key_format' in rules:
                if rules['key_format'] == 'kebab-case':
                    std_key = std_key.replace('_', '-')
                elif rules['key_format'] == 'snake_case':
                    std_key = std_key.replace('-', '_')
                elif rules['key_format'] == 'camelCase':
                    parts = std_key.replace('-', '_').split('_')
                    std_key = parts[0] + ''.join(p.capitalize() for p in parts[1:])

            return std_key

        except Exception as e:
            logger.error(f"Error standardizing key {key}: {str(e)}")
            return key

    def _standardize_value(self, value: str, rules: Dict) -> str:
        """Standardize tag value according to rules."""
        try:
            std_value = value

            # Apply value mappings if defined
            if 'value_mappings' in rules:
                std_value = rules['value_mappings'].get(value.lower(), value)

            # Apply value format
            if 'value_format' in rules:
                if rules['value_format'] == 'lower':
                    std_value = std_value.lower()
                elif rules['value_format'] == 'upper':
                    std_value = std_value.upper()
                elif rules['value_format'] == 'title':
                    std_value = std_value.title()

            return std_value

        except Exception as e:
            logger.error(f"Error standardizing value {value}: {str(e)}")
            return value

    def create_tag_policy(self, policy_config: Dict) -> bool:
        """Create or update a tag policy."""
        try:
            # Policy configuration example:
            # {
            #     'required_tags': ['environment', 'owner'],
            #     'allowed_values': {
            #         'environment': ['prod', 'dev', 'test'],
            #         'owner': ['team-a', 'team-b']
            #     },
            #     'inheritance': {
            #         'from_resource_group': ['environment', 'cost-center']
            #     }
            # }

            # Convert policy config to Azure Policy format
            policy_definition = self._create_policy_definition(policy_config)

            # Apply policy at subscription level
            scope = f'/subscriptions/{self.subscription_id}'
            self.resource_client.policy_assignments.create(
                scope=scope,
                policy_assignment_name='tag-governance-policy',
                parameters=policy_definition
            )

            return True

        except Exception as e:
            logger.error(f"Error creating tag policy: {str(e)}")
            return False

    def _create_policy_definition(self, config: Dict) -> Dict:
        """Create Azure Policy definition from config."""
        try:
            policy_rules = {
                'if': {
                    'allOf': []
                },
                'then': {
                    'effect': 'deny'
                }
            }

            # Add required tags rule
            if 'required_tags' in config:
                for tag in config['required_tags']:
                    policy_rules['if']['allOf'].append({
                        'field': f'tags[{tag}]',
                        'exists': 'false'
                    })

            # Add allowed values rule
            if 'allowed_values' in config:
                for tag, values in config['allowed_values'].items():
                    policy_rules['if']['allOf'].append({
                        'field': f'tags[{tag}]',
                        'notIn': values
                    })

            return {
                'properties': {
                    'displayName': 'Tag Governance Policy',
                    'description': 'Enforce tag standards across resources',
                    'policyRule': policy_rules,
                    'parameters': {}
                }
            }

        except Exception as e:
            logger.error(f"Error creating policy definition: {str(e)}")
            return {}

    def get_tag_inheritance(self, resource_id: str) -> Dict:
        """Get inherited tags for a resource."""
        try:
            # Get resource details
            resource = self.resource_client.resources.get_by_id(resource_id, '2021-04-01')
            
            # Get resource group
            rg_name = resource.id.split('/')[4]
            resource_group = self.resource_client.resource_groups.get(rg_name)
            
            inherited_tags = {
                'resource_group': resource_group.tags or {},
                'subscription': self._get_subscription_tags()
            }

            return inherited_tags

        except Exception as e:
            logger.error(f"Error getting tag inheritance for {resource_id}: {str(e)}")
            return {}

    def _get_subscription_tags(self) -> Dict:
        """Get subscription level tags."""
        try:
            subscription_scope = f'/subscriptions/{self.subscription_id}'
            tags = self.resource_client.tags.list()
            
            return {tag.tag_name: tag.values for tag in tags.value}

        except Exception as e:
            logger.error(f"Error getting subscription tags: {str(e)}")
            return {}
