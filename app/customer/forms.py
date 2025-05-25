from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

class CustomerForm(FlaskForm):
    # Fields for customer information
    name = StringField('Name', validators=[DataRequired()])
    contact_info = StringField('Contact Info', validators=[DataRequired()])
    address = StringField('Address', validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    email = StringField('Email', validators=[Email(), Optional()])
    
    submit = SubmitField('Save')
