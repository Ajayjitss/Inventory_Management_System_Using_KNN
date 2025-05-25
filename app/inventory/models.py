from app import db

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    # Relationship with Inventory (This will ensure that when the vendor is deleted, related inventories are deleted)
    inventory_items = db.relationship('Inventory', backref='vendor', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<Vendor {self.name}>'

from datetime import datetime
from sqlalchemy import func

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False)
    
    # Many-to-many relationship with SaleProduct (an inventory item can appear in many sale products)
    sales = db.relationship('SaleProduct', back_populates='inventory', overlaps="sale_products")

    # New fields for tracking updated times and stock levels
    minimum_stock_required = db.Column(db.Integer, nullable=True, default=5)  # Minimum stock threshold for inventory
    last_updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)  # Track when record was last updated
    last_checked_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)  # Track the last time the stock was checked

    def __repr__(self):
        return f'<Inventory {self.name}>'

    # Helper method to check if stock is below the minimum
    def is_below_minimum(self):
        return self.quantity < self.minimum_stock_required
