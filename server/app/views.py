# imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from .forms import QueryForm
from app import app
from app.dbconnect import DbConnect
from flask.ext import excel
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage


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
    session['query'] = query
    db = DbConnect(app.config)
    preview_results = db.getQueryResults(query)
    db.close()
    return jsonify(list_of_results=preview_results)

@app.route('/download',methods=['GET'])
def download():    
    db = DbConnect(app.config)
    query = session['query']
    header = [("logger_type:"+query["logger_type"],"country_name:"+query["country_name"],"state_name:"+query["state_name"],"location_name:"+query["location_name"],"zone_name:"+query["zone_name"],"sub_zone_name:"+query["sub_zone_name"],"wave_exp:"+query["wave_exp"]),("Timestamp","Temperature")]
    query_results =header  + db.getQueryRawResults(session['query'])
    db.close()
    return excel.make_response_from_array(query_results, "csv", file_name="export_data")

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



ALLOWED_EXTENSIONS_LOGGER_TYPE = set(['csv'])
ALLOWED_EXTENSIONS_LOGGER_TEMP = set(['csv', 'txt'])

def allowed_file(filetype, filename):
    if filetype == "loggerTypeFile":
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_LOGGER_TYPE
    elif filetype == "loggerTempFile":
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_LOGGER_TEMP
    else:
        return False

@app.route('/upload', methods=['GET','POST'])
def upload():   
    result = None;
    error=None;
    if request.method == 'POST':
        #print("request.files ",request.files)
        if 'loggerTypeFile' in request.files:
            file = request.files['loggerTypeFile']
            #print(file)
            if file:
                if allowed_file("loggerTypeFile", file.filename):
                    pass
                    #print("contents", list(file.stream))
                    #result = AddLoggerType(file.stream)
                else:
                    #print('File should be in "csv" format')
                    error = "File should be in csv format"
            else:
                #print("Error! File not selected")
                error = "Please choose a File first"
                #flash ('please choose a file first')
            file.close()        
        elif 'loggerTempFile' in request.files:
            files = request.files.getlist('loggerTempFile')
            #print(files[0])
            if files[0]:
                for file in files:
                    if allowed_file("loggerTempFile", file.filename):
                        pass
                        #print("contents", list(file.stream))
                        #result = AddLoggerTemp(file.stream)                        
                    else:
                        #print('File {0} should be in "csv" or "txt" format'.format(file.filename))
                        error = "File " + file.filename + " should be in csv or txt format"
                    file.close()
            else:
                print("Error! File not selected")
                error = "Please choose a File first"
        else:
            error = "Something went wrong!"
    return render_template('upload.html', result=result, error=error)

def AddLoggerType(file):
    for record in file:
        parsedRecord = parseLoggerType(str(record))
        res = insertIntoDB(parsedRecord)
    return  res
    #{"total": 0, "success": 0, "failure": 0, "corruptRecordIds": [], "corruptRecords": []}

def AddLoggerTemp(file):
    for record in file:
        parsedRecord = parseLoggerTemp(str(record))
        res = insertIntoDB(parsedRecord)
    return  res
    #return  {"total": 0, "success": 0, "failure": 0, "corruptRecordIds": [], "corruptRecords": []}

# This function makes sure the server only runs if the script is executed directly
# from the Python interpreter and not used as an imported module.
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)