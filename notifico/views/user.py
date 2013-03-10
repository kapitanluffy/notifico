# -*- coding: utf8 -*-
from flask import render_template
from flask.ext import wtf

from notifico import app


class UserLoginForm(wtf.Form):
    username = wtf.TextField('Username', validators=[
        wtf.Required()
    ])
    password = wtf.PasswordField('Password', validators=[
        wtf.Required()
    ])


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """
    Present the user with a login form, and authenticate them on POST.
    """
    login_form = UserLoginForm()
    return render_template('user/login.jinja', login_form=login_form)
