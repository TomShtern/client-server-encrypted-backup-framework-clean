from __future__ import annotations

try:
    from flask import Blueprint, jsonify
except Exception:  # server.py may not run Flask, so guard imports
    Blueprint = None
    jsonify = None

from .connection_health import get_connection_health_monitor


health_bp = Blueprint('conn_health', __name__) if Blueprint else None


if health_bp:
    @health_bp.route('/health/connections')
    def connections_summary():
        try:
            monitor = get_connection_health_monitor()
            return jsonify({
                'success': True,
                'connections': monitor.get_summary(),
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

