# -*- coding: utf8 -*-
from flask import (
    render_template,
    redirect,
    url_for,
    g,
    session
)
from flask.ext import wtf

from notifico import app
from notifico.models import User


class LoginForm(wtf.Form):
    username = wtf.TextField('Username', validators=[
        wtf.Required()
    ])
    password = wtf.PasswordField('Password', validators=[
        wtf.Required()
    ])

    def validate_password(form, field):
        if not User.login(form.username.data, field.data):
            raise wtf.ValidationError('Incorrect username and/or password.')


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
    confirm = wtf.PasswordField('Confirm Password', validators=[
        wtf.Required()
    ])


@app.before_request
def set_logged_in_user():
    g.user = None
    if '_u' in session and '_uu' in session:
        g.user = User.query.filter_by(
            id=session['_u'],
            username=session['_uu']
        ).first()


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """
    Present the user with a login form, and authenticate them on POST.
    """
    # An already logged-in user should not be able to login again
    # without first logging out.
    if g.user:
        return redirect(url_for('projects_dashboard'))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        u = User.by_username(login_form.username.data)
        session.update({
            '_u': u.id,
            '_uu': u.username
        })
        return redirect(url_for('projects_dashboard'))

    return render_template('user/login.jinja', login_form=login_form)


@app.route('/user/logout')
def user_logout():
    """
    Log the current user out (if any) and return them to the homepage.
    """
    if '_u' in session:
        del session['_u']
    if '_uu' in session:
        del session['_uu']
    return redirect(url_for('misc_landing'))


@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    """
    Present the user with a sign up form, creating an account on POST.
    """
    # User registration is disabled on this Notifico instance,
    # so toss them back to the homepage.
    if not app.config.get('ENABLE_SIGNUP', False):
        return redirect(url_for('misc_landing'))

    signup_form = SignUpForm()
    return render_template('user/register.jinja', signup_form=signup_form)
