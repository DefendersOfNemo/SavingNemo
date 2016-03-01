# imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from .forms import QueryForm
from app import app
from app.dbconnect import DbConnect

@app.route('/')
@app.route('/home')
def index():
    """Searches the database for entries, then displays them."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid Username. Please try again."
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Password. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('query'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    flash('You are logged out')
    return render_template('logout.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    error = None
    db = DbConnect(app.config)
    logger_type_choices = db.getLoggerTypes() 
    db.close()

    form = QueryForm(request.form)
    form.logger_type.choices = logger_type_choices


    if request.method == 'GET':
        form.process()
    else:   
        query = {}
        query["logger_type"] = form.logger_type.data,
        query["country_name"] = form.country_name.data,
        if form.state_name.data is not None:
            query["state_name"] = form.state_name.data, 
        if form.location_name.data is not None:
            query["location_name"] = form.location_name.data,
        if form.zone_name.data is not None:
            query["zone_name"] = form.zone_name.data,
        if form.sub_zone_name.data is not None:
            query["sub_zone_name"] = form.sub_zone_name.data,
        if form.wave_exp_name.data is not None:
            query["wave_exp"] = form.wave_exp_name.data,        
        query["start_date"] = form.date_pick_from.data.strftime('%m/%d/%Y'), 
        query["end_date"] = form.date_pick_to.data.strftime('%m/%d/%Y')
        # print("query: ", query)    
        # print("Query form submitted")

        db = DbConnect(app.config)
        query_results = db.getQueryResults(query) 
        db.close()
        # print("results: ", query_results)
        flash(query_results)
        # if form.validate_on_submit():
        
            # flash("Query details. logger_type: '%s', country_name: '%s', \
            #              state_name: '%s', location_name: '%s', \
            #              Date From: '%s', Date To: '%s' " % \

        # else:
        #     error = 'Invalid Submission. All fields marked with * are compulsory'
    return render_template('query.html', title='Query', form=form, error=error)

@app.route('/_parse_data', methods=['GET'])
def parse_data():
    select_type = request.args.get('select_type', 'default')
    select_value = request.args.get('select_value', 'default')
    result = queryDb(select_type, select_value)
    return jsonify(result)

def queryDb(query_type, query_value):
    result = None
    db = DbConnect(app.config)
    if query_type == "logger_type": 
        result = db.getCountry(query_value)
    elif query_type == "country_name":
        result = db.getState(query_value)
    elif query_type == "state_name":
        result = db.getLocation(query_value)
    elif query_type == "lt_for_zone":
        result = db.getZone(query_value)
    elif query_type == "lt_for_subzone":
        result = db.getSubZone(query_value)
    elif query_type == "lt_for_wave_exp":
        result = db.getWaveExp(query_value)
    return result       

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# This function makes sure the server only runs if the script is executed directly
# from the Python interpreter and not used as an imported module.
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)