import os
from flask_migrate import Migrate

from app import create_app, db
from app.auth.models import User, Role

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, user=User, role=Role)


@app.cli.command()
def test():
    ''' Run tests '''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# if __name__ == "__main__":
#     app.run(debug=True)
