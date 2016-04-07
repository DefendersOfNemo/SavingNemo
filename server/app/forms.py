from flask.ext.wtf import Form
from wtforms.fields import SelectField
from wtforms import validators
from wtforms import DateField
# Query Form class
class QueryForm(Form):
    biomimic_type = SelectField(u'biomimic_type', choices=[])
    country_name = SelectField(u'country_name', choices=[])
    state_name = SelectField(u'state_name', choices=[])
    location_name = SelectField(u'location_name', choices=[]) 
    zone_name = SelectField(u'zone_name', choices=[])
    sub_zone_name = SelectField(u'sub_zone', choices=[])
    wave_exp_name = SelectField(u'wave_exp', choices=[])
    #date_pick_from = DateField('date_pick_from', format='%m/%d/%Y')
    #date_pick_to = DateField('date_pick_to', format='%m/%d/%Y')
    # Static Choices. These wouldn't change.
    output_type_choices = [('Raw', 'Raw'), ('Min', 'Min'), ('Max', 'Max'), ('Average', 'Average')]
    output_type = SelectField(u'output_type', choices=output_type_choices)
    analysis_type = SelectField(u'analysis_type', choices=[])
    
