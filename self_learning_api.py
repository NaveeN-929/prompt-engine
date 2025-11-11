"""
Self-Learning API Endpoints
Exposes self-learning metrics, analytics, and controls via REST API
"""

from flask import Blueprint, jsonify, request
import asyncio
from app.learning.integration_helper import get_self_learning

# Create blueprint
self_learning_bp = Blueprint('self_learning', __name__, url_prefix='/self-learning')


@self_learning_bp.route('/status', methods=['GET'])
def get_self_learning_status():
    """Get self-learning system status"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({
            'status': 'disabled',
            'message': 'Self-learning system not initialized'
        }), 503
    
    return jsonify({
        'status': 'active',
        'is_ready': True,
        'components': {
            'learning_manager': 'active',
            'knowledge_graph': 'active',
            'cross_component_bridge': 'active',
            'learning_analytics': 'active'
        },
        'message': 'Self-learning system operational'
    })


@self_learning_bp.route('/metrics', methods=['GET'])
def get_learning_metrics():
    """Get current learning metrics"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    metrics = sl.get_learning_metrics()
    
    return jsonify({
        'status': 'success',
        'metrics': metrics
    })


@self_learning_bp.route('/insights', methods=['GET'])
def get_learning_insights():
    """Get learning insights"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    insights = sl.get_learning_insights()
    
    return jsonify({
        'status': 'success',
        'insights': insights
    })


@self_learning_bp.route('/report', methods=['GET'])
def generate_learning_report():
    """Generate comprehensive learning report"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    report = sl.generate_learning_report()
    
    return jsonify({
        'status': 'success',
        'report': report
    })


@self_learning_bp.route('/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get analytics dashboard data"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    dashboard_data = sl.get_analytics_dashboard_data()
    
    return jsonify({
        'status': 'success',
        'dashboard': dashboard_data
    })


@self_learning_bp.route('/predict-quality', methods=['POST'])
def predict_quality():
    """Predict interaction quality for given input"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    data = request.get_json()
    input_data = data.get('input_data', {})
    context = data.get('context')
    
    # Run async prediction
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        prediction = loop.run_until_complete(
            sl.predict_interaction_quality(input_data, context)
        )
    finally:
        loop.close()
    
    return jsonify({
        'status': 'success',
        'prediction': prediction
    })


@self_learning_bp.route('/similar-patterns', methods=['POST'])
def find_similar_patterns():
    """Find similar successful patterns"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    data = request.get_json()
    input_data = data.get('input_data', {})
    pattern_type = data.get('pattern_type')
    limit = data.get('limit', 5)
    
    # Run async search
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        patterns = loop.run_until_complete(
            sl.get_similar_successful_patterns(input_data, pattern_type, limit)
        )
    finally:
        loop.close()
    
    return jsonify({
        'status': 'success',
        'patterns_found': len(patterns),
        'patterns': patterns
    })


@self_learning_bp.route('/knowledge-graph/stats', methods=['GET'])
def get_knowledge_graph_stats():
    """Get knowledge graph statistics"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    if sl.knowledge_graph is None:
        return jsonify({'error': 'Knowledge graph not available'}), 503
    
    stats = sl.knowledge_graph.get_knowledge_stats()
    
    return jsonify({
        'status': 'success',
        'knowledge_graph_stats': stats
    })


@self_learning_bp.route('/cross-component/stats', methods=['GET'])
def get_cross_component_stats():
    """Get cross-component learning statistics"""
    
    sl = get_self_learning()
    
    if not sl.is_ready():
        return jsonify({'error': 'Self-learning not initialized'}), 503
    
    if sl.cross_component_bridge is None:
        return jsonify({'error': 'Cross-component bridge not available'}), 503
    
    stats = sl.cross_component_bridge.get_bridge_statistics()
    
    return jsonify({
        'status': 'success',
        'cross_component_stats': stats
    })


@self_learning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for self-learning system"""
    
    sl = get_self_learning()
    
    health = {
        'status': 'healthy' if sl.is_ready() else 'unhealthy',
        'self_learning_ready': sl.is_ready(),
        'components': {
            'learning_manager': sl.learning_manager is not None,
            'knowledge_graph': sl.knowledge_graph is not None,
            'cross_component_bridge': sl.cross_component_bridge is not None,
            'learning_analytics': sl.learning_analytics is not None
        }
    }
    
    status_code = 200 if health['status'] == 'healthy' else 503
    
    return jsonify(health), status_code


def register_self_learning_api(app):
    """Register self-learning API blueprint with Flask app"""
    app.register_blueprint(self_learning_bp)
    print("✅ Self-Learning API endpoints registered")

