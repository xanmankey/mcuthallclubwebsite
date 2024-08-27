from db import db
from models.vote_user import VoteUser


class Vote(db.Model):
    __tablename__ = "votes"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    president = db.Column(db.ForeignKey("users.id"), nullable=True)
    vice_president = db.Column(db.ForeignKey("users.id"), nullable=True)
    treasurer = db.Column(db.ForeignKey("users.id"), nullable=True)
    secretary = db.Column(db.ForeignKey("users.id"), nullable=True)
    grand_prix_rep = db.Column(db.ForeignKey("users.id"), nullable=True)
    resident_satisfaction_committee_head = db.Column(
        db.ForeignKey("users.id"), nullable=True
    )
    purchasing_committee_head = db.Column(db.ForeignKey("users.id"), nullable=True)
    event_committee_head = db.Column(db.ForeignKey("users.id"), nullable=True)
    hall_club_representation_committee_head = db.Column(
        db.ForeignKey("users.id"), nullable=True
    )

    users = db.relationship(
        "User", secondary=VoteUser.__tablename__, back_populates="votes"
    )

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
