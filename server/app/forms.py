""" This script creates fields for the Query Form in Query.html.
    Since most of the fields are dynamic, they are not created here. """

from flask.ext.wtf import Form
from wtforms.fields import SelectField


class QueryForm(Form):
    """Flask Form fields for Query.html"""
    #pylint: disable=too-few-public-methods

    biomimic_type = SelectField(u'biomimic_type', choices=[])
    # Static Choices. These wouldn't change.
    output_type_choices = [('Raw', 'Raw'), ('Min', 'Min'),
                           ('Max', 'Max'), ('Average', 'Average')]
    output_type = SelectField(u'output_type', choices=output_type_choices)
