from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)


@errors_bp.errorhandler(404)
def err_404(error):
    return render_template('error.jinja', error=error, code=404, message="Not Found"), 404
