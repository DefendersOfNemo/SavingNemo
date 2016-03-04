from flask.ext.wtf import Form
from wtforms.fields import SelectField
from wtforms import validators
from wtforms import DateField
# Query Form class
class QueryForm(Form):
    logger_type = SelectField(u'logger_type', choices=[])
    country_name = SelectField(u'country_name', choices=[])
    state_name = SelectField(u'state_name', choices=[])
    location_name = SelectField(u'location_name', choices=[]) 
    zone_name = SelectField(u'zone_name', choices=[])
    sub_zone_name = SelectField(u'sub_zone', choices=[])
    wave_exp_name = SelectField(u'wave_exp', choices=[])
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