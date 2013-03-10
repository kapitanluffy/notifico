# -*- coding: utf8 -*-
from flask import render_template
from flask.ext import wtf

from notifico import app


class LoginForm(wtf.Form):
    username = wtf.TextField('Username', validators=[
        wtf.Required()
    ])
    password = wtf.PasswordField('Password', validators=[
        wtf.Required()
    ])


class SignUpForm(wtf.Form):
    username = wtf.TextField('Username', validators=[
        wtf.Required(),
        wtf.Length(min=2, max=50),
        wtf.Regexp('^[a-zA-Z0-9_]*$', message=(
            'Username must only contain a to z, 0 to 9, and underscores.'
        ))
    ], description=(
        'Your username is public and used as part of your project name.'
    ))
    email = wtf.TextField('Email', validators=[
        wtf.Required(),
        wtf.validators.Email()
    ])
    password = wtf.PasswordField('Password', validators=[
        wtf.Required(),
        wtf.Length(5),
        wtf.EqualTo('confirm', 'Passwords do not match.'),
    ])
    confirm = wtf.PasswordField('Confirm Password')


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """
    Present the user with a login form, and authenticate them on POST.
    """
    login_form = LoginForm()
    return render_template('user/login.jinja', login_form=login_form)


@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    """
    Present the user with a sign up form, creating an account on POST.
    """
    signup_form = SignUpForm()
    return render_template('user/register.jinja', signup_form=signup_form)
