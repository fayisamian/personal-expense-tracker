
from datetime import datetime
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    expenses = db.relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Expense(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    description = db.Column(db.String(200), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    category = db.Column(db.String(100), nullable=False)

    transaction_type = db.Column(db.String(20), nullable=False)

    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    user = db.relationship("User", back_populates="expenses")
