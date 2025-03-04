from .analyzer import TaggingAnalyzer
from .manager import TagManager
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TaggingOptimizer:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.analyzer = TaggingAnalyzer(subscription_id)
        self.manager = TagManager(subscription_id)

    def optimize_tags(self) -> Dict:
        """Perform comprehensive tag optimization."""
        try:
            # Analyze current tagging state
            analysis = self.analyzer.analyze_resource_tags()
            if not analysis:
                return {'error': 'Failed to analyze resource tags'}

            # Generate recommendations
            recommendations = self._generate_recommendations(analysis)

            # Generate optimization plan
            optimization_plan = self._create_optimization_plan(analysis, recommendations)

            return {
                'analysis': analysis,
                'recommendations': recommendations,
                'optimization_plan': optimization_plan
            }

        except Exception as e:
            logger.error(f"Error optimizing tags: {str(e)}")
            return {'error': str(e)}

    def _generate_recommendations(self, analysis: Dict) -> Dict:
        """Generate tagging recommendations based on analysis."""
        try:
            recommendations = {
                'immediate_actions': [],
                'short_term': [],
                'long_term': [],
                'policy_recommendations': [],
                'standardization_recommendations': []
            }

            # Immediate actions for non-compliant resources
            if 'compliance' in analysis:
                for resource in analysis['compliance'].get('non_compliant_resources', []):
                    recommendations['immediate_actions'].append({
                        'type': 'add_required_tags',
                        'resource': resource['name'],
                        'missing_tags': resource['missing_tags'],
                        'priority': 'high'
                    })

            # Tag consistency recommendations
            if 'tag_consistency' in analysis:
                for tag, variations in analysis['tag_consistency'].get('case_inconsistencies', {}).items():
                    if len(variations) > 1:
                        recommendations['short_term'].append({
                            'type': 'standardize_tag_case',
                            'tag': tag,
                            'variations': variations,
                            'recommended_format': self._recommend_tag_format(variations),
                            'priority': 'medium'
                        })

            # Category-based recommendations
            if 'tag_categories' in analysis:
                for category, data in analysis['tag_categories'].items():
                    if data['coverage'] < 80:  # Less than 80% coverage
                        recommendations['short_term'].append({
                            'type': 'improve_category_coverage',
                            'category': category,
                            'current_coverage': data['coverage'],
                            'missing_tags': data['missing_tags'],
                            'priority': 'medium'
                        })

            # Policy recommendations
            policy_recs = self._generate_policy_recommendations(analysis)
            recommendations['policy_recommendations'].extend(policy_recs)

            # Standardization recommendations
            std_recs = self._generate_standardization_recommendations(analysis)
            recommendations['standardization_recommendations'].extend(std_recs)

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {}

    def _create_optimization_plan(self, analysis: Dict, recommendations: Dict) -> Dict:
        """Create a detailed optimization plan."""
        try:
            plan = {
                'phases': [
                    {
                        'name': 'Phase 1: Compliance',
                        'description': 'Address non-compliant resources and missing required tags',
                        'actions': [],
                        'estimated_effort': 'medium',
                        'priority': 'high'
                    },
                    {
                        'name': 'Phase 2: Standardization',
                        'description': 'Implement tag standardization and resolve inconsistencies',
                        'actions': [],
                        'estimated_effort': 'high',
                        'priority': 'medium'
                    },
                    {
                        'name': 'Phase 3: Governance',
                        'description': 'Implement tag policies and governance controls',
                        'actions': [],
                        'estimated_effort': 'high',
                        'priority': 'medium'
                    }
                ],
                'estimated_timeline': '4-6 weeks',
                'risk_assessment': self._assess_optimization_risks(analysis)
            }

            # Add compliance actions
            for rec in recommendations.get('immediate_actions', []):
                plan['phases'][0]['actions'].append({
                    'type': 'compliance',
                    'description': f"Add missing tags {rec['missing_tags']} to {rec['resource']}",
                    'implementation': {
                        'method': 'apply_tags',
                        'parameters': {
                            'resource': rec['resource'],
                            'tags': {tag: '' for tag in rec['missing_tags']}
                        }
                    }
                })

            # Add standardization actions
            for rec in recommendations.get('standardization_recommendations', []):
                plan['phases'][1]['actions'].append({
                    'type': 'standardization',
                    'description': f"Standardize {rec['tag']} format to {rec['recommended_format']}",
                    'implementation': {
                        'method': 'standardize_tags',
                        'parameters': {
                            'tag': rec['tag'],
                            'format': rec['recommended_format']
                        }
                    }
                })

            # Add governance actions
            for rec in recommendations.get('policy_recommendations', []):
                plan['phases'][2]['actions'].append({
                    'type': 'governance',
                    'description': f"Implement {rec['type']} policy",
                    'implementation': {
                        'method': 'create_tag_policy',
                        'parameters': rec['policy_config']
                    }
                })

            return plan

        except Exception as e:
            logger.error(f"Error creating optimization plan: {str(e)}")
            return {}

    def _generate_policy_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate policy recommendations based on analysis."""
        try:
            policy_recommendations = []

            # Required tags policy
            if 'compliance' in analysis:
                policy_recommendations.append({
                    'type': 'required_tags',
                    'description': 'Enforce required tags across all resources',
                    'policy_config': {
                        'required_tags': self.analyzer.required_tags,
                        'effect': 'deny'
                    }
                })

            # Value standardization policy
            if 'tag_consistency' in analysis:
                std_values = self._extract_standard_values(analysis)
                if std_values:
                    policy_recommendations.append({
                        'type': 'allowed_values',
                        'description': 'Enforce standardized tag values',
                        'policy_config': {
                            'allowed_values': std_values,
                            'effect': 'deny'
                        }
                    })

            # Inheritance policy
            policy_recommendations.append({
                'type': 'inheritance',
                'description': 'Enable tag inheritance from resource groups',
                'policy_config': {
                    'inherit_from_rg': ['environment', 'cost-center', 'project'],
                    'effect': 'modify'
                }
            })

            return policy_recommendations

        except Exception as e:
            logger.error(f"Error generating policy recommendations: {str(e)}")
            return []

    def _generate_standardization_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate standardization recommendations based on analysis."""
        try:
            recommendations = []

            # Case standardization
            if 'tag_consistency' in analysis:
                for tag, variations in analysis['tag_consistency'].get('case_inconsistencies', {}).items():
                    recommendations.append({
                        'type': 'case_standardization',
                        'tag': tag,
                        'current_variations': variations,
                        'recommended_format': self._recommend_tag_format(variations)
                    })

            # Value format standardization
            if 'value_standardization' in analysis:
                for tag, formats in analysis['value_standardization'].get('value_formats', {}).items():
                    if len(formats) > 1:  # Multiple formats detected
                        recommendations.append({
                            'type': 'value_format_standardization',
                            'tag': tag,
                            'current_formats': formats,
                            'recommended_format': self._recommend_value_format(formats)
                        })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating standardization recommendations: {str(e)}")
            return []

    def _recommend_tag_format(self, variations: List[str]) -> str:
        """Recommend a standard format for a tag."""
        # Prefer kebab-case for tag names
        return 'kebab-case'

    def _recommend_value_format(self, formats: Dict) -> str:
        """Recommend a standard format for tag values."""
        # Simple logic - could be enhanced based on specific requirements
        if 'date' in formats:
            return 'ISO8601'
        elif 'email' in formats:
            return 'lowercase'
        else:
            return 'lowercase'

    def _extract_standard_values(self, analysis: Dict) -> Dict:
        """Extract standardized values from analysis."""
        try:
            standard_values = {}
            
            if 'tag_consistency' in analysis:
                value_freq = analysis['tag_consistency'].get('value_frequency', {})
                for tag, values in value_freq.items():
                    # Get most frequent values (top 5)
                    common_values = sorted(
                        values.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                    standard_values[tag] = [v[0] for v in common_values]

            return standard_values

        except Exception as e:
            logger.error(f"Error extracting standard values: {str(e)}")
            return {}

    def _assess_optimization_risks(self, analysis: Dict) -> Dict:
        """Assess risks associated with tag optimization."""
        try:
            risks = {
                'high': [],
                'medium': [],
                'low': []
            }

            # Assess compliance risks
            if 'compliance' in analysis:
                non_compliant = len(analysis['compliance'].get('non_compliant_resources', []))
                if non_compliant > 100:
                    risks['high'].append({
                        'type': 'compliance',
                        'description': f'Large number of non-compliant resources ({non_compliant})',
                        'mitigation': 'Phase implementation and prioritize critical resources'
                    })

            # Assess standardization risks
            if 'tag_consistency' in analysis:
                inconsistent_tags = len(analysis['tag_consistency'].get('case_inconsistencies', {}))
                if inconsistent_tags > 10:
                    risks['medium'].append({
                        'type': 'standardization',
                        'description': f'Significant tag inconsistencies ({inconsistent_tags} tags)',
                        'mitigation': 'Implement automated standardization with validation'
                    })

            # Assess policy risks
            if 'tag_categories' in analysis:
                low_coverage_categories = sum(
                    1 for cat in analysis['tag_categories'].values()
                    if cat['coverage'] < 50
                )
                if low_coverage_categories > 2:
                    risks['medium'].append({
                        'type': 'coverage',
                        'description': f'Low tag coverage in {low_coverage_categories} categories',
                        'mitigation': 'Gradual policy implementation with grace period'
                    })

            return risks

        except Exception as e:
            logger.error(f"Error assessing optimization risks: {str(e)}")
            return {}
