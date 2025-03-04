from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from typing import Dict, List
import logging
from ..optimizers.cost.optimizer import CostOptimizer
from ..optimizers.scaling.optimizer import ScalingOptimizer
from ..optimizers.monitoring.optimizer import MonitoringOptimizer
from ..optimizers.tagging.optimizer import TaggingOptimizer
from ..optimizers.utilization.optimizer import UtilizationOptimizer

logger = logging.getLogger(__name__)
api = Blueprint('api', __name__)

class DashboardAPI:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.cost_optimizer = CostOptimizer(subscription_id)
        self.scaling_optimizer = ScalingOptimizer(subscription_id)
        self.monitoring_optimizer = MonitoringOptimizer(subscription_id)
        self.tagging_optimizer = TaggingOptimizer(subscription_id)
        self.utilization_optimizer = UtilizationOptimizer(subscription_id)

    @api.route('/api/cost/analysis', methods=['GET'])
    def get_cost_analysis(self):
        """Get comprehensive cost analysis."""
        try:
            time_range = int(request.args.get('time_range', 30))
            result = self.cost_optimizer.optimize_costs(time_range)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting cost analysis: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @api.route('/api/cost/trends', methods=['GET'])
    def get_cost_trends(self):
        """Get cost trends and forecasts."""
        try:
            time_range = int(request.args.get('time_range', 30))
            analysis = self.cost_optimizer.analyzer.analyze_costs(time_range)
            return jsonify(analysis.get('cost_trends', {}))
        except Exception as e:
            logger.error(f"Error getting cost trends: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @api.route('/api/cost/recommendations', methods=['GET'])
    def get_cost_recommendations(self):
        """Get cost optimization recommendations."""
        try:
            time_range = int(request.args.get('time_range', 30))
            analysis = self.cost_optimizer.optimize_costs(time_range)
            return jsonify(analysis.get('recommendations', {}))
        except Exception as e:
            logger.error(f"Error getting cost recommendations: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @api.route('/api/scaling/analysis', methods=['GET'])
    def get_scaling_analysis(self):
        """Get scaling analysis and recommendations."""
        try:
            time_range = int(request.args.get('time_range', 7))
            result = self.scaling_optimizer.optimize_scaling(time_range)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting scaling analysis: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @api.route('/api/monitoring/analysis', methods=['GET'])
    def get_monitoring_analysis(self):
        """Get monitoring analysis and recommendations."""
        try:
            time_range = int(request.args.get('time_range', 7))
            result = self.monitoring_optimizer.optimize_monitoring(time_range)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting monitoring analysis: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @api.route('/api/tagging/analysis', methods=['GET'])
    def get_tagging_analysis(self):
        """Get tagging analysis and recommendations."""
        try:
            result = self.tagging_optimizer.optimize_tagging()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting tagging analysis: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @api.route('/api/utilization/analysis', methods=['GET'])
    def get_utilization_analysis(self):
        """Get utilization analysis and recommendations."""
        try:
            time_range = int(request.args.get('time_range', 7))
            result = self.utilization_optimizer.optimize_utilization(time_range)
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting utilization analysis: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @api.route('/api/summary', methods=['GET'])
    def get_summary(self):
        """Get summary of all optimization analyses."""
        try:
            time_range = int(request.args.get('time_range', 30))
            
            # Get all analyses
            cost_analysis = self.cost_optimizer.optimize_costs(time_range)
            scaling_analysis = self.scaling_optimizer.optimize_scaling(time_range)
            monitoring_analysis = self.monitoring_optimizer.optimize_monitoring(time_range)
            tagging_analysis = self.tagging_optimizer.optimize_tagging()
            utilization_analysis = self.utilization_optimizer.optimize_utilization(time_range)
            
            # Combine results
            summary = {
                'cost': self._summarize_cost_analysis(cost_analysis),
                'scaling': self._summarize_scaling_analysis(scaling_analysis),
                'monitoring': self._summarize_monitoring_analysis(monitoring_analysis),
                'tagging': self._summarize_tagging_analysis(tagging_analysis),
                'utilization': self._summarize_utilization_analysis(utilization_analysis)
            }
            
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Error getting summary: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def _summarize_cost_analysis(self, analysis: Dict) -> Dict:
        """Summarize cost analysis results."""
        try:
            return {
                'total_cost': analysis.get('analysis', {}).get('cost_summary', {}).get('total_cost', 0),
                'potential_savings': sum(
                    rec.get('estimated_savings', 0)
                    for rec in analysis.get('recommendations', {}).get('immediate_actions', [])
                ),
                'recommendation_count': len(analysis.get('recommendations', {}).get('immediate_actions', [])),
                'optimization_score': self._calculate_optimization_score(analysis)
            }
        except Exception as e:
            logger.error(f"Error summarizing cost analysis: {str(e)}")
            return {}

    def _summarize_scaling_analysis(self, analysis: Dict) -> Dict:
        """Summarize scaling analysis results."""
        try:
            return {
                'resources_analyzed': len(analysis.get('analysis', {}).get('resources', [])),
                'optimization_opportunities': len(analysis.get('recommendations', {}).get('immediate_actions', [])),
                'potential_savings': sum(
                    rec.get('estimated_savings', 0)
                    for rec in analysis.get('recommendations', {}).get('immediate_actions', [])
                )
            }
        except Exception as e:
            logger.error(f"Error summarizing scaling analysis: {str(e)}")
            return {}

    def _summarize_monitoring_analysis(self, analysis: Dict) -> Dict:
        """Summarize monitoring analysis results."""
        try:
            return {
                'resources_monitored': len(analysis.get('analysis', {}).get('resources', [])),
                'alerts_configured': len(analysis.get('analysis', {}).get('alerts', [])),
                'improvement_opportunities': len(analysis.get('recommendations', {}).get('immediate_actions', []))
            }
        except Exception as e:
            logger.error(f"Error summarizing monitoring analysis: {str(e)}")
            return {}

    def _summarize_tagging_analysis(self, analysis: Dict) -> Dict:
        """Summarize tagging analysis results."""
        try:
            return {
                'resources_analyzed': len(analysis.get('analysis', {}).get('resources', [])),
                'tag_coverage': analysis.get('analysis', {}).get('tag_coverage', 0),
                'improvement_opportunities': len(analysis.get('recommendations', {}).get('immediate_actions', []))
            }
        except Exception as e:
            logger.error(f"Error summarizing tagging analysis: {str(e)}")
            return {}

    def _summarize_utilization_analysis(self, analysis: Dict) -> Dict:
        """Summarize utilization analysis results."""
        try:
            return {
                'resources_analyzed': len(analysis.get('analysis', {}).get('resources', [])),
                'underutilized_resources': len(analysis.get('analysis', {}).get('underutilized', [])),
                'potential_savings': sum(
                    rec.get('estimated_savings', 0)
                    for rec in analysis.get('recommendations', {}).get('immediate_actions', [])
                )
            }
        except Exception as e:
            logger.error(f"Error summarizing utilization analysis: {str(e)}")
            return {}

    def _calculate_optimization_score(self, analysis: Dict) -> float:
        """Calculate overall optimization score."""
        try:
            scores = []
            
            # Cost efficiency score
            if 'cost_summary' in analysis.get('analysis', {}):
                cost_data = analysis['analysis']['cost_summary']
                if cost_data.get('total_cost', 0) > 0:
                    efficiency = 1 - (
                        sum(
                            rec.get('estimated_savings', 0)
                            for rec in analysis.get('recommendations', {}).get('immediate_actions', [])
                        ) / cost_data['total_cost']
                    )
                    scores.append(efficiency * 100)
            
            # Resource utilization score
            if 'resource_costs' in analysis.get('analysis', {}):
                resource_data = analysis['analysis']['resource_costs']
                utilization_scores = []
                for resource_type in resource_data.values():
                    if 'utilization' in resource_type:
                        utilization_scores.append(resource_type['utilization'])
                if utilization_scores:
                    scores.append(sum(utilization_scores) / len(utilization_scores))
            
            return sum(scores) / len(scores) if scores else 0
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {str(e)}")
            return 0
