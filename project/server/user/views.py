# project/server/user/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_user, logout_user, login_required

from project.server import bcrypt, db
from project.server.models import User, Product, Products
from project.server.user.forms import *


from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

import numpy as np
################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)


################
#### routes ####
################

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash('Thank you for registering.', 'success')
        return redirect(url_for("user.members"))

    return render_template('user/register.html', form=form)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            flash('You are logged in. Welcome!', 'success')
            return redirect(url_for('user.members'))
        else:
            flash('Invalid email and/or password.', 'danger')
            return render_template('user/login.html', form=form)
    return render_template('user/login.html', title='Please Login', form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out. Bye!', 'success')
    return redirect(url_for('main.home'))


@user_blueprint.route('/members')
@login_required
def members():
    # print "###################"
    form = ProductRank(request.form)
    # print "BUG"
    return render_template('user/members.html', form=form)


@user_blueprint.route('/members/stats')
@login_required
def member_stats():

    graph_list = ["poly", "bokeh"]

    def getitem(obj, item, default):
        if item not in obj:
            return default
        else:
            return obj[item]

    x = {'products':[u'samsung 1234', u'nokia 1234', u'htc'],
         'prices': [10, 5, 2]}
    x1 = zip(x['products'], x['prices'])
    colors = {
        'Black': '#000000',
        'Red':   '#FF0000',
        'Green': '#00FF00',
        'Blue':  '#0000FF',
    }
    args = request.args
    # Get all the form arguments in the url with defaults
    color = colors[getitem(args, 'color', 'Black')]
    _from = int(getitem(args, '_from', 0))
    to = int(getitem(args, 'to', 10))
    # graph = getitem(args, 'graph', 'Black')

    # Create a polynomial line graph
    N = to

    x = np.random.random(size=N) * 100
    y = np.random.random(size=N) * 100
    radii = np.random.random(size=N) * 1.5
    colors = [
        "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
    ]

    TOOLS="resize,hover,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"

    fig = figure(title="bubbles",
                 tools=TOOLS,
                 x_range=(0,100),
                 y_range=(0,100))
    fig.circle(x,y, radius=radii, fill_color=colors, fill_alpha=0.6, line_color=None)
    fig2 = figure(title="poly")
    fig2.line(x, y)
    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#bokeh-embed
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
    script, div = components(fig, INLINE)
    script2, div2 = components(fig2, INLINE)


    return render_template('user/member_stats.html',
                            x=x1,
                            plot_script=script,
                            plot_div=div,
                            plot_script2=script2,
                            plot_div2=div2,
                            js_resources=js_resources,
                            css_resources=css_resources,
                            color=color,
                            _from=_from,
                            to=to)
