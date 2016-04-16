"""
    login.py
    ~~~~~~~~~~~~~~

    This script handles the login functionality in login.html

    :copyright: (c) 2016 by Abhijeet Sharma.
    :license: The MIT License (MIT), see LICENSE for more details.
"""

from flask import current_app, Blueprint, request, session, redirect, url_for, \
                  abort, render_template
from jinja2 import TemplateNotFound


#pylint: disable=invalid-name
login_page = Blueprint('login_page', __name__,
                       template_folder='../../client/templates')

@login_page.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    try:
        error = None
        if request.method == 'POST':
            if request.form['username'] != current_app.config['USERNAME']:
                error = "Invalid Username. Please try again."
            elif request.form['password'] != current_app.config['PASSWORD']:
                error = 'Invalid Password. Please try again.'
            else:
                session['logged_in'] = True
                return redirect(url_for('query_page.query'))
        return render_template('login.html', error=error)
    except TemplateNotFound:
        abort(404)

@login_page.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    return redirect(url_for('query_page.query'))
