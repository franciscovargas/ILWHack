# manage.py

from collections import OrderedDict
import os
import unittest
import coverage

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from pandas.compat import u

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
    """Creates sample data."""
    init_dat = pd.read_csv("project/test.csv")
    # print init_dat.keys()
    # print [mlp.keys[0] ,init_dat.keys()[0]]
    # jdfkshfkjhfdskj
    db.session.text_factory = str
    cats = map( set, dict(init_dat[mlp.cat_vec]).values())
    cat_dics = map(dict, (map(lambda x: zip(x,range(len(x))) , cats)) )
    cat_dics = OrderedDict(zip(mlp.cat_vec, cat_dics))
    # print cat_dics
    # print init_dat[mlp.keys]

    for y in mlp.cat:
        init_dat[y] = map(u, init_dat[y])
    for y in mlp.cat_vec:
        init_dat[y].replace(cat_dics[y], inplace=True)

    print init_dat[mlp.cat_vec]
    # bbbb
    print "RELABLING DONE"
    print len(mlp.keys)
    print init_dat[mlp.keys]
    print len(init_dat[mlp.keys])
    for x in init_dat[mlp.keys].iterrows():
        print OrderedDict(x[1]).keys()
        db.session.add(Product(*list(OrderedDict(x[1]).values()) ))
    print "DATA ADDED"
    db.session.commit()

@manager.command
def create_data_pur():
    init_dat = pd.read_csv("project/fakeData.csv")
    for x in init_dat.iterrows():
        print OrderedDict(x[1]).keys()
        db.session.add(Products(*list(OrderedDict(x[1]).values()) ))

@manager.command
def create_data_u():
    init_dat = pd.read_csv("project/fakeu.csv")
    for x in init_dat.iterrows():
        print OrderedDict(x[1]).keys()
        db.session.add(User(*list(OrderedDict(x[1]).values()) ))


if __name__ == '__main__':
    manager.run()
