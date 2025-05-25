from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, current_user, logout_user
from app import db
from .models import User
from .forms import RegistrationForm, LoginForm, UserForm, UserEditForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint('users', __name__)

# Register Route
@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    try:
        if form.validate_on_submit():
            # Hash the password before storing it
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

            # Create a new user
            new_user = User(username=form.username.data, password=hashed_password,
                            first_name=form.first_name.data, last_name=form.last_name.data,
                            email=form.email.data, role=form.role.data)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful!', 'success')
            return redirect(url_for('users.login_view'))  # Redirect to login page after successful registration
    except IntegrityError as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"Error: {str(e.orig)}", 'danger')  # Flash specific database error message
    except Exception as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"An unexpected error occurred: {str(e)}", 'danger')  # Flash unexpected error message
    return render_template('users/register.html', form=form)

# Login Route
@users_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    form = LoginForm()
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):  # Check the password hash
                login_user(user)
                return redirect(url_for('users.user_list'))  # Redirect to user list after successful login
            flash('Invalid username or password.', 'danger')
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", 'danger')
    return render_template('users/login.html', form=form)

# Logout Route
@users_bp.route('/logout')
@login_required  # Ensure that only logged-in users can access this route
def logout():
    logout_user()  # Log the user out
    flash('You have been logged out successfully.', 'success')  # Flash a success message
    return redirect(url_for('users.login_view'))  # Redirect to the login page

# User List Route (View all users)
@users_bp.route('/')
@login_required
def user_list():
    try:
        users = User.query.all()
        return render_template('users/user_list.html', users=users)
    except Exception as e:
        flash(f"An error occurred while fetching users: {str(e)}", 'danger')
        return redirect(url_for('users.login_view'))

# Create User Route
@users_bp.route('/user_create', methods=['GET', 'POST'])
@login_required
def user_create():
    # if current_user.role != 'admin':
    #     flash("You don't have permission to access this page.", 'danger')
    #     return redirect(url_for('users.user_list'))

    form = UserForm()
    try:
        if form.validate_on_submit():
            # Hash the password before storing it
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

            new_user = User(username=form.username.data, password=hashed_password,
                            first_name=form.first_name.data, last_name=form.last_name.data,
                            email=form.email.data, role=form.role.data)
            db.session.add(new_user)
            db.session.commit()

            flash('User created successfully!', 'success')
            return redirect(url_for('users.user_list'))
    except IntegrityError as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"Error: {str(e.orig)}", 'danger')  # Flash specific database error message
    except Exception as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"An unexpected error occurred: {str(e)}", 'danger')  # Flash unexpected error message

    return render_template('users/user_form.html', form=form)

# Edit User Route
@users_bp.route('/user_edit/<int:pk>', methods=['GET', 'POST'])
@login_required
def user_edit(pk):
    user = User.query.get_or_404(pk)
    # if current_user.role != 'admin' and current_user.id != pk:
    #     flash("You don't have permission to access this page.", 'danger')
    #     return redirect(url_for('users.user_list'))
    
    # Bind the form to the user instance
    form = UserEditForm(obj=user)  # Initialize form with the user instance
    print(form.data,form.validate_on_submit(),"sdfsdf")
    if form.validate_on_submit():
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.role = form.role.data

        # If password is being changed
        # if form.password.data:
        #     user.password = generate_password_hash(form.password.data, method='sha256')

        db.session.commit()

        flash('User updated successfully!', 'success')
        return redirect(url_for('users.user_list'))

    return render_template('users/user_form.html', form=form, user=user)

# Delete User Route
@users_bp.route('/user_delete/<int:pk>', methods=['POST'])
@login_required
def user_delete(pk):
    user = User.query.get_or_404(pk)
    # if current_user.role != 'admin':
    #     flash("You don't have permission to access this page.", 'danger')
    #     return redirect(url_for('users.user_list'))

    try:
        db.session.delete(user)
        db.session.commit()

        flash('User deleted successfully!', 'success')
        return redirect(url_for('users.user_list'))
    except Exception as e:
        db.session.rollback()  # Rollback any pending changes
        flash(f"An error occurred while deleting the user: {str(e)}", 'danger')
        return redirect(url_for('users.user_list'))

