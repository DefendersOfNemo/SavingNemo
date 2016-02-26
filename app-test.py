# imports
import unittest, os, datetime
from flask import json, request, Response, session
import MySQLdb
from nemoApp import app

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

class SavingNemoTestCase(unittest.TestCase):
    """SavingNemo Feature specific Test Cases will go here"""

    def setUp(self):
        """Setup test app"""
        app.config['TESTING'] = True

    def tearDown(self):
        """Destroy test app"""
        # ...

    def login(self, c, username, password):
        """Login helper function"""
        return c.post('/login', data=dict(
            username=username,
            password=password,
            ), follow_redirects=True)

    def logout(self, c):
        """Logout helper function"""
        return c.get('/logout', follow_redirects=True)

    def test_login_logout_good(self):
        """Test Login and Logout using helper functions"""      
        with app.test_client() as c:
            rv = self.login(c,
                app.config['USERNAME'],
                app.config['PASSWORD'])
            # Check log in successful
            self.assertEqual(request.path, '/query')
            # Check logged in session variable is set to True
            self.assertTrue(session.get('logged_in'))

            rv = self.logout(c)
            # Check log out successful
            self.assertEqual(request.path, '/logout')
            # Check logged in session variable is set to None
            self.assertEqual(session.get('logged_in'), None)

    def test_login_invalid_username(self):
        """Test login with Invalid Username"""
        with app.test_client() as c:
            # Check for Invalid Username
            rv = self.login(c,
                app.config['USERNAME'] + 'x',
                app.config['PASSWORD'])

            # Check log in fails
            self.assertEqual(request.path, '/login')
            # Check logged in session variable is set to None
            self.assertEqual(session.get('logged_in'), None)
            # Check if error message is displayed for invalid username
            self.assertIn(b"Invalid Username. Please try again.", rv.data)

    def test_login_invalid_password(self):
        """Test login with Invalid Password"""
        with app.test_client() as c:
            # Check for Invalid Password
            rv = self.login(c,
                app.config['USERNAME'],
                app.config['PASSWORD'] + 'x')
            # Check log in fails
            self.assertEqual(request.path, '/login')
            # Check logged in session variable is set to None
            self.assertEqual(session.get('logged_in'), None)
            # Check if error message is displayed for invalid password
            self.assertIn(b"Invalid Password. Please try again.", rv.data)

    def test_query_submit_good_values(self):
        """Test the QueryForm with proper values"""
        # Check Fields without redirection
        with app.test_client() as c:            
            rv = c.post('/query', 
                data=dict(
                    logger_type='Mussel',
                    country_name='USA',
                    state_name='Massachusetts', 
                    date_pick_from=datetime.date(1989, 1, 1).strftime('%m/%d/%Y'),
                    date_pick_to=datetime.date(2001, 4, 1).strftime('%m/%d/%Y')),
                follow_redirects=False)
            self.assertEqual(request.form.get('logger_type'), "Mussel")
            self.assertEqual(request.form.get('country_name'), "USA")
            self.assertEqual(request.form.get('state_name'), "Massachusetts")
            self.assertEqual(request.form.get('date_pick_from'), "01/01/1989")
            self.assertEqual(request.form.get('date_pick_to'), "04/01/2001")

    def test_query_submit_redirect_success(self):
        """Test redirection of QueryForm with proper values"""
        # Check successful redirection
        with app.test_client() as c:            
            rv = c.post('/query', 
                data=dict(
                    logger_type='Mussel',
                    country_name='USA',
                    state_name='Massachusetts', 
                    date_pick_from=datetime.date(1989, 1, 1).strftime('%m/%d/%Y'),
                    date_pick_to=datetime.date(2001, 4, 1).strftime('%m/%d/%Y')),
                follow_redirects=True)
            # Check successful redirection
            self.assertEqual(request.path, '/query')

    def test_query_submit_missing_compulsory_values(self):
        """Test the QueryForm with compulsory fields missing"""
        with app.test_client() as c:
            rv = c.post('/query', 
                data=dict( 
                    country_name='USA',
                    state_name='Massachusetts'), 
                follow_redirects=True)
            # Check Query Submission fails
            self.assertEqual(request.path, '/query')
            # Check if error message is displayed for invalid query
            self.assertIn(b'Invalid Submission. All fields marked with * are compulsory', rv.data)

if __name__ == '__main__':
    unittest.main()