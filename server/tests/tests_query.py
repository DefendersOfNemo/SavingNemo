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
        app.config['MYSQL_DB'] = 'logger'
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
            biomimic_type_choices = self.db.getBiomimicTypes() 
            for biomimic_type in biomimic_type_choices:
                self.assertIn(self.stringToBytes(biomimic_type[0]), response.data)        
    
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
        self.check_ajax("biomimic_type", "Robomussel", self.db.getCountry)

    def test_form_country_name_select(self):
        """Test the ajax call functionality if country_name field is selected"""
        self.check_ajax("country_name", "Usa", self.db.getState)

    def test_form_state_name_select(self):
        """Test the ajax call functionality if state_name field is selected"""
        self.check_ajax("state_name", "California", self.db.getLocation)

    def test_form_location_name_select(self):
        """Test the ajax call functionality if location_name field is selected"""
        self.check_ajax("lt_for_zone", "Robomussel", self.db.getZone)

    def test_form_Zone_name_select(self):
        """Test the ajax call functionality if zone_name field is selected"""
        self.check_ajax("lt_for_subzone", "Robomussel", self.db.getSubZone)    

    def test_form_SubZone_name_select(self):
        """Test the ajax call functionality if subZone_name field is selected"""
        self.check_ajax("lt_for_wave_exp", "Robomussel", self.db.getWaveExp)    

    def test_query_results(self):
        """Test the query results functionality"""
        with app.test_client() as client:
            response = client.get('/_submit_query', 
                query_string={
                'biomimic_type': ['Robobarnacle'], 
                'country': ['Usa'],
                'state_province': ['California'], 
                'location': ['Hopkins'],
                'zone': ['Mid'], 
                'sub_zone': ['Mid'],
                'wave_exp': ['Exposed'], 
                'start_date': ['07/01/2000'], 
                'end_date': ['07/02/2000']
                },
                    follow_redirects=True)
            self.assertIn(b"14", response.data)
            self.assertIn(b"13.5", response.data)

            """Test the download functionality"""
            response_download = client.get('/download')
            self.assertIn(b"14", response_download.data)
            self.assertIn(b"13.5", response_download.data)
            self.assertIn(b"biomimic_type:Robobarnacle", response_download.data)


if __name__ == '__main__':
    unittest.main()