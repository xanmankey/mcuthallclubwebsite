from db import db


class VoteUser(db.Model):
    __tablename__ = "vote_users"

    user_id = db.Column(db.Integer, db.ForeignKey(f"users.id"), nullable=False)
    vote_id = db.Column(db.Integer, db.ForeignKey(f"votes.id"), nullable=False)
