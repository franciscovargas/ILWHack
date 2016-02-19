# project/server/user/views.py
"""
Here be dragons... the core bulk of the app
occurs in an unabstracted illegible fashion
in the next lines.
"""
#################
#### imports ####
#################

from bokeh.charts import Area, show, vplot, output_file, defaults
from bokeh.plotting import *
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request,session
from flask.ext.login import login_user, logout_user, login_required
from flask import g
from project.server import bcrypt, db
from project.server.models import User, Product, Products
from project.server.user.forms import *
from ... import ml_p as mlp
from  sqlalchemy.sql.expression import func, select

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import HoverTool


import numpy as np
import pandas as  pd
from sklearn.neighbors import NearestNeighbors


import random
from collections import Counter
from copy import deepcopy
from collections import OrderedDict
from itertools import chain
################
#### config ####
################
user_blueprint = Blueprint('user', __name__,)
user = None

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
            # Flask allows use of global variables
            # here I store the user email for further queries
            session["user"] = user.__dict__["email"]
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
    # Main loged in users arival page
    form = ProductRank(request.form)
    return render_template('user/members.html', form=form)


@user_blueprint.route('/members/stats')
@login_required
def member_stats():
    """
    This function carries out knn, and all the other relevant statistics + graphs
    produced by this toool. Some optmixations should be carried out
    and the plots should be abstracted in to their own seperate methods
    """


    # Panda parsers
    pandifycv2 = lambda x: pd.DataFrame(x.__dict__, index=[0])[mlp.cat_vec2]
    pandifynv2 = lambda x: list(pd.DataFrame(x.__dict__, index=[0])[mlp.num_vec2].iloc[0])

    out = db.session.query(Product).join(Products).join(User).filter(User.email == session["user"])

    num_per_vec = np.mean(map(pandifynv2, out.all()), axis=0)

    # Parsing the user data in to a feature vector
    for k, ind in  enumerate(map(pandifycv2, out.all())):
        cat_per_vec = deepcopy(mlp.cat_matrix)
        for i,d in enumerate(dict(ind).values()):
            cat_per_vec[i][int(list(d)[0])] = 1

    # Averaging out to project the person in to product space.
    per_vec = list(np.sum(cat_per_vec, axis=0)) + list(num_per_vec)

    # for plotting purposes
    xn= per_vec[-4]
    yn =per_vec[-3]

    # Taking a random slice of size 700 out of our  products to use as training
    # for the recomender model
    rand = random.randrange(700,5400)
    out2 = db.session.query(Product).outerjoin(Products).filter(Products.email == None)[rand-700:rand]

    # Ser up variables for parsing the trainign set
    cat_train = deepcopy(mlp.cat_matrix)
    num_train = map(pandifynv2, out2)
    train = list()
    end = enumerate(map(pandifycv2, out2)  )

    # Cur dictionary which is later on used as a data structure for creating
    # plots that sumarize costs per Manufacturer.
    # This is slow. Another aditional thing that takes place here is the collapse
    # of the cathegorical variables in to a binary representation.
    cur = dict()
    for k, ind in  end:
        cat_train = deepcopy(mlp.cat_matrix)
        for i,d in enumerate(dict(ind).values()):
            cat_train[i][int(list(d)[0])] = 1

        if mlp.cat_dics["manu"][int(list(ind["manu"])[0])] in cur:
            cur[mlp.cat_dics["manu"][int(list(ind["manu"])[0])]].append(num_train[k][1])
        else:
            cur[mlp.cat_dics["manu"][int(list(ind["manu"])[0])]] =[ num_train[k][1]]

        train.append(list(chain(*cat_train)) + num_train[k])

    # K-neares neighbors object fitting on the training set (products from
    # data base)
    nbrs = NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(train)
    # predicting on current user who are his 5 closest prducts
    distances, indices = nbrs.kneighbors(per_vec)

    # Formatting the prediction in to a useful html renderable form
    prediction = [(out2[ind].__dict__["name"], out2[ind].__dict__["price"], out2[ind].__dict__["url"])
                  for ind in indices[0]]

    # variable used by bokeh for tooltip lables
    labl = [out2[ind].__dict__["name"] for ind in range(len(out2))]

    # Yes this is a crime
    getitem = lambda obj, item, default: default if item not in obj else obj[item]

    # price dimension of the training set
    # max number of delivery days of the training set
    trainprice = np.array(train)[:,-4]
    trainmax = np.array(train)[:,-3]


    # Get all the form arguments in the url with defaults
    args = request.args
    _from = int(getitem(args, '_from', 0))
    to = int(getitem(args, 'to', 10))

    # color dict for space plot ahead
    colors = [
        "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*trainprice, 30+2*trainmax)
    ]

    TOOLS="resize,hover,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"

    # Data sources for the first plot
    source = ColumnDataSource(
        data=dict(
            x=trainprice,
            y=trainmax,
            label=labl
        )
    )
    source2 = ColumnDataSource(
        data=dict(
            x=[xn],
            y=[yn],
            label=["YOU"]
        )
    )

    fig = figure(title="Price vs Discount",
                 tools=TOOLS,
                x_axis_label = "Price",
                y_axis_label = "Discount")
    fig.circle(x='x',y='y', radius=150, fill_color=colors,
              fill_alpha=0.6, line_color=None, source=source)
    fig.square(x='x',y='y',  fill_color="yellow",size=20,
               line_color="green", source=source2)
    # fig.xgrid.grid_line_color = None
    fig.axis.major_tick_line_color = None
    fig.axis[0].ticker.num_minor_ticks = 0
    fig.axis[1].ticker.num_minor_ticks = 0
    fig.outline_line_color = "white"
    fig.xaxis.axis_line_color = "white"
    fig.yaxis.axis_line_color = "white"

    hover =fig.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ("label", "@label"),
    ])

    # Generation of the second plot
    plt_list = list()
    for k, v in cur.items():
        plt_list.append((k, np.mean(v), np.std(v)))

    # Sorce data for tthe second plot
    plt_list.sort(key=lambda x: x[1])
    source3 = ColumnDataSource(
        data=dict(
            x=range(len(np.array(plt_list)[:,0])),
            y= np.array(plt_list)[:,1],
            label=np.array(plt_list)[:,0]
        )
    )
    xr = range(len(np.array(plt_list)[:,0])) + list(reversed(range(len(np.array(plt_list)[:,0]))))
    yr = list((np.array(plt_list)[:,1].astype(float))) + list(reversed(np.array(plt_list)[:,1].astype(float) + np.array(plt_list)[:,2].astype(float)))

    source4 = ColumnDataSource(
        data=dict(
            x=xr,
            y= yr,
            label=list(np.array(plt_list)[:,0])*2
        )
    )


    yr2 = list((np.array(plt_list)[:,1].astype(float))) + list(reversed(np.array(plt_list)[:,1].astype(float) - np.array(plt_list)[:,2].astype(float)))

    source5 = ColumnDataSource(
        data=dict(
            x=xr,
            y= yr2,
            label=list(np.array(plt_list)[:,0])*2
        )
    )


    fig2 = figure(title="Manufacturer and their average cost", tools=TOOLS,
       x_axis_label = "Manufacturer",
       y_axis_label = "Averag Price")
    # fig2.circle(x='x', y='y' , source=source3)
    fig2.patch(x='x', y='y', color="#99d8c9" , source=source4)
    fig2.patch(x='x', y='y', color="#99d8c9" , source=source5)
    fig2.line(x='x' , y='y' , source=source3)
    fig2.xgrid.grid_line_color = None
    fig2.axis[0].major_label_text_font_size = "0pt"
    fig2.axis.major_tick_line_color = None
    fig2.axis[0].ticker.num_minor_ticks = 0
    fig2.axis[1].ticker.num_minor_ticks = 0
    fig2.outline_line_color = "white"
    fig2.xaxis.axis_line_color = "white"
    fig2.yaxis.axis_line_color = "white"
    hover2 =fig2.select(dict(type=HoverTool))
    hover2.tooltips = OrderedDict([
        ("label", "@label"),
    ])

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(fig, INLINE)
    script2, div2 = components(fig2, INLINE)

    return render_template('user/member_stats.html',
                            plot_script=script,
                            plot_div=div,
                            plot_script2=script2,
                            plot_div2=div2,
                            js_resources=js_resources,
                            css_resources=css_resources,
                            _from=_from,
                            to=to,
                            prediction=prediction)
