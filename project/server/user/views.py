# project/server/user/views.py
from  sqlalchemy.sql.expression import func, select
import random
from collections import Counter
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
from itertools import chain

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from ... import ml_p as mlp
import numpy as np
from sklearn.neighbors import NearestNeighbors
################
#### config ####
################
import pandas as  pd
from copy import deepcopy
from bokeh.models import HoverTool
from collections import OrderedDict
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
        # global user
        # print session
        print form.email.data
        user = User.query.filter_by(email=form.email.data).first()
        print user
        # request.user = user
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
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
    # print "###################"
    form = ProductRank(request.form)
    # print "BUG"
    return render_template('user/members.html', form=form)


@user_blueprint.route('/members/stats')
@login_required
def member_stats():
    # global user
    # # print request.session
    # # print g
    # print session["user"]
    # g.i = 2
    graph_list = ["poly", "bokeh"]
    Products.query.order_by(func.random())
    Product.query.order_by(func.random())
    User.query.order_by(func.random())
    # vec = lambda x: [x[], x[], x[], x[]]
    pandifycv = lambda x: pd.DataFrame(x.__dict__)[mlp.cat_vec]
    pandifynv = lambda x: pd.DataFrame(x.__dict__)[mlp.num_vec]
    pandifycv2 = lambda x: pd.DataFrame(x.__dict__, index=[0])[mlp.cat_vec2]
    pandifynv2 = lambda x: list(pd.DataFrame(x.__dict__, index=[0])[mlp.num_vec2].iloc[0])

    out = db.session.query(Product).join(Products).join(User).filter(User.email == session["user"])
    # print out.all()[0].__dict__
    # cat_per_vec = deepcopy(mlp.cat_matrix)
    # print list(pd.DataFrame(out.all()[0].__dict__, index=[0])[mlp.num_vec2].iloc[0])
    # print pandifynv2(out.all()[0])
    num_per_vec = np.mean(map(pandifynv2, out.all()), axis=0)

    # print num_per_vec
    # bbbb
    # cat_per_vec = [mlp.cat_matrix[ind] for ind  in map(pandifycv2, out.all())]
    # per_vec = list()
    print num_per_vec.shape
    for k, ind in  enumerate(map(pandifycv2, out.all())):
        cat_per_vec = deepcopy(mlp.cat_matrix)
        for i,d in enumerate(dict(ind).values()):
            cat_per_vec[i][int(list(d)[0])] = 1
    per_vec = list(np.sum(cat_per_vec, axis=0)) + list(num_per_vec)
    # print per_vec
    xn= per_vec[-4]
    yn =per_vec[-3]

    rand = random.randrange(2000,5000)
    out2 = db.session.query(Product).outerjoin(Products).filter(Products.email == None)[rand-1000:rand]
    # print out2

    cat_train = deepcopy(mlp.cat_matrix)
    # cat_per_vec = [mlp.cat_matrix[ind] for ind  in map(pandifycv2, out.all())]
    num_train = map(pandifynv2, out2)
    train = list()
    end = enumerate(map(pandifycv2, out2)  )
    # print out2
    cur = dict()
    for k, ind in  end:
        cat_train = deepcopy(mlp.cat_matrix)
        # print ind
        # print mlp.cat_dics
        for i,d in enumerate(dict(ind).values()):
            # print d
            cat_train[i][int(list(d)[0])] = 1

        # print mlp.cat_dics["manu"]
        # # print int(list(ind["manu"])[0])
        # print num_train[k][:-4]
        if mlp.cat_dics["manu"][int(list(ind["manu"])[0])] in cur:
            cur[mlp.cat_dics["manu"][int(list(ind["manu"])[0])]].append(num_train[k][1])
        else:
            cur[mlp.cat_dics["manu"][int(list(ind["manu"])[0])]] =[ num_train[k][1]]

        train.append(list(chain(*cat_train)) + num_train[k])
    # print train
    nbrs = NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(train)
    distances, indices = nbrs.kneighbors(per_vec)
    # print indices
    # print
    # print out2.all()
    prediction = [(out2[ind].__dict__["name"], out2[ind].__dict__["price"], out2[ind].__dict__["url"])
                  for ind in indices[0]]
    # print "###############"
    labl = [out2[ind].__dict__["name"] for ind in range(len(out2))]
    def getitem(obj, item, default):
        if item not in obj:
            return default
        else:
            return obj[item]
    trainprice = np.array(train)[:,-4]
    trainmax = np.array(train)[:,-3]
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
        "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*trainprice, 30+2*trainmax)
    ]

    TOOLS="resize,hover,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"


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
    # print labl
    hover =fig.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ("label", "@label"),
    ])
    # fig.line(trainprice,trainmax)
    # print trainprice
    # print trainmax

    plt_list = list()
    for k, v in cur.items():

        plt_list.append((k, np.mean(v), np.std(v)))
    plt_list.sort(key=lambda x: x[1])
    source3 = ColumnDataSource(
        data=dict(
            x=range(len(np.array(plt_list)[:,0])),
            y= np.array(plt_list)[:,1],
            label=np.array(plt_list)[:,0]
        )
    )
    fig2 = figure(title="Manufacturer and their average cost", tools=TOOLS,
       x_axis_label = "Manufacturer",
       y_axis_label = "Averag Price")
    fig2.line(x='x' , y='y' , source=source3)
    fig2.circle(x='x', y='y' , source=source3)
    hover2 =fig2.select(dict(type=HoverTool))
    hover2.tooltips = OrderedDict([
        ("label", "@label"),
    ])
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
                            to=to,
                            prediction=prediction)
