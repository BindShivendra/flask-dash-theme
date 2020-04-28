from flask import Blueprint


bp = Blueprint('main', __name__, url_prefix='/main')

# views, errors should be last to avoid circular imports
from . import views, errors
