# imports
import unittest, os, datetime
from flask import json, request, Response, session
import MySQLdb
from app.views import create_app
from app.dbconnect import DbConnect

class BasicConnectionTestCase(unittest.TestCase):
    """Checks for app and db connectivity"""

    def setUp(self):
        """Setup test app"""
        self.app = create_app('app.config')

    def tearDown(self):
        """Destroy test app"""
    
    def test_index(self):
        """inital Test. Ensure flask is setup correctly"""
        response = self.app.test_client().get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_db_connection_positive(self):
        """"Test MySQL connection for connection"""        
        data = True
        try:
            with self.app.app_context():
                db = DbConnect(self.app.config)
                cursor = db.connection.cursor()
                res = cursor.execute('SELECT * from cnx_logger_biomimic_type LIMIT 2')
                res = cursor.execute('SELECT * from cnx_logger_properties LIMIT 2')
                res = cursor.execute('SELECT * from cnx_logger_geographics LIMIT 2')
                res = cursor.execute('SELECT * from cnx_logger LIMIT 2')
                res = cursor.execute('SELECT * from cnx_logger_temperature LIMIT 2')
        except (MySQLdb.OperationalError, MySQLdb.ProgrammingError) as e:
            data = None       
        finally:
            cursor.close()
            db.close()     
        self.assertNotEqual(data, None)

    def test_db_connection_username_negative(self):
        """"Test MySQL connection given incorrect username"""
        try:
            with self.app.app_context():
                db=MySQLdb.connect(
                    host=self.app.config['MYSQL_HOST'], \
                    port=self.app.config['MYSQL_PORT'], \
                    user='dummy', \
                    passwd=self.app.config['MYSQL_PASSWORD'], \
                    db=self.app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type LIMIT 2')
                c.execute('SELECT * from cnx_logger_properties LIMIT 2')
                c.execute('SELECT * from cnx_logger_geographics LIMIT 2')
                c.execute('SELECT * from cnx_logger LIMIT 2')
                c.execute('SELECT * from cnx_logger_temperature  LIMIT 2')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_password_negative(self):
        """"Test MySQL connection given incorrect password """
        try:
            with self.app.app_context():
                db=MySQLdb.connect(
                    host=self.app.config['MYSQL_HOST'], \
                    port=self.app.config['MYSQL_PORT'], \
                    user=self.app.config['MYSQL_USER'], \
                    passwd='dummy', \
                    db=self.app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type LIMIT 2')
                c.execute('SELECT * from cnx_logger_properties LIMIT 2')
                c.execute('SELECT * from cnx_logger_geographics LIMIT 2')
                c.execute('SELECT * from cnx_logger LIMIT 2')
                c.execute('SELECT * from cnx_logger_temperature LIMIT 2')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_host_negative(self):
        """"Test MySQL connection given incorrect hostname"""
        try:
            with self.app.app_context():
                db=MySQLdb.connect(
                    host='dummy', \
                    port=self.app.config['MYSQL_PORT'], \
                    user=self.app.config['MYSQL_USER'], \
                    passwd=self.app.config['MYSQL_PASSWORD'],\
                    db=self.app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type LIMIT 2')
                c.execute('SELECT * from cnx_logger_properties LIMIT 2')
                c.execute('SELECT * from cnx_logger_geographics LIMIT 2')
                c.execute('SELECT * from cnx_logger LIMIT 2')
                c.execute('SELECT * from cnx_logger_temperature  LIMIT 2')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_dbname_negative(self):
        """"Test MySQL connection given incorrect Database"""
        try:
            with self.app.app_context():
                db=MySQLdb.connect(
                    host=self.app.config['MYSQL_HOST'], \
                    port=self.app.config['MYSQL_PORT'], \
                    user=self.app.config['MYSQL_USER'], \
                    passwd=self.app.config['MYSQL_PASSWORD'],\
                    db='dummy')
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type LIMIT 2')
                c.execute('SELECT * from cnx_logger_properties LIMIT 2')
                c.execute('SELECT * from cnx_logger_geographics LIMIT 2')
                c.execute('SELECT * from cnx_logger LIMIT 2')
                c.execute('SELECT * from cnx_logger_temperature  LIMIT 2')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

if __name__ == '__main__':
    unittest.main()