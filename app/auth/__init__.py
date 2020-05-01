from flask import Blueprint


auth = Blueprint('auth', __name__, url_prefix='/auth')


# views, errors should be last to avoid circular imports
from . import views
from .models import Permission

@auth.app_context_processor
def inject_permission():
    return dict(permission=Permission)
