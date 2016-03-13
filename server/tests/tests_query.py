# imports
import unittest, os, datetime
from flask import Flask, json, request, Response, session
import MySQLdb
from app import app
from app.dbconnect import DbConnect
from flask.ext import excel


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
            response = client.get('/_submit_query', 
                query_string={
                'sub_zone_name': ['High'], 
                'end_date': ['04/12/2016'], 
                'state_name': ['British Columbia'], 
                'wave_exp': ['exposed'], 
                'location_name': ['Seppings Island'], 
                'zone_name': ['High'], 
                'logger_type': ['robomussel'], 
                'start_date': ['03/01/2016'], 
                'country_name': ['Canada']},
                    follow_redirects=True)
            self.assertIn(b"13.98", response.data)
            self.assertIn(b"12.87", response.data)

            """Test the download functionality"""
            response_download = client.get('/download')
            self.assertIn(b"13.98", response_download.data)
            self.assertIn(b"12.87", response_download.data)
            self.assertIn(b"logger_type:robomussel", response_download.data)


if __name__ == '__main__':
    unittest.main()