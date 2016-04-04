# imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from .forms import QueryForm
from app import app
from app.dbconnect import DbConnect
from flask.ext import excel
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
import io, csv, datetime, sys

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
    return redirect(url_for('query'))

@app.route('/query', methods=['GET', 'POST'])
def query():
    error = None
    results = None
    db = DbConnect(app.config)
    biomimic_type_choices = db.getBiomimicTypes()
    db.close()

    form = QueryForm(request.form)
    form.biomimic_type.choices = biomimic_type_choices


    if request.method == 'GET':
        form.process()
    else:   
        pass
    return render_template('query.html', title='Query', form=form, error=error)

@app.route('/_submit_query', methods=['GET'])
def submit_query():
    '''get values of form and query Database to get preview results'''
    form  = dict(request.args)
    query = {}
    query["biomimic_type"] = form.get("biomimic_type")[0]
    query["country"] = form.get("country")[0]
    query["state_province"] = form['state_province'][0]
    query["location"] = form['location'][0]
    query["zone"] = form['zone'][0]
    query["sub_zone"] = form['sub_zone'][0]
    query["wave_exp"] = form['wave_exp'][0]        
    query["start_date"] = str(datetime.datetime.strptime(form['start_date'][0],'%m/%d/%Y').date())
    query["end_date"] = str(datetime.datetime.strptime(form['end_date'][0],'%m/%d/%Y').date())
    query["output_type"] = form['output_type'][0]
    if form.get('analysis_type') is not None:
        query["analysis_type"] = form['analysis_type'][0]        
    session['query'] = query
    print("query: ", query)
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

@app.route('/_parse_data', methods=['GET'])
def parse_data():
    select_type = request.args.get('select_type', 'default')
    select_value = request.args.get('select_value', 'default')
    result = queryDb(select_type, select_value)
    return jsonify(result)

def queryDb(query_type, query_value):
    '''Query Database to get options for each drop-down menu'''
    result = None
    db = DbConnect(app.config)
    if query_type == "biomimic_type": 
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
    result = None;
    error= None;
    if request.method == 'POST':
        if 'loggerTypeFile' in request.files:
            file = request.files['loggerTypeFile']
            if file:
                if allowed_file("loggerTypeFile", file.filename):
                    stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
                    csv_input = csv.reader(stream)
                    next(csv_input, None)  # skip the headers
                    result, corruptRecords = AddLoggerType(csv_input)
                else:
                    error = "File should be in csv format"
            else:
                error = "Please choose a file first"
            file.close()        
        elif 'loggerTempFile' in request.files:
            files = request.files.getlist('loggerTempFile')
            if files[0]:
                result = {'total':0, 'success':0, 'failure':0};
                for file in files:
                    individual_result = None;
                    if allowed_file("loggerTempFile", file.filename):
                        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
                        if file.filename.rsplit('.', 1)[1] == 'txt':
                            csv_input = csv.reader(stream, delimiter = '\t')
                        else:
                            csv_input = csv.reader(stream)
                        next(csv_input, None)  # skip the headers                            
                        individual_result, corruptRecords, error_1 = AddLoggerTemp(csv_input,file.filename)
                        if individual_result is not None:
                            result['total'] += individual_result['total']
                            result['success'] += individual_result['success']
                            result['failure'] += individual_result['failure']
                            corruptRecords += file.filename + ':\n' + corruptRecords
                    else:
                        error_1 = "File " + file.filename + " should be in csv or txt format"
                    file.close()
                    if error == None:
                        error = error_1
                    elif error_1 != None:
                        error += error_1
            else:
                error = "Please choose a file first"
    if result is not None:
        if result.get('total') == 0:
            result = None
    return render_template('upload.html', result=result, error=error)

def AddLoggerType(reader):
    '''Insert logger type in file'''
    db = DbConnect(app.config)
    properRecords = list();
    corruptRecords = '';
    insertCorruptRecords = '';
    properCounter = 0;
    corruptCounter = 0;
    insertCorruptCounter = 0;
    count = 0
    for record in reader:
        parsedRecordDict, error = db.parseLoggerType(record, count)
        if (error == ''):
            properRecords.append(parsedRecordDict)
        else:
            corruptRecords += str(count) + ',' + error + ';'
            corruptCounter += 1
        count += 1
    if len(properRecords) > 0:
        properCounter, insertCorruptCounter, insertCorruptRecords = db.insertLoggerType(properRecords)
    corruptCounter += insertCorruptCounter
    corruptRecords += insertCorruptRecords
    db.close()   
    return {"total": properCounter + corruptCounter, "success": properCounter, "failure": corruptCounter}, corruptRecords

def AddLoggerTemp(reader,filename):
    '''Insert logger temperatures in uploaded file'''
    db = DbConnect(app.config)
    properRecords = list();
    corruptRecords = '';
    insertCorruptRecords = '';
    properCounter = 0;
    corruptCounter = 0;
    insertCorruptCounter = 0;
    errorMessage = ''
    error = ''
    microsite_id = filename.rsplit('_', 5)[0].upper()
    logger_id = db.FindMicrositeId(microsite_id)
    if logger_id == None:
        errorMessage = filename + ": The microsite_id dose not exist. Please upload logger data file first"+'\n'
        return None, None, errorMessage
    count = 0
    for record in reader:
        parsedRecordDict,error = db.parseLoggerTemp(record, count)
        if (error == ''):
            properRecords.append(parsedRecordDict)
            properCounter += 1
        else:
            corruptRecords = corruptRecords + str(count) + ',' + error + ';'
            corruptCounter += 1
        count+=1
    if len(properRecords) > 0:
        properCounter, insertCorruptCounter, insertCorruptRecords = db.insertLoggerTemp(properRecords,logger_id)
    corruptCounter += insertCorruptCounter
    corruptRecords += insertCorruptRecords
    db.close()
    return {"total": properCounter + corruptCounter, "success": properCounter, "failure": corruptCounter}, corruptRecords, None

# This function makes sure the server only runs if the script is executed directly
# from the Python interpreter and not used as an imported module.
if __name__ == '__main__':
    app.run()