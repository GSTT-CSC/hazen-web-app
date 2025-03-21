"""
Set of functions which dictate the behaviour of the admin functionality, e.g. registering and logging in.
Utilises the functions in the app.auth.forms module.
"""

from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, Flask
from werkzeug.urls import url_parse
from flask_login import login_user, login_required, logout_user, current_user

from app import db
from app.auth import bp
from app.auth.forms import RegistrationForm, LoginForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
from app.auth.email import validate_nhs_email
from app.auth.email import verify_email_auth_token



@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        #create new user
        user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            institution=form.institution.data,
            username=form.username.data,
            email=form.email.data,
            email_authenticated=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        #send email verification
        validate_nhs_email(user)

        flash('Please check your email for the verification link. The link will expire in 10 minutes.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register', form=form)

@bp.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    current_app.logger.info(f"Received token: {token}")
    user = verify_email_auth_token(token)
    if not user:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('auth.register'))

    flash('Email confirmed successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))




@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        if not user.email_authenticated:
            flash('Please verify your email address first.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(url_for('main.index'))

    return render_template('login.html', title='Sign In', form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit(): # if request.method == 'POST'
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.institution = form.institution.data
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('main.index'))

    # populate fields with current values from the User table
    form.firstname.data = current_user.firstname
    form.lastname.data = current_user.lastname
    form.institution.data = current_user.institution
    form.username.data = current_user.username

    return render_template('edit_profile.html', title='Edit Profile', form=form, page='edit_profile')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                            title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)
