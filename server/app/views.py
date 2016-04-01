# imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from .forms import QueryForm
from app import app
from app.dbconnect import DbConnect
from flask.ext import excel
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
import io, csv, datetime, os, sys

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../upload/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    print("form: ", form)
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
    if form['analysis_type'][0] != "":
        query["analysis_type"] = form['analysis_type'][0]        
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
    elif query.get("analysis_type") == "Weekly":
        time_title = "Week No"
    elif query.get("analysis_type") == "Monthly":
        time_title = "Month"
    elif query.get("analysis_type") == "Yearly":
        time_title = "Year" 
    elif query.get("analysis_type") == '':
        time_title = "Timestamp"

    header = [("biomimic_type:" + query["biomimic_type"], \
                "country:" + query["country"], \
                "state_province:" + query["state_province"], \
                "location:" + query["location"], \
                "zone:" + query["zone"], \
                "sub_zone:" + query["sub_zone"], \
                "wave_exp:" + query["wave_exp"], \
                "output_type:" + query["output_type"], \
                "analysis_type:" + query.get("analysis_type")), \
            (time_title,"Temperature")]
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
    error=None;
    if request.method == 'POST':
        print(request.form)
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
                        individual_result, corruptRecords, error = AddLoggerTemp(csv_input,file.filename)
                        if individual_result is not None:
                            result['total'] += individual_result['total']
                            result['success'] += individual_result['success']
                            result['failure'] += individual_result['failure']
                    else:
                        error = "File " + file.filename + " should be in csv or txt format"
                    file.close()
            else:
                error = "Please choose a file first"
    if result is not None:
        if result.get('total') == 0:
            result = None
        else:
            with open(os.path.join(app.config['UPLOAD_FOLDER']+"upload_result.csv"),"w") as csvfile:
                fieldnames = ['total', 'success','failure','corruptRecords']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'total': result['total'], 'success':result['success'],'failure':result['failure']})
                if corruptRecords is not None:
                    for record in corruptRecords:
                        writer.writerow({'corruptRecords':record})

    if 'download' in request.form:
        result=[]
        with open(os.path.join(app.config['UPLOAD_FOLDER']+"upload_result.csv"),"r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                result.append(row)
        return excel.make_response_from_array(result, "csv", file_name="upload_temperature_file_results")

    return render_template('upload.html', result=result, error=error)

def AddLoggerType(reader):
    '''Insert logger type in file'''
    db = DbConnect(app.config)
    properRecords = list();
    corruptRecords = list();
    insertCorruptRecords = list();
    properCounter = 0;
    corruptCounter = 0;
    insertCorruptCounter = 0;
    for record in reader:
        parsedRecordDict, error = db.parseLoggerType(record)
        if (not error):
            properRecords.append(parsedRecordDict)
        else:
            corruptRecords.append(record)
            corruptCounter += 1
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
    corruptRecords = list();
    insertCorruptRecords = list();
    properCounter = 0;
    corruptCounter = 0;
    insertCorruptCounter = 0;
    error = None
    microsite_id = filename.rsplit('_', 5)[0].upper()
    logger_id = db.FindMicrositeId(microsite_id)
    if logger_id == None:
        error = "The microsite_id dose not exist. Please upload logger data file first"
        return None, None, error
    for record in reader:
        parsedRecordDict,error = db.parseLoggerTemp(record)
        if (not error):
            properRecords.append(parsedRecordDict)
            properCounter += 1
        else:
            corruptRecords.append(record)
            corruptCounter += 1
    if len(properRecords) > 0:
        properCounter, insertCorruptCounter, insertCorruptRecords = db.insertLoggerTemp(properRecords,logger_id)
    corruptCounter += insertCorruptCounter
    corruptRecords += insertCorruptRecords

    db.close()
    return {"total": properCounter + corruptCounter, "success": properCounter, "failure": corruptCounter}, corruptRecords, error

# This function makes sure the server only runs if the script is executed directly
# from the Python interpreter and not used as an imported module.
if __name__ == '__main__':
    app.run()