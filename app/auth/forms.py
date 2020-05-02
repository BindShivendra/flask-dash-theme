from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, TextAreaField
from wtforms.validators import Email, DataRequired, Length, Regexp, EqualTo
from wtforms import ValidationError

from .models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(1.64),
                                       Regexp(
                                           '^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')
                                       ])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo(
                                 'password1', message='Password must match')]
                             )
    password1 = PasswordField('Confirm password',
                              validators=[DataRequired(), EqualTo(
                                  'password', message='Password must match')]
                              )
    submit = SubmitField('Sign Up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Username taken.')


class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Old password', validators={DataRequired()})
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo(
                                 'password2', message='Password must match')]
                             )
    password1 = PasswordField('Confirm password',
                              validators=[DataRequired(), EqualTo(
                                  'password', message='Password must match')]
                              )
    submit = SubmitField('Change password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Change password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class EmailChangeForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators={DataRequired()})
    submit = SubmitField('Change password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')


class EditProfileForm(FlaskForm):
    name = StringField('Name ', validators=[Length(1, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    profile_image = FileField('Profile Image')
    submit = SubmitField('Submit')
