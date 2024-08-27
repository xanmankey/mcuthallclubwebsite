from db import db


class RoleUser(db.Model):
    __tablename__ = "role_users"

    user_id = db.Column(db.Integer, db.ForeignKey(f"users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey(f"roles.id"), nullable=False)
