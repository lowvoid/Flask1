from datetime import datetime
from VAG import db, login_manager
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    bio = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(60), nullable=False)

    services = db.relationship('Service', backref='author', lazy=True ,cascade="all, delete-orphan")
    features = db.relationship('Feature', backref='author', lazy=True, cascade="all, delete-orphan")


    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], salt='pw-reset')
        return s.dumps({'user_id': self.id})
    @staticmethod
    def verify_reset_token(token, age=3600):
        s = Serializer(current_app.config['SECRET_KEY'], salt='pw-reset')
        try:
            user_id = s.loads(token,max_age=age)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


service_members = db.Table('service_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(150), nullable=False)
    icon = db.Column(db.String(20), nullable=False, default='default_icon.jpg')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"), nullable=False)

    is_private = db.Column(db.Boolean, default=False)  
    join_password = db.Column(db.String(100), nullable=True)  

    invite_code = db.Column(db.String(10), unique=True, nullable=True)  
    members = db.relationship('User', secondary='service_members', backref='joined_services')

    features = db.relationship('Feature',backref='service',lazy=True,cascade="all, delete-orphan")



    def __repr__(self):
        return f"Service('{self.name}', private={self.is_private})"


class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(20), nullable=False, default='default_thumbnail.jpg')
    slug = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id',ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"Feature('{self.title}', '{self.date_posted}')"


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Contact('{self.name}', '{self.email}')"
    

