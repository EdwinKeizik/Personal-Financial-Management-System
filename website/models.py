from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Finances:
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    name = db.Column(db.String(255))
    date = db.Column(db.Date, default=func.current_date())
    type = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Income(Finances, db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Expenses(Finances, db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Planning(Finances, db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Savings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class ChatAI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    message = db.Column(db.String(10000))
    response = db.Column(db.String(10000))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    income = db.relationship("Income")
    expenses = db.relationship("Expenses")
    planning = db.relationship("Planning")
    savings = db.relationship("Savings")
    chat_ai = db.relationship("ChatAI")