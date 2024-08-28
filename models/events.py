from db import db


class Event(db.Model):
    __tablename__ = "events"

    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    img = db.Column(db.String, nullable=False)

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
