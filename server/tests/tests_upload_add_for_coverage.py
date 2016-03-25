# imports
from io import BytesIO
import unittest, os, datetime
from flask import Flask, json, request, Response, session, jsonify
from werkzeug.datastructures import (ImmutableMultiDict, FileStorage)
from flask.ext.uploads import TestingFileStorage
import MySQLdb
from app import app
from app.dbconnect import DbConnect
import datetime

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
    
    def cleanUpLoggerTemp(self, cursor):
        ''' clean up table cnx_logger_temperature'''
        cursor.execute("SELECT logger_temp_id FROM `cnx_logger_temperature`")
        results = cursor.fetchall()
        if results is not None:
            results = list(results)        
        logger_temp_ids = [result[0] for result in results]        
        for logger_temp_id in logger_temp_ids:
            res = cursor.execute("DELETE FROM `cnx_logger_temperature` WHERE logger_temp_id=\'%s\'" % (logger_temp_id))
            self.db.connection.commit()

    def cleanUpLoggerType(self, cursor, rec):
        ''' clean up logger type tables'''
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

    def test_logger_type_upload_MicrositeId_None(self):
        """Test that upload Logger Type file without microsite_id will not be inserted to database"""
        test_filename = 'server/tests/test_data_files/Test/Test_New_Logger_Type_MicrositeId_None.csv'
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (open(test_filename, 'rb'), 'Test_New_Logger_Type_MicrositeId_None.csv')
                    }, follow_redirects=True)
            query = ("SELECT * from  cnx_logger_biomimic_type where biomimic_type='DummyBiomimicTypeNone'")
            cursor = self.db.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            results = list(results)
            self.assertEqual(len(results), 0)

    def test_logger_temperature_upload_duplicate(self):
        """Test that Logger Temperature file with duplicate entry cannot be uploaded"""
        test_type_filename = 'server/tests/test_data_files/Test/Test_New_Logger_Type_Positive.csv'
        test_temp_filename = 'server/tests/test_data_files/Test/temp_files/DUMMYID_2000_pgsql_Duplicate.txt'
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (open(test_type_filename, 'rb'), 'Test_New_Logger_Type_Positive.csv')
                    }, follow_redirects=True)
            response = client.post('/upload', 
                data={
                    'loggerTempFile':  (open(test_temp_filename, 'rb'), 'DUMMYID_2000_pgsql_Duplicate.txt')
                    }, follow_redirects=True)
            record_type = {
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
            where_condition = self.db.buildWhereCondition(record_type)
            query = ("SELECT temp.Time_GMT, temp.Temp_C  "
                    "FROM `cnx_logger` logger "
                    "INNER JOIN `cnx_logger_biomimic_type` biotype ON biotype.`biomimic_id` = logger.`biomimic_id` "
                    "INNER JOIN `cnx_logger_geographics` geo ON geo.`geo_id` = logger.`geo_id` "
                    "INNER JOIN `cnx_logger_properties` prop ON prop.`prop_id` = logger.`prop_id` "
                    "INNER JOIN `cnx_logger_temperature` temp ON temp.`logger_id` = logger.`logger_id` ")
            cursor = self.db.connection.cursor()
            cursor.execute(query  + where_condition)
            results = cursor.fetchall()
            results = list(results)
            self.cleanUpLoggerTemp(cursor)
            self.cleanUpLoggerType(cursor, record_type)            
            cursor.close()
            self.assertEqual(len(results), 1)

if __name__ == '__main__':
    unittest.main()