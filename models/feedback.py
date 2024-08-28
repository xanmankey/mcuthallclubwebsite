from db import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    feedback = db.Column(db.String, nullable=False)

    user = db.relationship("User", backref="Feedback", uselist=False)

    def __repr__(self):
        string = "<{}(".format(self.__class__.__name__)
        for field in self.__dict__:
            string += f"{field}: {getattr(self, field)}, "
        string = string[:-2] + ")>"
        return string

    def __str__(self):
        string = "<{}(".format(self.__class__.__name__)
        for field in self.__dict__:
            string += f"{field}: {getattr(self, field)}, "
        string = string[:-2] + ")>"
        return string
