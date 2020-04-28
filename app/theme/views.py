from flask import render_template
from . import theme_bp


@theme_bp.route('/')
def main():
    return render_template('theme/index.html')


@theme_bp.route('/buttons')
def buttons():
    return render_template('theme/buttons.html')


@theme_bp.route('/cards')
def cards():
    return render_template('theme/cards.html')


@theme_bp.route('/colours')
def colours():
    return render_template('theme/utilities-color.html')


@theme_bp.route('/borders')
def borders():
    return render_template('theme/utilities-border.html')


@theme_bp.route('/animations')
def animations():
    return render_template('theme/utilities-animation.html')


@theme_bp.route('/others')
def others():
    return render_template('theme/utilities-other.html')


@theme_bp.route('/login')
def login():
    return render_template('theme/login.html')


@theme_bp.route('/register')
def register():
    return render_template('theme/register.html')


@theme_bp.route('/reset_password')
def reset_password():
    return render_template('theme/forgot-password.html')


@theme_bp.route('/blank')
def blank():
    return render_template('theme/blank.html')


@theme_bp.route('/charts')
def charts():
    return render_template('theme/charts.html')


@theme_bp.route('/tables')
def tables():
    return render_template('theme/tables.html')


@theme_bp.route('/404')
def page_not_found():
    return render_template('theme/404.html')
