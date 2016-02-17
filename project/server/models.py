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
    registered_on = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(255), nullable=False)


    def __init__(self, registered_on, name, price, category):
        self.registered_on = registered_on
        self.name = name
        self.price = price
        self.category = category
        self.registered_on = datetime.datetime.now()



    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)


class Products(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # registered_on = db.Column(db.DateTime, nullable=False)
    pro_id = db.Column(db.Integer, db.ForeignKey(Product.id),
                       unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id),
                        unique=False, nullable=False)

    def __init__(self, pro_id, user_id):
        self.pro_id = pro_id
        self.user_id = user_id

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)
