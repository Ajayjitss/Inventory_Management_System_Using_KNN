from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from .models import Vendor, Inventory
from .forms import InventoryForm
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from .models import Vendor
from .forms import VendorForm
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify
from .utils import update_inventory_predictions

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory_list')
@login_required
def inventory_list():
    inventory_items = Inventory.query.all()
    return render_template('inventory/inventory_list.html', inventory_items=inventory_items)

@inventory_bp.route('/inventory_create', methods=['GET', 'POST'])
@login_required
def inventory_create():
    form = InventoryForm()
    if form.validate_on_submit():
        vendor = Vendor.query.get(form.vendor.data)  # Retrieve the Vendor object by its ID
        if vendor:
            new_inventory = Inventory(
                name=form.name.data,
                quantity=form.quantity.data,
                price=form.price.data,
                vendor=vendor  # Use the full vendor object here
            )
            db.session.add(new_inventory)
            db.session.commit()
            flash('Inventory item created successfully!', 'success')
            return redirect(url_for('inventory.inventory_list'))
        else:
            flash("Selected vendor doesn't exist.", 'danger')
            return redirect(url_for('inventory.inventory_create'))
    return render_template('inventory/inventory_form.html', form=form)

# Update Inventory Route
@inventory_bp.route('/inventory_update/<int:pk>', methods=['GET', 'POST'])
@login_required
def inventory_update(pk):
    inventory_item = Inventory.query.get_or_404(pk)  # Fetch inventory item by primary key
    form = InventoryForm(obj=inventory_item)  # Populate form with the existing item details

    if form.validate_on_submit():
        vendor = Vendor.query.get(form.vendor.data)
        inventory_item.name = form.name.data
        inventory_item.quantity = form.quantity.data
        inventory_item.price = form.price.data
        inventory_item.vendor_id = vendor.id  # Update vendor if it's selected
        
        db.session.commit()
        flash('Inventory item updated successfully!', 'success')
        return redirect(url_for('inventory.inventory_list'))

    return render_template('inventory/inventory_form.html', form=form, inventory_item=inventory_item)

# Delete Inventory Route
@inventory_bp.route('/inventory_delete/<int:pk>', methods=['POST'])
@login_required
def inventory_delete(pk):
    inventory_item = Inventory.query.get_or_404(pk)
    
    try:
        db.session.delete(inventory_item)
        db.session.commit()
        flash('Inventory item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting inventory item: {str(e)}', 'danger')
    
    return redirect(url_for('inventory.inventory_list'))

@inventory_bp.route('/vendor_list')
@login_required
def vendor_list():
    vendors = Vendor.query.all()
    return render_template('vendor/vendor_list.html', vendors=vendors)

@inventory_bp.route('/vendor_create', methods=['GET', 'POST'])
@login_required
def vendor_create():
    form = VendorForm()
    try:
        if form.validate_on_submit():
            new_vendor = Vendor(
                name=form.name.data,
                contact_info=form.contact_info.data,
                address=form.address.data,
                phone_number=form.phone_number.data,
                email=form.email.data
            )
            db.session.add(new_vendor)
            db.session.commit()
            flash('Vendor created successfully!', 'success')
            return redirect(url_for('inventory.vendor_list'))
    except IntegrityError as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"Error: {str(e.orig)}", 'danger')  # Flash specific database error message
    except Exception as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"An unexpected error occurred: {str(e)}", 'danger')  # Flash unexpected error message

    return render_template('vendor/vendor_form.html', form=form)

# Update Vendor Route
@inventory_bp.route('/vendor_update/<int:pk>', methods=['GET', 'POST'])
@login_required
def vendor_update(pk):
    vendor = Vendor.query.get_or_404(pk)  # Fetch vendor by primary key
    form = VendorForm(obj=vendor)  # Bind the form to the vendor instance

    if form.validate_on_submit():
        vendor.name = form.name.data
        vendor.contact_info = form.contact_info.data
        vendor.address = form.address.data
        vendor.phone_number = form.phone_number.data
        vendor.email = form.email.data

        db.session.commit()
        flash('Vendor updated successfully!', 'success')
        return redirect(url_for('inventory.vendor_list'))

    return render_template('vendor/vendor_form.html', form=form, vendor=vendor)

# Delete Vendor Route
@inventory_bp.route('/vendor_delete/<int:pk>', methods=['GET', 'POST'])
@login_required
def vendor_delete(pk):
    # Fetch the vendor by primary key
    vendor = Vendor.query.get_or_404(pk)
    form = VendorForm()
    
    # If the form is submitted (POST)
    if request.method == 'POST':
        try:
            db.session.delete(vendor)
            db.session.commit()  # Commit the transaction
            flash('Vendor deleted successfully!', 'success')
            print('Vendor deleted successfully!')
            return redirect(url_for('inventory.vendor_list'))  # Redirect to the vendor list page
        except IntegrityError as e:
            db.session.rollback()  # Rollback if there is an error
            flash(f"Error deleting vendor: {str(e.orig)}", 'danger')
            print(f"Error deleting vendor: {str(e.orig)}")
            return redirect(url_for('inventory.vendor_list'))  # Return to vendor list if error occurs
        except Exception as e:
            db.session.rollback()  # Rollback if there is any other unexpected error
            flash(f"An unexpected error occurred: {str(e)}", 'danger')
            print(f"An unexpected error occurred: {str(e)}")
            return redirect(url_for('inventory.vendor_list'))  # Return to vendor list in case of unexpected errors
    
    # If the method is GET, just display the delete confirmation page
    return render_template('vendor/vendor_delete.html', form=form, vendor=vendor)

@inventory_bp.route('/stock_status', methods=['GET'])
def stock_status():
    # Get the sort_by and order parameters from the query string, default to 'id' and 'asc'
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    # Define the valid columns for sorting
    valid_columns = ['id', 'quantity', 'minimum_stock_required', 'last_checked_at']
    
    # If the requested sort_by column is invalid, default to 'id'
    if sort_by not in valid_columns:
        sort_by = 'id'
    
    # Ensure order is either 'asc' or 'desc'
    if order not in ['asc', 'desc']:
        order = 'asc'

    # Fetch the inventory data from the database, ordered by the selected column and direction
    if order == 'asc':
        order_direction = getattr(Inventory, sort_by).asc()
    else:
        order_direction = getattr(Inventory, sort_by).desc()
    # update_inventory_predictions()
    inventory_items = Inventory.query.with_entities(
        Inventory.id,
        Inventory.name,
        Inventory.quantity,
        Inventory.minimum_stock_required,
        Inventory.last_checked_at
    ).order_by(order_direction).all()  # Dynamically use the sort_by column and order direction

    return render_template('inventory/stock_status.html', inventory_items=inventory_items, sort_by=sort_by, order=order)

@inventory_bp.route('update_inventory_predictions', methods=['GET'])
def run_inventory_update():
    try:
        # Log that the API call has been received
        print('API request to update inventory predictions received.')

        # Run the update function
        update_inventory_predictions()

        # Log success
        print('Inventory update successful.')

        # Return a success response
        return jsonify({"message": "Inventory predictions updated successfully!"}), 200
    except Exception as e:
        # Log any error
        print(f"Error occurred during inventory update: {str(e)}")
        return jsonify({"message": "Failed to update inventory predictions", "error": str(e)}), 500
    

