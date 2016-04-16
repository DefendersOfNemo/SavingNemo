"""
    query.py
    ~~~~~~~~~~~~~~

    This script handles all routes to Query.html.

    :copyright: (c) 2016 by Abhijeet Sharma, Jiayi Wu.
    :license: The MIT License (MIT), see LICENSE for more details.
"""

import datetime
import time
from flask import current_app, Blueprint, request, session, \
     abort, render_template, jsonify
from flask.ext import excel
from jinja2 import TemplateNotFound
from app.forms import QueryForm
from app.dbconnect import DbConnect


#pylint: disable=invalid-name
query_page = Blueprint('query_page', __name__,
                       template_folder='../../client/templates')

@query_page.route('/')
@query_page.route('/query', methods=['GET', 'POST'])
def query():
    """Function for rendering the query form"""
    try:
        error = None
        db_connection = DbConnect(current_app.config)
        biomimic_type_choices = db_connection.fetch_biomimic_types()
        db_connection.close()
        form = QueryForm(request.form)
        form.biomimic_type.choices = biomimic_type_choices
        session['query'] = dict()
        if request.method == 'GET':
            form.process()
        else:
            pass
        return render_template('query.html', title='Query', form=form, error=error)
    except TemplateNotFound:
        abort(404)

@query_page.route('/_parse_data', methods=['GET'])
def parse_data():
    """Function which parses query and fetches preview data from Database"""
    select_type = request.args.get('select_type', 'default')
    select_value = request.args.get('select_value', 'default')
    result, countRecords, minDate, maxDate = queryDb(select_type, select_value)
    return jsonify(result=result, countRecords=countRecords,
                   minDate=minDate, maxDate=maxDate)

def queryDb(value_type, value):
    """Query Database to get options for each drop-down menu"""
    result, countRecords, minDate, maxDate = None, None, None, None
    db_connection = DbConnect(current_app.config)
    keyList = ['biomimic_type', 'country', 'state_province', 'location', 'zone', 'sub_zone', \
                'wave_exp', 'start_date', 'end_date', 'output_type', 'analysis_type']
    # delete all keys in session variable "query" after the selected field
    for key in keyList[keyList.index(value_type) + 1:]:
        session['query'].pop(key, None)
    session['query'][value_type] = value
    if value_type == "biomimic_type":
        result, countRecords, minDate, maxDate = \
              db_connection.fetch_distinct_countries_and_zones(session['query'])
    elif value_type == "country":
        result, countRecords, minDate, maxDate = \
                        db_connection.fetch_distinct_states(session['query'])
    elif value_type == "state_province":
        result, countRecords, minDate, maxDate = \
                        db_connection.fetch_distinct_locations(session['query'])
    elif value_type == "location":
        # location field doesn't have any associated dynamic behavior
        # except for fetching metadata.
        countRecords, minDate, maxDate = \
                        db_connection.fetch_metadata(session['query'])
    elif value_type == "zone":
        result, countRecords, minDate, maxDate = \
                        db_connection.fetch_distinct_sub_zones(session['query'])
    elif value_type == "sub_zone":
        result, countRecords, minDate, maxDate = \
                   db_connection.fetch_distinct_wave_exposures(session['query'])
    db_connection.close()
    return result, countRecords, minDate, maxDate

@query_page.route('/_submit_query', methods=['GET'])
def submit_query():
    '''get values of form and query Database to get preview results'''
    form = dict(request.args)
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
        query["start_date"] = str(datetime.datetime
                                  .strptime(form['start_date'][0], '%m/%d/%Y')
                                  .date())
        query["end_date"] = str(datetime.datetime
                                .strptime(form['end_date'][0], '%m/%d/%Y')
                                .date())
    session['query'] = query
    db_connection = DbConnect(current_app.config)
    preview_results, db_query = db_connection.get_query_results_preview(query)
    session['db_query'] = db_query
    db_connection.close()
    return jsonify(list_of_results=preview_results)

@query_page.route('/download', methods=['GET'])
def download():
    """ Create file in csv format and downloaded to user's computer"""
    db_connection = DbConnect(current_app.config)
    query = session['query']
    time_title = ''
    if query.get("analysis_type") == "Daily":
        time_title = "Date"
    elif query.get("analysis_type") == "Monthly":
        time_title = "Month, Year"
    elif query.get("analysis_type") == "Yearly":
        time_title = "Year"
    else:
        time_title = "Timestamp"
    header = [[key + ":" + str(value) for key, value in query.items()],
              (time_title, "Temperature")]
    query_results = header + db_connection.get_query_raw_results(session['db_query'])
    db_connection.close()
    return excel.make_response_from_array(query_results, "csv",
                                          file_name="export_data")
