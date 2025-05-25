from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange
from .models import Vendor
from flask_sqlalchemy import SQLAlchemy

from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired

class InventoryForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    vendor = SelectField('Vendor', coerce=int, validators=[DataRequired()])  # Ensure vendor is a SelectField and coerce to int

    def __init__(self, *args, **kwargs):
        super(InventoryForm, self).__init__(*args, **kwargs)
        # Populate the vendor field with all available vendors
        self.vendor.choices = [(vendor.id, vendor.name) for vendor in Vendor.query.all()]

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, EmailField
from wtforms.validators import DataRequired, Email

class VendorForm(FlaskForm):
    name = StringField('Vendor Name', validators=[DataRequired()])
    contact_info = TextAreaField('Contact Info', validators=[DataRequired()])
    address = StringField('Address')
    phone_number = StringField('Phone Number')
    email = EmailField('Email', validators=[Email()])

    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
