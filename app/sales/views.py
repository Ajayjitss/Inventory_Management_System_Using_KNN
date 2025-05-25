from flask import render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_required
from app import db
from .models import Sale, SaleProduct
from app.customer.models import Customer  # Ensure this import is here
from app.inventory.models import Inventory  # Ensure this import is here
from .forms import SaleForm, SaleProductForm  # Create a form for Sale
from sqlalchemy.exc import IntegrityError
from flask import Blueprint
import pdfkit
from flask import make_response
from sqlalchemy.exc import IntegrityError
from app import db
from decimal import Decimal

sales_bp = Blueprint('sales', __name__)

# View Sales Route
@sales_bp.route('/sale_list')
@login_required
def sale_list():
    sales = Sale.query.all()  # Get all sales
    return render_template('sales/sale_list.html', sales=sales)

@sales_bp.route('/sale_create', methods=['GET', 'POST'])
@login_required
def sale_create():
    if request.method == 'GET':
        # Handle GET request to render the template
        form = SaleForm()

        return render_template('sales/sale_form.html', form=form)

    if request.method == 'POST':
        # Handle POST request to create a sale
        try:
            # Parse JSON payload
            data = request.get_json()

            # Validate required fields
            if not data.get('customer_id') or not data.get('products'):
                return jsonify({'success': False, 'message': 'Missing required data'}), 400

            # Fetch the customer from the database
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({'success': False, 'message': 'Invalid customer'}), 400

            # Initialize total value
            total_value = 0

            # Create Sale entry
            new_sale = Sale(customer=customer, total_value=total_value)
            db.session.add(new_sale)
            db.session.commit()

            # Add products to the sale
            for product in data['products']:
                product_id = product['product_id']
                quantity = int(product['quantity'])  # Convert quantity to int
                product_price = float(product['product_price'])  # Convert product_price to float

                inventory_item = Inventory.query.get(product_id)

                if not inventory_item:
                    return jsonify({'success': False, 'message': f'Invalid product ID {product_id}'}), 400

                # Check if enough stock is available
                if inventory_item.quantity < quantity:
                    return jsonify({'success': False, 'message': f'Not enough stock for product ID {product_id}'}), 400

                # Create SaleProduct entry
                sale_product = SaleProduct(
                    sale_id=new_sale.id,
                    inventory_id=inventory_item.id,
                    quantity=quantity,
                    product_price=product_price
                )
                db.session.add(sale_product)

                # Update the inventory quantity
                inventory_item.quantity -= quantity  # Reduce quantity by the sold amount
                db.session.commit()  # Commit to update inventory

                # Calculate the total sale value
                total_value += product_price * quantity

            # Update Sale with total value
            new_sale.total_value = total_value
            db.session.commit()

            return jsonify({'success': True, 'message': 'Sale created successfully!'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@sales_bp.route('/sale_update/<int:pk>', methods=['GET', 'POST'])
@login_required
def sale_update(pk):
    if request.method == 'GET':
        # Handle GET request to render the update form (template)
        sale = Sale.query.get_or_404(pk)
        form = SaleForm(obj=sale)

        # Fetch the associated sale products
        sale_products = []
        for sale_product in sale.sale_products:
            sale_products.append({
                'product_id': sale_product.inventory.id,
                'product_name': sale_product.inventory.name,
                'quantity': sale_product.quantity,
                'product_price': sale_product.product_price
            })

        return render_template('sales/sale_update_form.html', form=form, sale=sale, sale_products=sale_products)

    if request.method == 'POST':
        try:
            # Parse the incoming JSON request
            data = request.get_json()

            # Validate required fields
            if not data.get('customer_id') or not data.get('products'):
                return jsonify({'success': False, 'message': 'Missing required data'}), 400

            # Fetch the customer from the database
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({'success': False, 'message': 'Invalid customer'}), 400

            # Fetch the sale object from the database
            sale = Sale.query.get_or_404(pk)
            total_value = 0

            # Clear existing products for this sale
            for existing_product in sale.sale_products:
                # Increase the inventory quantity back by the old sold quantity
                inventory_item = existing_product.inventory
                inventory_item.quantity += existing_product.quantity
                db.session.delete(existing_product)  # Remove the old SaleProduct
            db.session.commit()

            # Add new products to the sale
            for product in data['products']:
                product_id = product['product_id']
                quantity = int(product['quantity'])  # Ensure this is an integer
                product_price = float(product['product_price'])  # Ensure this is a float
                
                # Get the inventory item (product)
                inventory_item = Inventory.query.get(product_id)
                if not inventory_item:
                    return jsonify({'success': False, 'message': f'Invalid product ID {product_id}'}), 400

                # Check if enough stock is available
                if inventory_item.quantity < quantity:
                    return jsonify({'success': False, 'message': f'Not enough stock for product "{inventory_item.name}"'}), 400

                # Create new SaleProduct entry
                sale_product = SaleProduct(
                    sale_id=sale.id,
                    inventory_id=inventory_item.id,
                    quantity=quantity,
                    product_price=product_price
                )
                db.session.add(sale_product)

                # Update the inventory quantity
                inventory_item.quantity -= quantity  # Reduce quantity by the sold amount
                db.session.commit()  # Commit to update inventory

                # Update the total sale value
                total_value += product_price * quantity

            # Update sale total value
            sale.total_value = total_value
            sale.customer = customer
            db.session.commit()

            return jsonify({'success': True, 'message': 'Sale updated successfully!'}), 200

        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Delete Sale Route
@sales_bp.route('/sale_delete/<int:pk>', methods=['GET', 'POST'])
@login_required
def sale_delete(pk):
    sale = Sale.query.get_or_404(pk)
    if request.method == 'POST':
        try:
            db.session.delete(sale)
            db.session.commit()
            flash('Sale deleted successfully!', 'success')
            return redirect(url_for('sales.sale_list'))
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Error deleting sale: {str(e.orig)}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')
    return render_template('sales/sale_delete.html', sale=sale)




@sales_bp.route('/sale_view/<int:sale_id>')
@login_required
def sale_view(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    tax = sale.total_value * Decimal('0.10')   # Decimal * Decimal
    grand_total = sale.total_value + tax
    return render_template('sales/sale_view.html', sale=sale, tax=tax, grand_total=grand_total)


@sales_bp.route('/generate_invoice/<int:sale_id>')
@login_required
def generate_invoice(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    tax = sale.total_value * Decimal('0.10')  # Use Decimal for the multiplier
    grand_total = sale.total_value + tax
    
    html = render_template('sales/invoice_template.html',
                         sale=sale,
                         tax=tax,
                         grand_total=grand_total)

    
    # Configure pdfkit to point to your wkhtmltopdf binary
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
    }
    
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=invoice_{sale.id}.pdf'
    
    return response