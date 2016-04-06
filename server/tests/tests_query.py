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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave"}
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
        res = cursor.execute("DELETE FROM `cnx_logger` WHERE logger_id=%s" % (logger_id))
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
            biomimic_type_choices = self.db.fetch_biomimic_types() 
            for biomimic_type in biomimic_type_choices:
                self.assertIn(self.stringToBytes(biomimic_type[0]), response.data)        
    
    def check_ajax(self, selected_type, selected_value, dbFunction):
        """Helper Function to test the ajax call functionality when
           given selected type field is selected with given value"""
        with app.test_client() as client:
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

    def test_form_select_biomimic_type(self):
        """Test the ajax call functionality if logger_type field is selected"""
        selected_type = "biomimic_type"
        selected_value = "DummyBiomimicType"
        with app.test_client() as client:
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

    def test_form_select_country_name(self):
        """Test the ajax call functionality if country field is selected"""
        self.check_ajax("country", "DummyCountry", self.db.fetch_distinct_states)

    def test_form_select_state_province(self):
        """Test the ajax call functionality if state_province field is selected"""
        self.check_ajax("state_province", "DummyState", self.db.fetch_distinct_locations)

    def test_form_select_zone_name(self):
        """Test the ajax call functionality if zone field is selected"""
        self.check_ajax("zone", "DummyZone", self.db.fetch_distinct_sub_zones)    

    def test_form_select_sub_zone_name(self):
        """Test the ajax call functionality if sub_zone_name field is selected"""
        self.check_ajax("sub_zone", "DummySubZone", self.db.fetch_distinct_wave_exposures)    

    def test_query_results_raw(self):
        """Test the query results functionality for Raw"""
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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave",
                        "start_date": "7/1/2000",
                        "end_date": "7/2/2000",
                        "output_type" : "Raw"},
                            follow_redirects=False)            
            self.assertIn(b"14", response.data)
            self.assertIn(b"13.5", response.data)
            
            # Merging with the above test case, since we are storing the query in the sessin variable
            """Test the download functionality"""
            response = client.get('/download')
            self.assertIn(b"14", response.data)
            self.assertIn(b"13.5", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)
    
    def test_query_results_min_daily(self):
            """Test the query results functionality for Min Daily"""
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
                            "zone" : "DummyZone",
                            "sub_zone" : "DummySubZone",
                            "wave_exp" : "DummyWave",
                            "start_date": "7/1/2000",
                            "end_date": "7/2/2000",
                            "output_type" : "Min",
                            "analysis_type" : "Daily"},
                                follow_redirects=False)            
                self.assertIn(b"13.5", response.data)
                self.assertNotIn(b"14", response.data)
                
                #Test the download functionality
                response = client.get('/download')
                self.assertIn(b"13.5", response.data)
                self.assertNotIn(b"14", response.data)
                self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_max_daily(self):
        """Test the query results functionality for Max Daily"""
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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave",
                        "start_date": "7/1/2000",
                        "end_date": "7/2/2000",
                        "output_type" : "Max",
                        "analysis_type" : "Daily"},
                            follow_redirects=False)            
            self.assertIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            
            #Test the download functionality
            response = client.get('/download')
            self.assertIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_average_daily(self):
        """Test the query results functionality for Average Daily"""
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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave",
                        "start_date": "7/1/2000",
                        "end_date": "7/2/2000",
                        "output_type" : "Average",
                        "analysis_type" : "Daily"},
                            follow_redirects=False)            
            self.assertIn(b"13.75", response.data)
            self.assertNotIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            
            #Test the download functionality
            response = client.get('/download')
            self.assertIn(b"13.75", response.data)
            self.assertNotIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_min_monthly(self):
            """Test the query results functionality for Min Monthly"""
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
                            "zone" : "DummyZone",
                            "sub_zone" : "DummySubZone",
                            "wave_exp" : "DummyWave",
                            "start_date": "1/1/2000",
                            "end_date": "1/1/2003",
                            "output_type" : "Min",
                            "analysis_type" : "Monthly"},
                                follow_redirects=False)            
                self.assertIn(b"13.5", response.data)
                self.assertNotIn(b"14", response.data)
                self.assertIn(b"10", response.data)
                self.assertNotIn(b"20.0", response.data)
                self.assertIn(b"15", response.data)
                self.assertIn(b"7", response.data)
                
                #Test the download functionality
                response = client.get('/download')
                self.assertIn(b"13.5", response.data)
                self.assertNotIn(b"14", response.data)
                self.assertIn(b"10", response.data)
                self.assertNotIn(b"20.0", response.data)
                self.assertIn(b"15", response.data)
                self.assertIn(b"7", response.data)
                self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_max_monthly(self):
        """Test the query results functionality for Max Monthly"""
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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave",
                        "start_date": "1/1/2000",
                        "end_date": "1/1/2003",
                        "output_type" : "Max",
                        "analysis_type" : "Monthly"},
                            follow_redirects=False)            
            self.assertIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertIn(b"20.0", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertIn(b"15.0", response.data)
            self.assertIn(b"7", response.data)
            
            #Test the download functionality
            response = client.get('/download')
            self.assertIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertIn(b"20.0", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertIn(b"15.0", response.data)
            self.assertIn(b"7", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_average_monthly(self):
        """Test the query results functionality for Average Monthly"""
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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave",
                        "start_date": "1/1/2000",
                        "end_date": "1/1/2003",
                        "output_type" : "Average",
                        "analysis_type" : "Monthly"},
                            follow_redirects=False)            
            self.assertIn(b"13.75", response.data)
            self.assertNotIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertIn(b"15.0", response.data)
            self.assertIn(b"7.0", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertNotIn(b"20.0", response.data)
                        
            #Test the download functionality
            response = client.get('/download')
            self.assertIn(b"13.75", response.data)
            self.assertNotIn(b"14", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertIn(b"15.0", response.data)
            self.assertIn(b"7.0", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertNotIn(b"20.0", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_min_yearly(self):
            """Test the query results functionality for Min Yearly"""
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
                            "zone" : "DummyZone",
                            "sub_zone" : "DummySubZone",
                            "wave_exp" : "DummyWave",
                            "start_date": "1/1/2000",
                            "end_date": "1/1/2003",
                            "output_type" : "Min",
                            "analysis_type" : "Yearly"},
                                follow_redirects=False)            
                self.assertNotIn(b"13.5", response.data)
                self.assertNotIn(b"14", response.data)
                self.assertNotIn(b"20.0", response.data)
                self.assertIn(b"10", response.data)
                self.assertIn(b"15", response.data)
                self.assertIn(b"7", response.data)
                
                #Test the download functionality
                response = client.get('/download')
                self.assertNotIn(b"13.5", response.data)
                self.assertNotIn(b"14", response.data)
                self.assertNotIn(b"20.0", response.data)
                self.assertIn(b"10", response.data)
                self.assertIn(b"15", response.data)
                self.assertIn(b"7", response.data)
                self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_max_yearly(self):
        """Test the query results functionality for Max Yearly"""
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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave",
                        "start_date": "1/1/2000",
                        "end_date": "1/1/2003",
                        "output_type" : "Max",
                        "analysis_type" : "Yearly"},
                            follow_redirects=False)            
            self.assertNotIn(b"13.5", response.data)
            self.assertNotIn(b"14", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertIn(b"20.0", response.data)
            self.assertIn(b"15", response.data)
            self.assertIn(b"7", response.data)
            
            #Test the download functionality
            response = client.get('/download')
            self.assertNotIn(b"13.5", response.data)
            self.assertNotIn(b"14", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertIn(b"20.0", response.data)
            self.assertIn(b"15", response.data)
            self.assertIn(b"7", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)

    def test_query_results_average_yearly(self):
        """Test the query results functionality for Average Yearly"""
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
                        "zone" : "DummyZone",
                        "sub_zone" : "DummySubZone",
                        "wave_exp" : "DummyWave",
                        "start_date": "1/1/2000",
                        "end_date": "1/1/2003",
                        "output_type" : "Average",
                        "analysis_type" : "Yearly"},
                            follow_redirects=False)            
            self.assertIn(b"14.375", response.data)
            self.assertNotIn(b"14.0", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertNotIn(b"20.0", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertIn(b"15", response.data)
            self.assertIn(b"7", response.data)            
            
            #Test the download functionality
            response = client.get('/download')
            self.assertIn(b"14.375", response.data)
            self.assertNotIn(b"13.5", response.data)
            self.assertNotIn(b"14.0", response.data)
            self.assertNotIn(b"20.0", response.data)
            self.assertNotIn(b"10", response.data)
            self.assertIn(b"15", response.data)
            self.assertIn(b"7", response.data)
            self.assertIn(b"biomimic_type:Dummybiomimictype", response.data)


if __name__ == '__main__':
    unittest.main()