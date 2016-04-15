#coding:utf8
# imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from app.forms import QueryForm
from app.dbconnect import DbConnect
from flask.ext import excel
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
import io, csv, datetime, sys
import time

app = Flask(__name__, template_folder="../../client/templates", static_folder="../../client/static")
app.config.from_object('app.config')

################### Query ######################
@app.route('/')
@app.route('/query', methods=['GET', 'POST'])
def query():
    """Function for rendering the query form"""
    error = None
    results = None
    db = DbConnect(app.config)
    biomimic_type_choices = db.fetch_biomimic_types()
    db.close()
    form = QueryForm(request.form)
    form.biomimic_type.choices = biomimic_type_choices
    session['query'] = dict()
    if request.method == 'GET':
        form.process()
    else:   
        pass
    return render_template('query.html', title='Query', form=form, error=error)

@app.route('/_parse_data', methods=['GET'])
def parse_data():
    select_type = request.args.get('select_type', 'default')
    select_value = request.args.get('select_value', 'default')
    result, countRecords, minDate, maxDate = queryDb(select_type, select_value)
    return jsonify(result = result, countRecords = countRecords, minDate = minDate, maxDate = maxDate)

def queryDb(value_type, value):
    '''Query Database to get options for each drop-down menu'''
    result, countRecords, minDate, maxDate = None, None, None, None        
    db = DbConnect(app.config)
    keyList = ['biomimic_type', 'country', 'state_province', 'location', 'zone', 'sub_zone', \
                'wave_exp', 'start_date', 'end_date', 'output_type', 'analysis_type']
    # delete all keys in session variable "query" after the selected field
    for key in keyList[keyList.index(value_type) + 1:]:
        session['query'].pop(key, None)
    session['query'][value_type] = value
    if value_type == "biomimic_type": 
        result, countRecords, minDate, maxDate = db.fetch_distinct_countries_and_zones(session['query'])
    elif value_type == "country":        
        result, countRecords, minDate, maxDate  = db.fetch_distinct_states(session['query'])
    elif value_type == "state_province":
        result, countRecords, minDate, maxDate = db.fetch_distinct_locations(session['query'])
    elif value_type == "location":
        # location field doesn't have any associated dynamic behavior except for fetching metadata.
        countRecords, minDate, maxDate  = db.fetchMetadata(session['query']);
    elif value_type == "zone":
        result, countRecords, minDate, maxDate = db.fetch_distinct_sub_zones(session['query'])
    elif value_type == "sub_zone":
        result, countRecords, minDate, maxDate  = db.fetch_distinct_wave_exposures(session['query'])
    return result, countRecords, minDate, maxDate        

@app.route('/_submit_query', methods=['GET'])
def submit_query():
    '''get values of form and query Database to get preview results'''
    form  = dict(request.args)
    query = dict()
    query["biomimic_type"] = form.get("biomimic_type")[0]
    query["country"] = form.get("country")[0]
    query["state_province"] = form['state_province'][0]
    query["location"] = form['location'][0]
    query["zone"] = form['zone'][0]
    query["sub_zone"] = form['sub_zone'][0]
    query["wave_exp"] = form['wave_exp'][0]
    query["output_type"] = form['output_type'][0]
    if form.get('analysis_type') is not None:
        query["analysis_type"] = form['analysis_type'][0]        
    if (form.get('start_date')[0] != '') and (form.get('end_date')[0] != ''):
        query["start_date"] = str(datetime.datetime.strptime(form['start_date'][0],'%m/%d/%Y').date())
        query["end_date"] = str(datetime.datetime.strptime(form['end_date'][0],'%m/%d/%Y').date())
    session['query'] = query
    db = DbConnect(app.config)
    preview_results, db_query = db.getQueryResultsPreview(query)
    session['db_query'] = db_query
    db.close()
    return jsonify(list_of_results=preview_results)

@app.route('/download',methods=['GET'])
def download():
    '''Create download file in csv format, then file be downloaded to user's computer'''    
    db = DbConnect(app.config)
    query = session['query']
    db_query = session['db_query']
    time_title = ''
    if query.get("analysis_type") == "Daily":
        time_title = "Date"
    elif query.get("analysis_type") == "Monthly":
        time_title = "Month, Year"
    elif query.get("analysis_type") == "Yearly":
        time_title = "Year" 
    else:
        time_title = "Timestamp"
    header = [[key + ":" + str(value) for key, value in query.items()], (time_title,"Temperature")]    
    query_results = header  + db.getQueryRawResults(session['db_query'])
    db.close()
    return excel.make_response_from_array(query_results, "csv", file_name="export_data")

