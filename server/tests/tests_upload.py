# imports
from io import BytesIO
import unittest, os, datetime
from flask import Flask, json, request, Response, session, jsonify
from werkzeug.datastructures import (ImmutableMultiDict, FileStorage)
from flask.ext.uploads import TestingFileStorage
import MySQLdb
from app import app
from app.dbconnect import DbConnect


class UploadTestCase(unittest.TestCase):
    """Upload Feature specific Test Cases will go here"""
    
    def setUp(self):
        """Setup test app"""
        app.config['TESTING'] = True     
        app.config['MYSQL_DB'] = 'test'   
        self.db = DbConnect(app.config)

    def tearDown(self):
        """Close test database"""        
        self.db.close()
    
    def cleanUp(self, cursor, rec):
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
    
    def stringToBytes(self, stringValue):
        """Convert Strings to their Bytes representation"""
        return bytes(stringValue, 'UTF-8')

    def test_uploaded_logger_type_file_extension(self):
        """Test that uploaded logger type file has correct extensions"""
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (BytesIO(b'logger Type File'), 
                                        'correctExtensionLoggerTypeFile.csv')
                    }, follow_redirects=True)
            self.assertNotIn(b'File should be in csv format', response.data)

    def test_uploaded_logger_temp_file_extension(self):
        """Test that uploaded logger temperature file has correct extensions"""
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTempFile':  (BytesIO(b'logger Temp File'), 
                                        'correctExtensionLoggerTempFile.csv')
                    }, follow_redirects=True)
            self.assertNotIn(b'File correctExtensionLoggerTempFile.pdf should be in csv or txt format', response.data)

    def test_uploaded_logger_type_file_extension_negative(self):
        """Test that uploaded logger type file has correct extensions"""
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (BytesIO(b'logger Type File'), 
                                        'incorrectExtensionLoggerTypeFile.txt')
                    }, follow_redirects=True)
            self.assertIn(b'File should be in csv format', response.data)

    def test_uploaded_logger_temp_file_extension_negative(self):
        """Test that uploaded logger temperature file has correct extensions"""
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTempFile':  (BytesIO(b'logger Temp File'), 
                                        'incorrectExtensionLoggerTypeFile.pdf')
                    }, follow_redirects=True)
            self.assertIn(b'File incorrectExtensionLoggerTypeFile.pdf should be in csv or txt format', response.data)

    def test_uploaded_logger_type_file_missing(self):
        """Test that uploaded logger type file is not missing"""
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (BytesIO(b'logger Type File'), '')
                    }, follow_redirects=True)
            self.assertIn(b'Please choose a File first', response.data)

    def test_uploaded_logger_temp_file_missing(self):
        """Test that uploaded logger temp file is not missing"""
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTempFile':  (BytesIO(b'logger Temp File'), '')
                    }, follow_redirects=True)
            self.assertIn(b'Please choose a File first', response.data)


    def test_logger_type_upload(self):
        """Test that file with valid uploads is inserted in DB."""
        test_filename = 'server/tests/test_data_files/Test/Test_New_Logger_Type_Positive.csv'
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (open(test_filename, 'rb'), 'Test_New_Logger_Type_Positive.csv')
                    }, follow_redirects=True)
            record = {
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
            where_condition = self.db.buildWhereCondition(record)
            query = ("SELECT logger.microsite_id "
                    "FROM `cnx_logger` logger "
                    "INNER JOIN `cnx_logger_biomimic_type` biotype ON biotype.`biomimic_id` = logger.`biomimic_id` "
                    "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id` = logger.`geo_id` "
                    "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id` = logger.`prop_id` ")
            cursor = self.db.connection.cursor()
            cursor.execute(query  + where_condition)
            results = cursor.fetchone()
            if results is not None:
                results = results[0]     
            self.cleanUp(cursor, record)
            cursor.close()
            self.assertEqual(record['microsite_id'], results)

    def test_logger_type_upload_corrupt(self):
        """Test that Logger Type file with corrupt records cannot be uploaded"""
        test_filename = 'server/tests/test_data_files/Test/Test_New_Logger_Type_Corrupt.csv'
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (open(test_filename, 'rb'), 'Test_New_Logger_Type_Corrupt.csv')
                    }, follow_redirects=True)
            record_corrupt_ncolumns = {
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
            where_condition = self.db.buildWhereCondition(record_corrupt_ncolumns)
            query = ("SELECT logger.microsite_id "
                    "FROM `cnx_logger` logger "
                    "INNER JOIN `cnx_logger_biomimic_type` biotype ON biotype.`biomimic_id` = logger.`biomimic_id` "
                    "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id` = logger.`geo_id` "
                    "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id` = logger.`prop_id` ")
            cursor = self.db.connection.cursor()
            cursor.execute(query  + where_condition)
            results = cursor.fetchall()
            results = list(results)
            self.assertEqual(len(results), 0)

            record_corrupt_coordinates = {
                                            "microsite_id" : "DUMMYID",
                                            "site" : "DUMMYSITE",
                                            "biomimic_type" : "Dummybiomimictype",
                                            "country" : "Dummycountry",
                                            "state_province" : "Dummystate",
                                            "location" : "Dummylocation",
                                            "field_lat" : "A36.621933330000",
                                            "field_lon" : "-121.905316700000",
                                            "zone" : "Dummy",
                                            "sub_zone" : "Dummy",
                                            "wave_exp" : "Dummy"}
            where_condition = self.db.buildWhereCondition(record_corrupt_coordinates)
            query = ("SELECT logger.microsite_id "
                    "FROM `cnx_logger` logger "
                    "INNER JOIN `cnx_logger_biomimic_type` biotype ON biotype.`biomimic_id` = logger.`biomimic_id` "
                    "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id` = logger.`geo_id` "
                    "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id` = logger.`prop_id` ")
            cursor = self.db.connection.cursor()
            cursor.execute(query  + where_condition)
            results = cursor.fetchall()
            results = list(results)
            self.assertEqual(len(results), 0)
            cursor.close()

    def test_logger_type_upload_duplicate(self):
        """Test that Logger Type file with duplicate Microsite Id cannot be uploaded"""
        test_filename = 'server/tests/test_data_files/Test/Test_New_Logger_Type_Duplicate.csv'
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (open(test_filename, 'rb'), 'Test_New_Logger_Type_Duplicate.csv')
                    }, follow_redirects=True)
            record = {
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
            where_condition = self.db.buildWhereCondition(record)
            query = ("SELECT logger.microsite_id "
                    "FROM `cnx_logger` logger "
                    "INNER JOIN `cnx_logger_biomimic_type` biotype ON biotype.`biomimic_id` = logger.`biomimic_id` "
                    "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id` = logger.`geo_id` "
                    "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id` = logger.`prop_id` ")
            cursor = self.db.connection.cursor()
            cursor.execute(query  + where_condition)
            results = cursor.fetchall()
            results = list(results)
            self.cleanUp(cursor, record)            
            cursor.close()
            self.assertEqual(len(results), 1)
    
    def test_logger_temperature_upload(self):
        """Test that file with valid uploads is inserted in DB."""
        with app.test_client() as client:
            pass

    def test_logger_temperature_upload_corrupt(self):
        """Test that Logger Temperature file with corrupt records cannot be uploaded"""
        with app.test_client() as client:
            pass

    def test_logger_temperature_upload_missing(self):
        """Test that Logger Temperature file with missing Microsite Id cannot be uploaded"""
        with app.test_client() as client:
            pass            

if __name__ == '__main__':
    unittest.main()