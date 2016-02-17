from flask.ext.wtf import Form
from wtforms.fields import SelectField

# Query Form class
class QueryForm(Form):
    logger_type = SelectField(u'logger_type', choices=[])
    country_name = SelectField(u'country_name', choices=[])
    state_name = SelectField(u'state_name', choices=[])
    location_name = SelectField(u'location_name', choices=[]) 
    zone_name = SelectField(u'zone_name', choices=[])
    sub_zone_name = SelectField(u'sub_zone', choices=[])
    # Static Choices. These wouldn't change.
    measurement_interval_choices = [('daily', 'daily'), ('monthly', 'monthly'), \
                                    ('yearly', 'yearly')]
    analysis_type_choices = [('min_max', 'Max/Min Only'), ('mean', 'Mean'), \
                             ('median', 'Median')]
    measurement_interval = SelectField(u'measurement_interval', \
                            choices=measurement_interval_choices)
    
    analysis_type = SelectField(u'analysis_type', \
                    choices=analysis_type_choices)