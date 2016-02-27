# imports
import unittest, os, datetime
from flask import json, request, Response, session
import MySQLdb
from app import app

class QueryFormTestCase(unittest.TestCase):
    """Query Form Feature specific Test Cases will go here"""

    def setUp(self):
        """Setup test app"""
        app.config['TESTING'] = True

    def tearDown(self):
        """Destroy test app"""        

    def test_form_logger_type_automatic_fill(self):
          """Test the logger_type field is filled automatically on page load"""
          with app.test_client() as client:
            rv = client.get('/query')
            print(request.form)
            print(rv.data)
    # def test_query_submit_good_values(self):
    #     """Test the QueryForm with proper values"""
    #     # Check Fields without redirection
    #     with app.test_client() as c:            
    #         rv = c.post('/query', 
    #             data=dict(
    #                 logger_type='Mussel',
    #                 country_name='USA',
    #                 state_name='Massachusetts', 
    #                 date_pick_from=datetime.date(1989, 1, 1).strftime('%m/%d/%Y'),
    #                 date_pick_to=datetime.date(2001, 4, 1).strftime('%m/%d/%Y')),
    #             follow_redirects=False)
    #         self.assertEqual(request.form.get('logger_type'), "Mussel")
    #         self.assertEqual(request.form.get('country_name'), "USA")
    #         self.assertEqual(request.form.get('state_name'), "Massachusetts")
    #         self.assertEqual(request.form.get('date_pick_from'), "01/01/1989")
    #         self.assertEqual(request.form.get('date_pick_to'), "04/01/2001")

    # def test_query_submit_redirect_success(self):
    #     """Test redirection of QueryForm with proper values"""
    #     # Check successful redirection
    #     with app.test_client() as c:            
    #         rv = c.post('/query', 
    #             data=dict(
    #                 logger_type='Mussel',
    #                 country_name='USA',
    #                 state_name='Massachusetts', 
    #                 date_pick_from=datetime.date(1989, 1, 1).strftime('%m/%d/%Y'),
    #                 date_pick_to=datetime.date(2001, 4, 1).strftime('%m/%d/%Y')),
    #             follow_redirects=True)
    #         # Check successful redirection
    #         self.assertEqual(request.path, '/query')

    # def test_query_submit_missing_compulsory_values(self):
    #     """Test the QueryForm with compulsory fields missing"""
    #     with app.test_client() as c:
    #         rv = c.post('/query', 
    #             data=dict( 
    #                 country_name='USA',
    #                 state_name='Massachusetts'), 
    #             follow_redirects=True)
    #         # Check Query Submission fails
    #         self.assertEqual(request.path, '/query')
    #         # Check if error message is displayed for invalid query
    #         self.assertIn(b'Invalid Submission. All fields marked with * are compulsory', rv.data)

if __name__ == '__main__':
    unittest.main()