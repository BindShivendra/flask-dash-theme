from flask import render_template, url_for, \
    redirect, request, flash, current_app, \
    abort, send_file
from flask_login import login_user, logout_user, login_required, current_user


from dash import db
from . import auth
from .models import User, Profile
from .forms import LoginForm, RegistrationForm, EmailChangeForm, \
    PasswordChangeForm, PasswordResetRequestForm, PasswordResetForm, \
    EditProfileForm
from ..email import send_email
from .utils import allowed_file, resize_image_and_save


@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        if current_user.profile:
            profile = Profile.query.filter_by(user_id=current_user.id).first()
            profile.ping()
        if not current_user.confirmed \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.main')
            return redirect(next)
        flash('Invalid email or password')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.main'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confimation_token()
        send_email(user.email, 'Account confimation',
                   'auth/email/confirm', user=user, token=token)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.main'))

    if current_user.confirm(token):
        db.session.commit()
        flash('Thakn you for confirming your email.')
    else:
        flash('Link is invalid or expired')
    return redirect(url_for('main.main'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.main'))

    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confimation_token()
    send_email(current_user.email, 'Account confimation',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email sent to your registered email')
    return redirect(url_for('main.main'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.main'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    current_app.logger.info(current_user)
    if not current_user.is_anonymous:
        return redirect(url_for('main.main'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.main'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.main'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = EmailChangeForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.main'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.main'))


@auth.route('/user/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('auth/profile.html', user=user)


@auth.route('/edit-profile', methods=['GET', 'Post'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        profile = current_user.profile
        profile.name = form.name.data
        profile.location = form.location.data
        profile.about_me = form.about_me.data
        image = form.profile_image.data
        current_app.logger.info(image.filename)
        if image is not None and image != '':
            if not allowed_file(image.filename):
                flash("Please upload 'webp', 'png', 'jpg', 'jpeg' and 'gif' only")
                return redirect(url_for('auth.edit_profile'))
            try:
                profile.profile_image = resize_image_and_save(
                    image, current_app.config['UPLOAD_FOLDER'], current_user.username)
            except Exception as e:
                current_app.logger.info(f'image uploaed failed {e}')
                abort(500)
                # TODO : handle exception

        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Update sucess')
        return redirect(url_for('auth.profile', username=current_user.username))
    if current_user.profile is not None:
        form.name.data = current_user.profile.name
        form.location.data = current_user.profile.location
        form.about_me.data = current_user.profile.about_me

    return render_template('auth/edit_profile.html', form=form)


@auth.route('/media')
def media():
    image = current_user.profile.profile_image or None
    if image:
        return send_file(image)
    return None
