# imports
import unittest, os, datetime
from flask import json, request, Response, session
import MySQLdb
from app import app
from app.dbconnect import DbConnect

class BasicConnectionTestCase(unittest.TestCase):
    """Checks for app and db connectivity"""
    
    def test_index(self):
        """inital Test. Ensure flask is setup correctly"""
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_db_connection_positive(self):
        """"Test MySQL connection for connection"""        
        data = True
        try:
            with app.app_context():
                app.config['TESTING'] = True     
                app.config['MYSQL_DB'] = 'logger'
                db = DbConnect(app.config)
                cursor = db.connection.cursor()
                res = cursor.execute('SELECT * from cnx_logger_biomimic_type')
                res = cursor.execute('SELECT * from cnx_logger_properties')
                res = cursor.execute('SELECT * from cnx_logger_geographics')
                res = cursor.execute('SELECT * from cnx_logger')
                res = cursor.execute('SELECT * from cnx_logger_temperature')                
        except (MySQLdb.OperationalError, MySQLdb.ProgrammingError) as e:
            data = None       
        finally:
            cursor.close()
            db.close()     
        self.assertNotEqual(data, None)

    def test_db_connection_username_negative(self):
        """"Test MySQL connection given incorrect username"""
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user='dummy', \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temperature')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_password_negative(self):
        """"Test MySQL connection given incorrect password """
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd='dummy', \
                    db=app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temperature')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_host_negative(self):
        """"Test MySQL connection given incorrect hostname"""
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host='dummy', \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'],\
                    db=app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temperature')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_dbname_negative(self):
        """"Test MySQL connection given incorrect Database"""
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'],\
                    db='dummy')
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_biomimic_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temperature')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

if __name__ == '__main__':
    unittest.main()