import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = current_app('testing')
        self.app.context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self):
        """Check if app is created"""
        self.assertIsNotNone(current_app)

    def test_app_is_in_testing(self):
        """Check if app is in testing mode"""
        self.assertTrue(current_app.config['TESTING'])
