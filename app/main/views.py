from flask import render_template
from . import bp as main_bp


@main_bp.route('/')
def main():
    return render_template('base.html')
