# imports
import unittest, os, datetime
from flask import Flask, json, request, Response, session
import MySQLdb
from app import app
from app.dbconnect import DbConnect

class QueryFormTestCase(unittest.TestCase):
    """Query Form Feature specific Test Cases will go here"""
    
    def setUp(self):
        """Setup test app"""
        app.config['TESTING'] = True     
        self.db = DbConnect(app.config)

    def tearDown(self):
        """Close test database"""        
        self.db.close()

    def stringToBytes(self, stringValue):
        """Convert Strings to their Bytes representation"""
        return bytes(stringValue, 'UTF-8')

    def test_form_logger_type_automatic_fill(self):
        """Test the logger_type field is filled automatically on page load"""
        with app.test_client() as client:
            response = client.get('/query')
            logger_type_choices = self.db.getLoggerTypes() 
            for logger_type in logger_type_choices:
                self.assertIn(self.stringToBytes(logger_type[0]), response.data)        
    
    def check_ajax(self, selected_type, selected_value, dbFunction):
        """Helper Function to test the ajax call functionality when
           given selected type field is selected with given value"""
        with app.test_client() as client:
            response = client.get('/_parse_data', 
                                query_string=dict(
                                    select_type=selected_type,
                                    select_value=selected_value))
            self.assertEqual(selected_type, request.args.get('select_type'))
            self.assertEqual(selected_value, request.args.get('select_value'))
            choices = dbFunction(request.args.get('select_value'))
            for choice in choices:
                self.assertIn(self.stringToBytes(choice[0]), response.data)

    def test_form_logger_type_select(self):
        """Test the ajax call functionality if logger_type field is selected"""
        self.check_ajax("logger_type", "robomussel", self.db.getCountry)

    def test_form_country_name_select(self):
        """Test the ajax call functionality if country_name field is selected"""
        self.check_ajax("country_name", "USA", self.db.getState)

    def test_form_state_name_select(self):
        """Test the ajax call functionality if state_name field is selected"""
        self.check_ajax("state_name", "California", self.db.getLocation)

    def test_form_location_name_select(self):
        """Test the ajax call functionality if location_name field is selected"""
        self.check_ajax("lt_for_zone", "robomussel", self.db.getZone)

    def test_form_Zone_name_select(self):
        """Test the ajax call functionality if zone_name field is selected"""
        self.check_ajax("lt_for_subzone", "robomussel", self.db.getSubZone)    

    def test_form_SubZone_name_select(self):
        """Test the ajax call functionality if subZone_name field is selected"""
        self.check_ajax("lt_for_wave_exp", "robomussel", self.db.getWaveExp)    

    def test_query_results(self):
        """Test the query results functionality"""
        with app.test_client() as client:
            response = client.post('/query', 
                data=dict(
                    logger_type="robomussel",
                    country_name="Canada",
                    state_name="British Columbia",
                    location_name="Seppings Island",
                    zone_name="High",
                    sub_zone_name="High",
                    wave_exp_name="exposed",
                    date_pick_from=datetime.date(1995, 4, 15).strftime('%m/%d/%Y'),
                    date_pick_to=datetime.date(2016, 4, 30).strftime('%m/%d/%Y')),
                    follow_redirects=True)
            self.assertIn(b"[(&#39;robomussel&#39;, 13.98), (&#39;robomussel&#39;, 12.87)]", response.data)

            # self.assertIn((robomussel, 13.98), (&#39;robomussel&#39;, 12.87)

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