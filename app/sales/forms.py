from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DecimalField, FieldList, FormField
from wtforms.validators import DataRequired
from app.inventory.models import Inventory
from app.customer.models import Customer

class SaleProductForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired()])
    product_price = DecimalField('Product Price', places=2, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(SaleProductForm, self).__init__(*args, **kwargs)
        # Populate the product dropdown with all inventory products
        self.product_id.choices = [(product.id, f"{product.name}", product.price) for product in Inventory.query.all()]

class SaleForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    products = FieldList(FormField(SaleProductForm), min_entries=1)

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        # Populate the customer dropdown with all customers
        self.customer_id.choices = [(customer.id, customer.name) for customer in Customer.query.all()]
