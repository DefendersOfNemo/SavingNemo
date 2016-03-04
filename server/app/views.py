# imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from .forms import QueryForm
from app import app
from app.dbconnect import DbConnect
from flask.ext import excel

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
    results = None
    db = DbConnect(app.config)
    logger_type_choices = db.getLoggerTypes()
    db.close()

    form = QueryForm(request.form)
    form.logger_type.choices = logger_type_choices


    if request.method == 'GET':
        form.process()
    else:   
        pass
        # if form.validate_on_submit():
        
            # flash("Query details. logger_type: '%s', country_name: '%s', \
            #              state_name: '%s', location_name: '%s', \
            #              Date From: '%s', Date To: '%s' " % \

        # else:
        #     error = 'Invalid Submission. All fields marked with * are compulsory'
    return render_template('query.html', title='Query', form=form, error=error)

@app.route('/_submit_query', methods=['GET'])
def submit_query():
    print("inside submit")
    form  = dict(request.args)
    print("form")
    print(form)
    query = {}
    query["logger_type"] = form.get("logger_type")[0]
    query["country_name"] = form.get("country_name")[0]
    if form['state_name'][0] is not None:
        query["state_name"] = form['state_name'][0]
    if form['location_name'][0] is not None:
        query["location_name"] = form['location_name'][0]
    if form['zone_name'][0] is not None:
        query["zone_name"] = form['zone_name'][0]
    if form['sub_zone_name'][0] is not None:
        query["sub_zone_name"] = form['sub_zone_name'][0]
    if form["wave_exp"][0] is not '':
        query["wave_exp"] = form['wave_exp'][0]        
    query["start_date"] = form['start_date'][0] 
    query["end_date"] = form['end_date'][0]
    print("query")
    print(query)
    db = DbConnect(app.config)
    query_results = db.getQueryResults(query)
    session['query_raw_results'] = db.getQueryRawResults(query)
    db.close()
    session['query_info'] = query;

    results = query_results
    return jsonify(list_of_results=results)

@app.route('/download',methods=['GET'])
def download():
    #download raw data
    return excel.make_response_from_array(session['query_raw_results'], "csv", file_name="export_data")


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