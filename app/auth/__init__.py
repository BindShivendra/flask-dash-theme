from flask import Blueprint


auth = Blueprint('auth', __name__, url_prefix='/auth')

# views, errors should be last to avoid circular imports
from . import views