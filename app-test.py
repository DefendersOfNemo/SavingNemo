# imports
import unittest
import os
from flask import json
from app import app

class BasicTestCase(unittest.TestCase):
	# DB Connection Test Cases will go here
	# ...

	def test_index(self):
		"""inital test. ensure flask was setup correctly"""
		tester = app.test_client(self)
		response = tester.get('/', content_type='html/text')
		self.assertEqual(response.status_code, 200)


class SavingNemoTestCase(unittest.TestCase):
	# Feature Specific Test Cases will go here
	# ...
	def setUp(self):
		"""Setup test app"""
		app.config['TESTING'] = True
		self.app = app.test_client()

	def tearDown(self):
		"""Destroy test app"""
		# ...

	def login(self, username, password):
		"""Login helper function"""
		return self.app.post('/login', data=dict(
			username=username,
			password=password,
			), follow_redirects=True)

	def logout(self):
		"""Logout helper function"""
		return self.app.get('/logout', follow_redirects=True)

	def test_login_logout(self):
		"""Test login and logout using helper functions"""
		rv = self.login(
			app.config['USERNAME'],
			app.config['PASSWORD']
			)
		self.assertIn(b'You are logged in', rv.data)
		rv = self.logout()
		self.assertIn(b'You are logged out', rv.data)
		rv = self.login(
			app.config['USERNAME'] + 'x',
			app.config['PASSWORD']
			)
		self.assertIn(b'Invalid username', rv.data)
		rv = self.login(
			app.config['USERNAME'],
			app.config['PASSWORD'] + 'x'
			)
		self.assertIn(b'Invalid password', rv.data)

	def test_query(self):
		"""Test the QueryForm in the HomePage"""
		rv = self.app.post('/query', data=dict(
			logger_type='Mussel',
			country_name='USA',
			state_name='Massachusetts'), follow_redirects=True)
		self.assertIn(b'Mussel', rv.data)
		self.assertIn(b'USA', rv.data)
		self.assertIn(b'Massachusetts', rv.data)

if __name__ == '__main__':
	unittest.main()