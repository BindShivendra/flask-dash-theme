import unittest

from app.auth.models import User


class UserModelTestCase(unittest.TestCase):

    def test_password_setter(self):
        u = User(password='thispass')
        self.assertTrue(u.password_has is not None)

    def test_no_password_getter(self):
        u = User(password='thispass')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='thispass')
        self.assertTrue(u.verify_password('thispass'))
        self.assertFalse(u.verify_password('thatpass'))

    def test_password_are_random(self):
        u = User(password='thispass')
        _u = User(password='thatpass')
        self.assertTrue(u.password_has != _u.password_has)
