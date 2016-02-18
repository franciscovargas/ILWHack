# project/server/models.py


import datetime

from project.server import app, db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        )
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
    """
    def get_prods(self):
        results = (session.query(PlayerModel)
                  .join(PlayerModel.messages)
                  .values(PlayerModel.username,
                          MessageModel.message,
                          MessageModel.time))
        # results will be a generator object

        # This seems a bit convoluted, but here you go.
        resultlist = []
        for username, message, time in results:
            resultlist.append({'message': message,
                               'username': username,
                               'time': time})
    """

    def __repr__(self):
        return '<User {0}>'.format(self.email)


class Product(db.Model):

    __tablename__ = "prodcut"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Unicode(64), unique=False, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.Unicode(64), nullable=False)
    brand = db.Column(db.Unicode(64), nullable=False)
    image_url = db.Column(db.Unicode(64), nullable=False)
    url = db.Column(db.Unicode(64), nullable=False)
    manu = db.Column(db.Unicode(64), nullable=False)
    mindev = db.Column(db.Integer, nullable=False)
    maxdev = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    shipping = db.Column(db.Integer, nullable=False)



    def __init__(self, sku, category, brand, name, image_url,
                 url, price, manu,  shipping, mindev, maxdev,
                 discount):
        self.name = name
        self.price = price
        self.category = category
        self.brand = brand
        self.image_url = image_url
        self.url = url
        self.manu = manu
        self.mindev = mindev
        self.maxdev = maxdev
        self.discount = discount
        self.shipping = shipping
        self.sku = sku




    def get_id(self):
        return self.id

    def __repr__(self):
        return '<prod {0}>'.format(self.name)


class Products(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # registered_on = db.Column(db.DateTime, nullable=False)
    sku = db.Column(db.Integer,db.ForeignKey(Product.sku), nullable=False)
    email = db.Column(db.Unicode(255), db.ForeignKey(User.email))
    name = db.Column(db.Unicode(64), nullable=False)
    sname = db.Column(db.Unicode(64), nullable=False)
    sat = db.Column(db.Integer, nullable=False)


    def __init__(self, sku, email, name, sname, sat):
        self.sku = sku
        self.email = email
        self.name = name
        self.sname = sname
        self.sat = sat

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<prods {0}>'.format(self.name)
