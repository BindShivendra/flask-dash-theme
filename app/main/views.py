from . import bp as main_bp


@main_bp.route('/')
def main():
    return 'main bp main route'
