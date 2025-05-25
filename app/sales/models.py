from app import db
from datetime import datetime

# SaleProduct Model (Intermediary table between Sale and Inventory, represents a specific product in a sale)
class SaleProduct(db.Model):
    __tablename__ = 'sale_product'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product_price = db.Column(db.Numeric(10, 2),  nullable=True)  # Store product price at the time of sale
    
    # Relationships
    sale = db.relationship('Sale', back_populates='sale_products')
    inventory = db.relationship('Inventory', back_populates='sales')  # Add back_populates here to link properly

    def __str__(self):
        return f"{self.quantity} x {self.inventory.name} in sale"

    

# Sale Model (Represents a sale transaction)
class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total_value = db.Column(db.Numeric(10, 2), nullable=False)  # Store total sale value
    
    # Relationship to Customer
    customer = db.relationship('Customer', back_populates='sales')
    
    # One-to-many relationship with SaleProduct (a sale can have multiple SaleProducts)
    sale_products = db.relationship('SaleProduct', back_populates='sale', cascade='all, delete-orphan')

    def __str__(self):
        return f"Sale to {self.customer.name} on {self.date}"

