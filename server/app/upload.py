"""
    upload.py
    ~~~~~~~~~~~~~~

    This script handles the upload functionality in upload.html

    :copyright: (c) 2016 by Abhijeet Sharma.
    :license: The MIT License (MIT), see LICENSE for more details.
"""

import time
import io
import csv
from flask import current_app, Blueprint, request, session, redirect, url_for, \
                  abort, render_template
from app.dbconnect import DbConnect


#pylint: disable=invalid-name
upload_page = Blueprint('upload_page', __name__,
                        template_folder='../../client/templates')
ALLOWED_EXTENSIONS_LOGGER_TYPE = set(['csv'])
ALLOWED_EXTENSIONS_LOGGER_TEMP = set(['csv', 'txt'])

def allowed_file(filetype, filename):
    '''check whether uploaded file is in correct format'''
    if filetype == "loggerTypeFile":
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_LOGGER_TYPE
    else:
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_LOGGER_TEMP

@upload_page.route('/upload', methods=['GET', 'POST'])
def upload():
    '''Handle user upload functions, including logger type and logger temperature file'''
    try:
        # Interceptor for Upload
        if session.get('logged_in') is None:
            return redirect(url_for('query_page.query'))
        error = ""
        all_results = None
        if request.method == 'POST':
            if 'loggerTypeFile' in request.files:
                all_results, error = upload_logger_type(request.files['loggerTypeFile'])
            elif 'loggerTempFile' in request.files:
                all_results, error = upload_logger_temp(request.files.getlist('loggerTempFile'))
            if all_results is not None:
                if all_results.get('total') == 0:
                    all_results = None
        return render_template('upload.html', result=all_results, error=error)
    #pylint: disable=bare-except
    except:
        abort(404)

def upload_logger_type(file):
    """Helper function for uploading new logger type"""
    error = ""
    all_results = {'total': 0, 'success': 0, 'failure': 0, 'time_taken': 0}
    start_time = time.time()
    if file:
        if allowed_file("loggerTypeFile", file.filename):
            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
            csv_input = csv.reader(stream)
            next(csv_input, None)  # skip the headers
            all_results, error = add_logger_type(csv_input)
        else:
            error = "File {0} should be in csv format\n".format(file.filename)
    else:
        error = "Please choose a file first"
    file.close()
    end_time = time.time()
    all_results['time_taken'] = round(end_time - start_time, 2)
    return all_results, error

def upload_logger_temp(files):
    """Helper function for uploading new logger temperature"""
    error = ""
    all_results = {'total': 0, 'success': 0, 'failure': 0, 'time_taken': 0}
    start_time = time.time()
    if files[0]:
        for file in files:
            individual_result = None
            if allowed_file("loggerTempFile", file.filename):
                stream = io.StringIO(file.stream.read()
                                     .decode("UTF-8"), newline=None)
                if file.filename.rsplit('.', 1)[1] == 'txt':
                    csv_input = csv.reader(stream, delimiter='\t')
                else:
                    csv_input = csv.reader(stream)
                # skip the header
                next(csv_input, None)
                individual_result, error_message = \
                                        add_logger_temp(csv_input, file.filename)
                if individual_result is not None:
                    all_results['total'] += individual_result['total']
                    all_results['success'] += individual_result['success']
                    all_results['failure'] += individual_result['failure']
                if error_message is not None:
                    error += error_message
            else:
                error += "File {0} should be in csv or txt format\n".format(file.filename)
            file.close()
    else:
        error = "Please choose a file first\n"
    end_time = time.time()
    all_results['time_taken'] = round(end_time - start_time, 2)
    return all_results, error

def add_logger_type(reader):
    """Insert logger type in file"""
    db = DbConnect(current_app.config)
    parsed_records = list()
    total_counter = 0
    success_counter = 0
    failure_counter = 0
    error_message = None
    is_parse_error = False
    for record in reader:
        parsed_record_dict, is_parse_error = db.parse_logger_type(record)
        if not is_parse_error:
            parsed_records.append(parsed_record_dict)
        else:
            failure_counter += 1
    total_counter = len(parsed_records) + failure_counter
    if len(parsed_records) > 0:
        success_counter = db.insert_logger_type(parsed_records)
    failure_counter += len(parsed_records) - success_counter
    db.close()
    return  {"total": total_counter, "success": success_counter,
             "failure": failure_counter}, error_message

def add_logger_temp(reader, filename):
    '''Insert logger temperatures in uploaded file'''
    db = DbConnect(current_app.config)
    parsed_records = list()
    total_counter = 0
    success_counter = 0
    failure_counter = 0
    error_message = None
    is_parse_error = False
    microsite_id = filename.rsplit('_', 5)[0].upper()
    logger_id = db.find_microsite_id(microsite_id)
    if logger_id is None:
        error_message = filename + ": The microsite_id does not exist. \
                                    Please upload logger data type file first\n"
        return None, error_message
    for record in reader:
        parsed_record_dict, is_parse_error = db.parse_logger_temp(record)
        if not is_parse_error:
            parsed_records.append(parsed_record_dict)
        else:
            failure_counter += 1
    total_counter = len(parsed_records) + failure_counter
    if len(parsed_records) > 0:
        success_counter = db.insert_logger_temp(parsed_records, logger_id)
    failure_counter += len(parsed_records) - success_counter
    db.close()
    return {"total": total_counter, "success": success_counter,
            "failure": failure_counter}, error_message
