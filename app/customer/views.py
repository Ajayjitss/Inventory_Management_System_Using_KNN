from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from .models import Customer
from .forms import CustomerForm
from sqlalchemy.exc import IntegrityError
from flask import Blueprint

customer_bp = Blueprint('customer', __name__)

# Customer List Route
@customer_bp.route('/customer_list')
@login_required
def customer_list():
    customers = Customer.query.all()
    return render_template('customer/customer_list.html', customers=customers)

# Create Customer Route
@customer_bp.route('/customer_create', methods=['GET', 'POST'])
@login_required
def customer_create():
    form = CustomerForm()
    try:
        if form.validate_on_submit():
            new_customer = Customer(
                name=form.name.data,
                contact_info=form.contact_info.data,
                address=form.address.data,
                phone_number=form.phone_number.data,
                email=form.email.data
            )
            db.session.add(new_customer)
            db.session.commit()
            flash('Customer created successfully!', 'success')
            return redirect(url_for('customer.customer_list'))
    except IntegrityError as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"Error: {str(e.orig)}", 'danger')  # Flash specific database error message
    except Exception as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"An unexpected error occurred: {str(e)}", 'danger')  # Flash unexpected error message

    return render_template('customer/customer_form.html', form=form)

# Update Customer Route
@customer_bp.route('/customer_update/<int:pk>', methods=['GET', 'POST'])
@login_required
def customer_update(pk):
    customer = Customer.query.get_or_404(pk)  # Fetch customer by primary key
    form = CustomerForm(obj=customer)  # Bind the form to the customer instance

    if form.validate_on_submit():
        customer.name = form.name.data
        customer.contact_info = form.contact_info.data
        customer.address = form.address.data
        customer.phone_number = form.phone_number.data
        customer.email = form.email.data

        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customer.customer_list'))

    return render_template('customer/customer_form.html', form=form, customer=customer)

# Delete Customer Route
@customer_bp.route('/customer_delete/<int:pk>', methods=['GET', 'POST'])
@login_required
def customer_delete(pk):
    # Fetch the customer by primary key
    customer = Customer.query.get_or_404(pk)
    form = CustomerForm()
    
    # If the form is submitted (POST)
    if request.method == 'POST':
        try:
            db.session.delete(customer)
            db.session.commit()  # Commit the transaction
            flash('Customer deleted successfully!', 'success')
            print('Customer deleted successfully!')
            return redirect(url_for('customer.customer_list'))  # Redirect to the customer list page
        except IntegrityError as e:
            db.session.rollback()  # Rollback if there is an error
            flash(f"Error deleting customer: {str(e.orig)}", 'danger')
            print(f"Error deleting customer: {str(e.orig)}")
            return redirect(url_for('customer.customer_list'))  # Return to customer list if error occurs
        except Exception as e:
            db.session.rollback()  # Rollback if there is any other unexpected error
            flash(f"An unexpected error occurred: {str(e)}", 'danger')
            print(f"An unexpected error occurred: {str(e)}")
            return redirect(url_for('customer.customer_list'))  # Return to customer list in case of unexpected errors
    
    # If the method is GET, just display the delete confirmation page
    return render_template('customer/customer_delete.html', form=form, customer=customer)
