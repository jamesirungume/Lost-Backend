from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    role = db.Column(db.String)
    password = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship with Item (Reported by)
    lostitems_reported = relationship('Item', back_populates='user_reported')

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String)
    item_description = db.Column(db.String)
    image_url = db.Column(db.String)
    categories = db.Column(db.String)
    reward = db.Column(db.String)
    status = db.Column(db.String)
    reported_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship with User (User who reported)
    user_reported_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_reported = relationship('User', back_populates='lostitems_reported')

    # Relationship with Comment (Comment on)
    comments = relationship('Comment', back_populates='lostitem')

   
class Reward(db.Model):
    __tablename__ = 'rewards'

    id = db.Column(db.Integer, primary_key=True)
    rewardamount = db.Column(db.String)

    # Relationship with Item (Has Reward)
    lostitem_id = db.Column(db.Integer, db.ForeignKey('items.id'))

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    
    # Relationship with Item (Comment on)
    lostitem_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    lostitem = relationship('Item', back_populates='comments')
    
class Claim(db.Model):
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String, nullable=False)
    
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'))
    payer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
