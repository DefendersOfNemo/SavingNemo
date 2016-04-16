import unittest, os, datetime
from flask import Flask, json, request, Response, session
import MySQLdb
from app.views import create_app
from app.dbconnect import DbConnect
from flask.ext import excel

class QueryFormTestEdgeCase(unittest.TestCase):
    """Test for query functionality while wave_exp is none"""
    
    def setUp(self):
        """Setup test app"""
        self.app = create_app('tests.config')
        self.db = DbConnect(self.app.config)
        test_type_filename = 'server/tests/test_data_files/Test/Test_New_Logger_Type_WaveExp_None.csv'
        test_temp_filename = 'server/tests/test_data_files/Test/temp_files/DUMMYIDWAVENA_2000_pgsql.txt'
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['logged_in'] = True
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (open(test_type_filename, 'rb'), 'Test_New_Logger_Type_WaveExp_None.csv')
                    }, follow_redirects=True)
            response = client.post('/upload', 
                data={
                    'loggerTempFile':  (open(test_temp_filename, 'rb'), 'DUMMYIDWAVENA_2000_pgsql.txt')
                    }, follow_redirects=True)
            self.record_type = {
                        "microsite_id" : "DUMMYIDWAVENA",
                        "site" : "DUMMYSITE",
                        "biomimic_type" : "Dummybiomimictype",
                        "country" : "Dummycountry",
                        "state_province" : "Dummystate",
                        "location" : "Dummylocation",
                        "field_lat" : "36.621933330000",
                        "field_lon" : "-121.905316700000",
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : None}
    def tearDown(self):
        """Close test database"""        
        cursor = self.db.connection.cursor()
        self.clean_up_logger_temp(cursor)
        self.clean_up_logger_type(cursor, self.record_type)
        cursor.close()
        self.db.close()

    def stringToBytes(self, stringValue):
        """Convert Strings to their Bytes representation"""
        return bytes(stringValue, 'utf-8')

    def clean_up_logger_temp(self, cursor):
        cursor.execute("SELECT logger_temp_id FROM `cnx_logger_temperature`")
        results = cursor.fetchall()
        if results is not None:
            results = list(results)        
        logger_temp_ids = [result[0] for result in results]        
        for logger_temp_id in logger_temp_ids:
            res = cursor.execute("DELETE FROM `cnx_logger_temperature` WHERE logger_temp_id=%s", (logger_temp_id,))
            self.db.connection.commit()

    def clean_up_logger_type(self, cursor, rec):
        biomimic_id = self.db.fetch_existing_bio_id(cursor, rec.get('biomimic_type'))
        geo_id = self.db.fetch_existing_geo_id(cursor, rec)
        prop_id = self.db.fetch_existing_prop_id(cursor, rec)
        logger_id = self.db.find_microsite_id(rec.get('microsite_id'))
        res = cursor.execute("DELETE FROM `cnx_logger` WHERE logger_id=%s", (logger_id,))
        self.db.connection.commit()
        res = cursor.execute("DELETE FROM `cnx_logger_biomimic_type` WHERE biomimic_id=%s", (biomimic_id,))
        self.db.connection.commit()
        res = cursor.execute("DELETE FROM `cnx_logger_geographics` WHERE geo_id=%s", (geo_id,))
        self.db.connection.commit()
        res = cursor.execute("DELETE FROM `cnx_logger_properties` WHERE prop_id=%s", (prop_id,))
        self.db.connection.commit()
    
    def test_form_logger_type_automatic_fill(self):
        """Test the logger_type field is filled automatically on page load"""
        with self.app.test_client() as client:
            response = client.get('/query')
            biomimic_type_choices = self.db.fetch_biomimic_types() 
            for biomimic_type in biomimic_type_choices:
                self.assertIn(self.stringToBytes(biomimic_type[0]), response.data)        
    
    def check_ajax(self, selected_type, selected_value, dbFunction):
        """Helper Function to test the ajax call functionality when
           given selected type field is selected with given value"""
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['query'] = self.record_type
            response = client.get('/_parse_data', 
                                query_string=dict(
                                    select_type=selected_type,
                                    select_value=selected_value))
            self.assertEqual(selected_type, request.args.get('select_type'))
            self.assertEqual(selected_value, request.args.get('select_value'))
            choices = dbFunction(session['query'])
            for choice in choices[0]:
                self.assertIn(self.stringToBytes(choice[0]), response.data)

    def test_form_logger_type_select(self):
        """Test the ajax call functionality if logger_type field is selected"""
        selected_type = "biomimic_type"
        selected_value = "DummyBiomimicType"
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['query'] = self.record_type
            response = client.get('/_parse_data', 
                                query_string=dict(
                                    select_type=selected_type,
                                    select_value=selected_value))
            self.assertEqual(selected_type, request.args.get('select_type'))
            self.assertEqual(selected_value, request.args.get('select_value'))            
            choices = self.db.fetch_distinct_countries_and_zones(self.record_type)
            country_list = choices[0]["country"]
            zone_list = choices[0]["zone"]
            for country in country_list:
                self.assertIn(self.stringToBytes(country), response.data)
            for zone in zone_list:
                self.assertIn(self.stringToBytes(zone), response.data)

    def test_form_country_name_select(self):
        """Test the ajax call functionality if country field is selected"""
        self.check_ajax("country", "DummyCountry", self.db.fetch_distinct_states)

    def test_form_state_name_select(self):
        """Test the ajax call functionality if state_province field is selected"""
        self.check_ajax("state_province", "DummyState", self.db.fetch_distinct_locations)

    def test_form_Zone_name_select(self):
        """Test the ajax call functionality if zone field is selected"""
        self.check_ajax("sub_zone", "DummyZoneType", self.db.fetch_distinct_sub_zones)    

    def test_form_SubZone_name_select(self):
        """Test the ajax call functionality if sub_zone_name field is selected"""
        self.check_ajax("wave_exp", "DummySubZone", self.db.fetch_distinct_wave_exposures)    

    def test_query_results_WaveExp_None(self):
        """Test the query results functionality"""
        with self.app.test_client() as client:
            response = client.get('/_submit_query', 
                        query_string={
                        "microsite_id" : "DUMMYIDWAVENA",
                        "site" : "DUMMYSITE",
                        "biomimic_type" : "Dummybiomimictype",
                        "country" : "Dummycountry",
                        "state_province" : "Dummystate",
                        "location" : "Dummylocation",
                        "field_lat" : "36.621933330000",
                        "field_lon" : "-121.905316700000",
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "N/A",
                        "start_date": "6/1/2000",
                        "end_date": "8/1/2000",
                        "output_type" : "Raw",
                        "analysis_type" : ""},
                            follow_redirects=False)            
            self.assertIn(b"14", response.data)
            self.assertIn(b"13.5", response.data)

if __name__ == '__main__':
	unittest.main()