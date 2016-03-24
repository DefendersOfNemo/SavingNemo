# imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from .forms import QueryForm
from app import app
from app.dbconnect import DbConnect
from flask.ext import excel
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
import io, csv

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
    logger_type_choices = db.getBiomimicTypes()
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
    query["biomimic_type"] = form.get("biomimic_type")[0]
    query["country"] = form.get("country")[0]
    query["state_province"] = form['state_province'][0]
    query["location"] = form['location'][0]
    query["zone"] = form['zone'][0]
    query["sub_zone"] = form['sub_zone'][0]
    query["wave_exp"] = form['wave_exp'][0]        
    query["start_date"] = form['start_date'][0] 
    query["end_date"] = form['end_date'][0]
    print("query")
    print(query)
    session['query'] = query
    db = DbConnect(app.config)
    preview_results = db.getQueryResultsPreview(query)
    db.close()
    return jsonify(list_of_results=preview_results)

@app.route('/download',methods=['GET'])
def download():    
    db = DbConnect(app.config)
    query = session['query']
    header = [("biomimic_type:"+query["biomimic_type"],"country:"+query["country"],"state_province:"+query["state_province"],"location:"+query["location"],"zone:"+query["zone"],"sub_zone:"+query["sub_zone"],"wave_exp:"+query["wave_exp"]),("Timestamp","Temperature")]
    query_results = header  + db.getQueryRawResults(session['query'])
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
        if 'loggerTypeFile' in request.files:
            file = request.files['loggerTypeFile']
            if file:
                if allowed_file("loggerTypeFile", file.filename):
                    stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
                    csv_input = csv.reader(stream)
                    result = AddLoggerType(csv_input)
                else:
                    error = "File should be in csv format"
            else:
                error = "Please choose a File first"
            file.close()        
        elif 'loggerTempFile' in request.files:
            files = request.files.getlist('loggerTempFile')
            if files[0]:
                for file in files:
                    if allowed_file("loggerTempFile", file.filename):
                        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
                        csv_input = csv.reader(stream, delimiter = '\t')
                        print(csv_input)
                        result = AddLoggerTemp(csv_input,file.filename)                  
                    else:
                        error = "File " + file.filename + " should be in csv or txt format"
                    file.close()
            else:
                print("Error! File not selected")
                error = "Please choose a File first"
        else:
            error = "Something went wrong!"
    return render_template('upload.html', result=result, error=error)

def AddLoggerType(reader):
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
            properCounter += 1
        else:
            corruptRecords.append(record)
            corruptCounter += 1
    print(len(properRecords))
    if len(properRecords) > 0:
        print("going to insert")
        ProperCounter, insertCorruptCounter, insertCorruptRecords = db.insertLoggerType(properRecords)
    corruptCounter += insertCorruptCounter
    corruptRecords += insertCorruptRecords
    db.close()
    print("pc: ", properCounter)
    print("cc: ", corruptCounter)
    print("cr: ", corruptRecords)    
    #{"total": 0, "success": 0, "failure": 0, "corruptRecordIds": [], "corruptRecords": []}

def AddLoggerTemp(reader,filename):
    db = DbConnect(app.config)
    properRecords = list();
    corruptRecords = list();
    insertCorruptRecords = list();
    properCounter = 0;
    corruptCounter = 0;
    insertCorruptCounter = 0;
  
    microsite_id = filename.rsplit('_', 5)[0].upper()
    print(microsite_id)
    logger_id = db.FindMicrositeId(microsite_id)
    if logger_id == None:
        print("This microsite id does not exist")
        return

    for record in reader:
        parsedRecordDict,error = db.parseLoggerTemp(record)
        if (not error):
            properRecords.append(parsedRecordDict)
            properCounter += 1
        else:
            corruptRecords.append(record)
            corruptCounter += 1
    if len(properRecords) > 0:
        print("going to insert")
        ProperCounter, insertCorruptCounter, insertCorruptRecords = db.insertLoggerTemp(properRecords,logger_id)
    corruptCounter += insertCorruptCounter
    corruptRecords += insertCorruptRecords
    db.close()
    print("in file:", filename)
    print("pc: ", properCounter)
    print("cc: ", corruptCounter)
    print("cr: ", corruptRecords)    
    return 
    #return  {"total": 0, "success": 0, "failure": 0, "corruptRecordIds": [], "corruptRecords": []}


# This function makes sure the server only runs if the script is executed directly
# from the Python interpreter and not used as an imported module.
if __name__ == '__main__':
    app.run()