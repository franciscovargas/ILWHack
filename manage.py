# manage.py

from collections import OrderedDict
import os
import unittest
import coverage

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from pandas.compat import u
from flask import g

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/server/config.py',
        'project/server/*/__init__.py'
    ]
)
COV.start()

from project.server import app, db
from project.server.models import *
from project import ml_p as mlp
import pandas as pd

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)
# user = None

@manager.command
def test():
    """Runs the unit tests without coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    else:
        return 1


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(User(email='ad@min.com', password='admin', admin=True))
    db.session.commit()


@manager.command
def create_data():
    """
    Fills in the product table with real data that is later
    on used to build a feature vector
    """
    init_dat = pd.read_csv("project/test.csv")

    # To deal with annoying unicode bugs
    db.session.text_factory = str

    # Cats stands for categorys
    # In the next 10 lines we relable the string categorical DATA
    #  to a numerical integer representation
    cats = map( set, dict(init_dat[mlp.cat_vec]).values())
    cat_dics = map(dict, (map(lambda x: zip(x,range(len(x))) , cats)) )
    cat_dics = OrderedDict(zip(mlp.cat_vec, cat_dics))

    # Remaping done with pandings to spead things up
    for y in mlp.cat:
        init_dat[y] = map(u, init_dat[y])
    for y in mlp.cat_vec:
        init_dat[y].replace(cat_dics[y], inplace=True)

    # Insertions and commisions
    for x in init_dat[mlp.keys].iterrows():
        db.session.add(Product(*list(OrderedDict(x[1]).values()) ))
    db.session.commit()

@manager.command
def create_data_pur():
    """
    This method pulls in fake genereic purchases that we designed
    to test and motivate our recomender system.
    """
    init_dat = pd.read_csv("project/fd.csv")
    for y in init_dat.keys():
        try:
            init_dat[y] = map(u, init_dat[y])
        except:
            pass
    for x in init_dat.iterrows():
        db.session.add(Products(*list(OrderedDict(x[1]).values()) ))
    db.session.commit()

@manager.command
def create_data_u():
    """
    This methods adds in our fake users.
    """
    init_dat = pd.read_csv("project/fakeu.csv")
    for y in init_dat.keys():
        init_dat[y] = map(u, init_dat[y])
    for x in init_dat.iterrows():
        print OrderedDict(x[1]).keys()
        db.session.add(User(*list(OrderedDict(x[1]).values()) ))
    db.session.commit()


if __name__ == '__main__':
    manager.run()
