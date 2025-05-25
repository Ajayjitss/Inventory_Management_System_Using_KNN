from app import db

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    sales = db.relationship('Sale', back_populates='customer')

    # Relationship with Inventory (This will ensure that when the customers is deleted, related inventories are deleted)
    # inventory_items = db.relationship('Inventory', backref='customers', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<Customer {self.name}>'
