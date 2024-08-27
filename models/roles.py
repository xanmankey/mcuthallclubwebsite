from db import db
from models.role_user import RoleUser


class Role(db.Model):
    __tablename__ = "roles"

    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship(
        "User", secondary=RoleUser.__tablename__, back_populates="roles"
    )
    is_electable = db.Column(db.Boolean, default=False)

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
