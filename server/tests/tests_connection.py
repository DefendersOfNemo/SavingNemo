# imports
import unittest, os, datetime
from flask import json, request, Response, session
import MySQLdb
from app import app

class BasicConnectionTestCase(unittest.TestCase):
    """Checks for app and db connectivity"""
    
    def test_index(self):
        """inital Test. Ensure flask was setup correctly"""
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_db_connection_positive(self):
        """"Test MySQL connection"""
        
        data = None
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])
                c = db.cursor()
                res = c.execute('SELECT * from cnx_logger_type')
                res = c.execute('SELECT * from cnx_logger_properties')
                res = c.execute('SELECT * from cnx_logger_geographics')
                res = c.execute('SELECT * from cnx_logger')
                res = c.execute('SELECT * from cnx_logger_temp')                
                data = c.fetchone()
                c.close()
        except (MySQLdb.OperationalError, MySQLdb.ProgrammingError) as e:
            data = None            
        self.assertNotEqual(data, None)

    def test_db_connection_username_negative(self):
        """"Test MySQL connection"""
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user='jiayi', \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temp')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_password_negative(self):
        """"Test MySQL connection"""
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd='jiayi', \
                    db=app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temp')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_host_negative(self):
        """"Test MySQL connection"""
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host='jiayi', \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'],\
                    db=app.config['MYSQL_DB'])                
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temp')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_db_connection_dbname_negative(self):
        """"Test MySQL connection"""
        try:
            with app.app_context():
                db=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'],\
                    db='jiayi')
                c = db.cursor()
                c.execute('SELECT * from cnx_logger_type')
                c.execute('SELECT * from cnx_logger_properties')
                c.execute('SELECT * from cnx_logger_geographics')
                c.execute('SELECT * from cnx_logger')
                c.execute('SELECT * from cnx_logger_temp')                
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:
            data = None            
        self.assertEqual(data, None)

    def test_negative_db_dummy(self):
        """"Test table logger_type negative"""
        try:
            with app.app_context():
                connection=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])
                c = connection.cursor()
                res = c.execute('SELECT * from dummy')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:# 
            data = None
        self.assertEqual(data, None)

    def test_db_logger_type_nonempty(self):
        """"Test table logger_type positive"""
        try:
            with app.app_context():
                connection=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])
                c = connection.cursor()
                c.execute('SELECT * from cnx_logger_type')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:# 
            data = None
        self.assertNotEqual(data, None)

    def test_db_logger_properties_nonempty(self):
        """"Test table logger_properties positive"""
        try:
            with app.app_context():
                connection=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])
                c = connection.cursor()
                c.execute('SELECT * from cnx_logger_properties')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:# 
            data = None
        self.assertNotEqual(data, None)

    def test_db_logger_geographiscs_nonempty(self):
        """"Test table logger_geographics positive"""
        try:
            with app.app_context():
                connection=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])
                c = connection.cursor()
                res = c.execute('SELECT * from cnx_logger_geographics')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:# 
            data = None
        self.assertNotEqual(data, None)

    def test_db_logger_positive_nonempty(self):
        """"Test table logger positive"""
        try:
            with app.app_context():
                connection=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])
                c = connection.cursor()
                res = c.execute('SELECT * from cnx_logger')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:# 
            data = None
        self.assertNotEqual(data, None)

    def test_db_logger_temp_nonempty(self):
        """"Test table logger positive"""
        try:
            with app.app_context():
                connection=MySQLdb.connect(
                    host=app.config['MYSQL_HOST'], \
                    port=app.config['MYSQL_PORT'], \
                    user=app.config['MYSQL_USER'], \
                    passwd=app.config['MYSQL_PASSWORD'], \
                    db=app.config['MYSQL_DB'])
                c = connection.cursor()
                res = c.execute('SELECT * from cnx_logger_temp')
                data = c.fetchone()
                c.close()
        except MySQLdb.OperationalError as e:# 
            data = None
        self.assertNotEqual(data, None)

if __name__ == '__main__':
    unittest.main()