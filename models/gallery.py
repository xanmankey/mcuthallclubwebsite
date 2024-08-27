from db import db


class Gallery(db.Model):
    __tablename__ = "gallery"

    img = db.Column(db.String, nullable=False)
    event_id = db.Column(db.ForeignKey("events.id"))

    event = db.relationship("Event", backref="Gallery", uselist=False)

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