################### Upload ######################
ALLOWED_EXTENSIONS_LOGGER_TYPE = set(['csv'])
ALLOWED_EXTENSIONS_LOGGER_TEMP = set(['csv', 'txt'])

def allowed_file(filetype, filename):
    '''check whether uploaded file is in correct format'''
    if filetype == "loggerTypeFile":
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_LOGGER_TYPE
    else:
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_LOGGER_TEMP

@app.route('/upload', methods=['GET','POST'])
def upload():   
    '''Handle user upload functions, including logger type and logger temperature file'''
    # Interceptor for Upload
    if session.get('logged_in') is None:
        return redirect(url_for('query'))
    all_results = {'total': 0, 'success': 0, 'failure': 0, 'time_taken': 0}
    error = "";
    if request.method == 'POST':
        start_time = time.time()
        if 'loggerTypeFile' in request.files:
            file = request.files['loggerTypeFile']
            if file:
                all_results = dict()
                if allowed_file("loggerTypeFile", file.filename):
                    stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
                    csv_input = csv.reader(stream)
                    next(csv_input, None)  # skip the headers
                    all_results, corruptRecords = AddLoggerType(csv_input)
                else:
                    error = "File should be in csv format"
            else:
                error = "Please choose a file first"
            file.close()        
        elif 'loggerTempFile' in request.files:
            files = request.files.getlist('loggerTempFile')
            if files[0]:
                all_results = {'total': 0, 'success': 0, 'failure': 0, 'time_taken': 0}
                
                for file in files:
                    individual_result = None;
                    if allowed_file("loggerTempFile", file.filename):
                        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
                        if file.filename.rsplit('.', 1)[1] == 'txt':
                            csv_input = csv.reader(stream, delimiter = '\t')
                        else:
                            csv_input = csv.reader(stream)
                        next(csv_input, None)  # skip the headers                                                    
                        individual_result, errorMessage = AddLoggerTemp(csv_input, file.filename)
                        if individual_result is not None:
                            all_results['total'] += individual_result['total']
                            all_results['success'] += individual_result['success']
                            all_results['failure'] += individual_result['failure']
                        if errorMessage is not None:
                            error += errorMessage
                    else:
                        error += "File " + file.filename + " should be in csv or txt format\n"
                    file.close()                
            else:
                error = "Please choose a file first\n"
        end_time = time.time()
        all_results['time_taken'] = round(end_time - start_time, 2)
    if all_results is not None:
        if all_results.get('total') == 0:
            all_results = None
    return render_template('upload.html', result=all_results, error=error)

def AddLoggerType(reader):
    '''Insert logger type in file'''
    db = DbConnect(app.config)
    parsedRecords = list();
    totalCounter = 0;
    successCounter = 0;
    failureCounter = 0;
    errorMessage = None
    isParseError = False
    for record in reader:
        parsedRecordDict, isParseError = db.parseLoggerType(record)
        if not isParseError:
            parsedRecords.append(parsedRecordDict)
        else:
            failureCounter += 1
    totalCounter = len(parsedRecords) + failureCounter
    if len(parsedRecords) > 0:
        successCounter = db.insertLoggerType(parsedRecords)
    failureCounter += len(parsedRecords) - successCounter
    db.close()   
    return  {"total": totalCounter, "success": successCounter, "failure": failureCounter}, errorMessage

def AddLoggerTemp(reader, filename):
    '''Insert logger temperatures in uploaded file'''
    db = DbConnect(app.config)
    parsedRecords = list();    
    totalCounter = 0;
    successCounter = 0;
    failureCounter = 0;
    errorMessage = None
    isParseError = False
    microsite_id = filename.rsplit('_', 5)[0].upper()    
    logger_id = db.FindMicrositeId(microsite_id)    
    if logger_id is None:
        errorMessage = filename + ": The microsite_id does not exist. Please upload logger data type file first\n"
        return None, errorMessage
    for record in reader:
        parsedRecordDict, isParseError = db.parseLoggerTemp(record)        
        if not isParseError:
            parsedRecords.append(parsedRecordDict)
        else:
            failureCounter += 1
    totalCounter = len(parsedRecords) + failureCounter
    if len(parsedRecords) > 0:
        successCounter = db.insertLoggerTemp(parsedRecords,logger_id)
    failureCounter += len(parsedRecords) - successCounter
    db.close()
    return {"total": totalCounter, "success": successCounter, "failure": failureCounter}, errorMessage

################### Login ######################
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
    return redirect(url_for('query'))

# This function makes sure the server only runs if the script is executed directly
# from the Python interpreter and not used as an imported module.
if __name__ == '__main__':
    app.run()