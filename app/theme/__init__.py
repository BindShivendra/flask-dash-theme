from flask import Blueprint


theme_bp = Blueprint('theme', __name__, url_prefix='/theme')

# views should be last to avoid circular imports
from . import views