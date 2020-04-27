from flask import render_template

from . import bp as main_bp


@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 404


@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main_bp.app_errorhandler(500)
def internat_server_error(e):
    return render_template('500.html'), 500
