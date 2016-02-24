from flask.ext.wtf import Form
from wtforms.fields import SelectField
from wtforms import validators
from wtforms import DateField
# Query Form class
class QueryForm(Form):
    logger_type = SelectField(u'logger_type', choices=[(None, 'Enter Logger Type')], \
                   validators=[validators.required()])
    country_name = SelectField(u'country_name', choices=[(None, 'Enter Country Name')], \
                   validators=[validators.required()])
    state_name = SelectField(u'state_name')
    location_name = SelectField(u'location_name') 
    zone_name = SelectField(u'zone_name')
    sub_zone_name = SelectField(u'sub_zone')
    date_pick_from = DateField('date_pick_from', format='%m/%d/%Y')
    date_pick_to = DateField('date_pick_to', format='%m/%d/%Y')
    # Static Choices. These wouldn't change.
    measurement_interval_choices = [('Daily', 'Daily'), ('Monthly', 'Monthly'), \
                                    ('Yearly', 'Yearly')]
    measurement_interval = SelectField(u'measurement_interval', \
                            choices=measurement_interval_choices)
    analysis_type_choices = [('Min_Max', 'Max/Min Only'), ('Mean', 'Mean'), \
                             ('Median', 'Median')]
    analysis_type = SelectField(u'analysis_type', \
                    choices=analysis_type_choices)