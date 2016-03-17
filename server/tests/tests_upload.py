# imports
from io import BytesIO
import unittest, os, datetime
from flask import Flask, json, request, Response, session, jsonify
from werkzeug.datastructures import (ImmutableMultiDict, FileStorage)
from flask.ext.uploads import TestingFileStorage
import MySQLdb
from app import app


class UploadFormTestCase(unittest.TestCase):
    """Query Form Feature specific Test Cases will go here"""
    
    def setUp(self):
        """Setup test app"""
        app.config['TESTING'] = True     
        #self.db = DbConnect(app.config)

    def tearDown(self):
        """Close test database"""        
        #self.db.close()

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
            # testFile = open('tests/incorrectFormatLoggerTypeFile.pdf', 'r')
            # ts = TestingFileStorage(stream=testFile, filename='incorrectFormatLoggerTypeFile.pdf', content_type='text/plain')
            response = client.post('/upload', 
                data={
                    'loggerTypeFile':  (BytesIO(b'logger Type File'), 
                                        'incorrectExtensionLoggerTypeFile.txt')
                        #ImmutableMultiDict([('loggerTypeFile', ts)])
                            #FileStorage(stream=testFile, filename='incorrectFormatLoggerTypeFile.pdf', content_type='text/plain'))])

                    }, follow_redirects=True)
            #print(response.data)
            # testFile.close()
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
        """Test that uploaded logger type file is not missing"""
        with app.test_client() as client:
            response = client.post('/upload', 
                data={
                    'loggerTempFile':  (BytesIO(b'logger Temp File'), '')
                    }, follow_redirects=True)
            self.assertIn(b'Please choose a File first', response.data)


    def test_logger_type_upload(self):
        """Test that file with valid uploads is inserted in DB."""
        with app.test_client() as client:
            pass
        
    def test_logger_temperature_upload(self):
        """Test that file with valid uploads is inserted in DB."""
        with app.test_client() as client:
            pass

    def test_logger_type_upload_corrupt(self):
        """Test that file with invalid extensions cannot be uploaded"""
        with app.test_client() as client:
            pass
        
    def test_logger_temperature_upload_corrupt(self):
        """Test that file with invalid extensions cannot be uploaded"""
        with app.test_client() as client:
            pass

    def test_logger_type_upload_existing(self):
        """Test that file with invalid extensions cannot be uploaded"""
        with app.test_client() as client:
            pass
        
    def test_logger_temperature_upload_missing(self):
        """Test that file with invalid extensions cannot be uploaded"""
        with app.test_client() as client:
            pass
            #self.assertIn(b"Logger Microsite Id missing in DB.Please add Logger Details first.", response.data)

if __name__ == '__main__':
    unittest.main()