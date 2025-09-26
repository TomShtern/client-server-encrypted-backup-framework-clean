from __future__ import annotations

try:
    from flask import Blueprint, Response, jsonify
    from flask.wrappers import Response as FlaskResponse
    HAS_FLASK = True
except Exception:  # server.py may not run Flask, so guard imports
    Blueprint = None
    jsonify = None
    Response = None
    FlaskResponse = None
    HAS_FLASK = False

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from .connection_health import get_connection_health_monitor

if HAS_FLASK and Blueprint is not None and jsonify is not None:
    health_bp = Blueprint('conn_health', __name__)

    @health_bp.route('/health/connections')
    def connections_summary() -> Any:
        """Get connection health summary"""
        from flask import jsonify as flask_jsonify  # Re-import to avoid None issues
        try:
            monitor = get_connection_health_monitor()
            if monitor is not None:
                return flask_jsonify({
                    'success': True,
                    'connections': monitor.get_summary(),  # type: ignore
                })
            else:
                return flask_jsonify({'success': False, 'error': 'Monitor not available'}), 503
        except Exception as e:
            return flask_jsonify({'success': False, 'error': str(e)}), 500
else:
    health_bp = None

