# imports
import unittest, os, datetime
from flask import json, request, Response, session
import MySQLdb
from app import app

class LoginTestCase(unittest.TestCase):
    """Login Feature specific Test Cases will go here"""

    def setUp(self):
        """Setup test app"""
        app.config['TESTING'] = True

    def tearDown(self):
        """Destroy test app"""
        

    def login(self, c, username, password):
        """Login helper function"""
        return c.post('/login', data=dict(
            username=username,
            password=password,
            ), follow_redirects=True)

    def logout(self, c):
        """Logout helper function"""
        return c.get('/logout', follow_redirects=True)

    def test_login_logout_good(self):
        """Test Login and Logout using helper functions"""      
        with app.test_client() as c:
            rv = self.login(c,
                app.config['USERNAME'],
                app.config['PASSWORD'])
            # Check log in successful
            self.assertEqual(request.path, '/query')
            # Check logged in session variable is set to True
            self.assertTrue(session.get('logged_in'))

            rv = self.logout(c)
            # Check log out successful
            self.assertEqual(request.path, '/logout')
            # Check logged in session variable is set to None
            self.assertEqual(session.get('logged_in'), None)

    def test_login_invalid_username(self):
        """Test login with Invalid Username"""
        with app.test_client() as c:
            # Check for Invalid Username
            rv = self.login(c,
                app.config['USERNAME'] + 'x',
                app.config['PASSWORD'])

            # Check log in fails
            self.assertEqual(request.path, '/login')
            # Check logged in session variable is set to None
            self.assertEqual(session.get('logged_in'), None)
            # Check if error message is displayed for invalid username
            self.assertIn(b"Invalid Username. Please try again.", rv.data)

    def test_login_invalid_password(self):
        """Test login with Invalid Password"""
        with app.test_client() as c:
            # Check for Invalid Password
            rv = self.login(c,
                app.config['USERNAME'],
                app.config['PASSWORD'] + 'x')
            # Check log in fails
            self.assertEqual(request.path, '/login')
            # Check logged in session variable is set to None
            self.assertEqual(session.get('logged_in'), None)
            # Check if error message is displayed for invalid password
            self.assertIn(b"Invalid Password. Please try again.", rv.data)

if __name__ == '__main__':
    unittest.main()