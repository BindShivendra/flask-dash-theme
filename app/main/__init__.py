from flask import Blueprint


bp = Blueprint('main', __name__)

# views, errors should be last to avoid circular imports
from . import views, errors