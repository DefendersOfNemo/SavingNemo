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
        app.config['MYSQL_DB'] = 'test'
        self.db = DbConnect(app.config)
        test_type_filename = 'server/tests/test_data_files/Test/Test_New_Logger_Type_Positive.csv'
        test_temp_filename = 'server/tests/test_data_files/Test/temp_files/DUMMYID_2000_pgsql.txt'
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (open(test_type_filename, 'rb'), 'Test_New_Logger_Type_Positive.csv')
                    }, follow_redirects=True)
            response = client.post('/upload', 
                data={
                    'loggerTempFile':  (open(test_temp_filename, 'rb'), 'DUMMYID_2000_pgsql.txt')
                    }, follow_redirects=True)
            self.record_type = {
                        "microsite_id" : "DUMMYID",
                        "site" : "DUMMYSITE",
                        "biomimic_type" : "Dummybiomimictype",
                        "country" : "Dummycountry",
                        "state_province" : "Dummystate",
                        "location" : "Dummylocation",
                        "field_lat" : "36.621933330000",
                        "field_lon" : "-121.905316700000",
                        "zone" : "Dummy",
                        "sub_zone" : "Dummy",
                        "wave_exp" : "Dummy"}
    def tearDown(self):
        """Close test database"""        
        cursor = self.db.connection.cursor()
        self.cleanUpLoggerTemp(cursor)
        self.cleanUpLoggerType(cursor, self.record_type)
        cursor.close()
        self.db.close()


    def stringToBytes(self, stringValue):
        """Convert Strings to their Bytes representation"""
        return bytes(stringValue, 'UTF-8')

    def cleanUpLoggerTemp(self, cursor):
        cursor.execute("SELECT logger_temp_id FROM `cnx_logger_temperature`")
        results = cursor.fetchall()
        if results is not None:
            results = list(results)        
        logger_temp_ids = [result[0] for result in results]        
        for logger_temp_id in logger_temp_ids:
            res = cursor.execute("DELETE FROM `cnx_logger_temperature` WHERE logger_temp_id=\'%s\'" % (logger_temp_id))
            self.db.connection.commit()

    def cleanUpLoggerType(self, cursor, rec):
        biomimic_id = self.db.fetchExistingBioId(cursor, rec.get('biomimic_type'))
        geo_id = self.db.fetchExistingGeoId(cursor, rec)
        prop_id = self.db.fetchExistingPropId(cursor, rec)
        logger_id = self.db.FindMicrositeId(rec.get('microsite_id'))
        res = cursor.execute("DELETE FROM `cnx_logger` WHERE logger_id=%s", logger_id)
        self.db.connection.commit()
        res = cursor.execute("DELETE FROM `cnx_logger_biomimic_type` WHERE biomimic_id=%s", biomimic_id)
        self.db.connection.commit()
        res = cursor.execute("DELETE FROM `cnx_logger_geographics` WHERE geo_id=%s", geo_id)
        self.db.connection.commit()
        res = cursor.execute("DELETE FROM `cnx_logger_properties` WHERE prop_id=%s", prop_id)
        self.db.connection.commit()

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
                        "microsite_id" : "DUMMYID",
                        "site" : "DUMMYSITE",
                        "biomimic_type" : "Dummybiomimictype",
                        "country" : "Dummycountry",
                        "state_province" : "Dummystate",
                        "location" : "Dummylocation",
                        "field_lat" : "36.621933330000",
                        "field_lon" : "-121.905316700000",
                        "zone" : "Dummy",
                        "sub_zone" : "Dummy",
                        "wave_exp" : "Dummy",
                        "start_date": datetime.datetime.strptime("7/1/2000 2:21", '%m/%d/%Y %H:%M'),
                        "end_date": datetime.datetime.strptime("7/1/2000 2:21", '%m/%d/%Y %H:%M')},
                            follow_redirects=False)            
            self.assertIn(b"14", response.data)
            self.assertIn(b"13.5", response.data)
            
            # Merging with the above test case, since we are storing the query in the sessin variable
            """Test the download functionality"""
            response = client.get('/download')
            self.assertIn(b"14", response.data)
            self.assertIn(b"13.5", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

if __name__ == '__main__':
    unittest.main()