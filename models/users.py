from datetime import datetime
from flask_login import UserMixin
from db import db
from sqlalchemy.orm import validates
from models.role_user import RoleUser
from models.vote_user import VoteUser


class User(db.Model, UserMixin):
    __tablename__ = "users"

    full_name = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    img = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.String(100), nullable=True)
    platform = db.Column(db.String(1000), nullable=True)
    confirmed_at = db.Column(db.DateTime(), default=datetime.now())
    # Active discusses user activity; can be used for soft-deletion
    is_active = db.Column(db.Boolean(), default=True)
    is_authenticated = db.Column(db.Boolean(), default=False)
    is_anonymous = db.Column(db.Boolean(), default=False)
    roles = db.relationship(
        "Role", secondary=RoleUser.__tablename__, back_populates="users"
    )
    running = db.Column(db.ForeignKey("roles.id"), nullable=True)
    votes = db.relationship(
        "Vote", secondary=VoteUser.__tablename__, back_populates="users"
    )

    @validates("email")
    def validate_email(self, email):
        if not email.contains("@purdue.edu"):
            raise ValueError("You must use your purdue email address.")
        else:
            return email

    # Flask-Login required method
    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __repr__(self):
        string = "<{}(".format(self.__class__.__name__)
        for field in self.__dict__:
            string += f"{field}: {getattr(self, field.value)}, "
        string = string[:-2] + ")>"
        return string

    def __str__(self):
        string = "<{}(".format(self.__class__.__name__)
        for field in self.__dict__:
            string += f"{field}: {getattr(self, field.value)}, "
        string = string[:-2] + ")>"
        return string
