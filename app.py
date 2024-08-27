from datetime import timedelta
import os

from flask_admin import Admin, expose
from flask_admin import helpers as admin_helpers
from flask_admin.model.template import macro, EndpointLinkRowAction, LinkRowAction
from flask_admin.form import FileUploadInput, FileUploadField, Select2Field
from flask_admin.contrib.sqla import ModelView
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    request,
    render_template,
    url_for,
    g,
    session,
)
from flask_htmx import HTMX
from dotenv import load_dotenv
import sqlite3
from models.admin_users import AdminUsers
from models.event import Event
from models.gallery import Gallery
from models.rating import Rating
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from utils import Base
import random

# if not load_dotenv(os.path.join(os.getcwd(), ".env")):
#     print("No .env file found")
#     exit()
load_dotenv()

app = Flask(__name__)
htmx = HTMX(app)
DB_PATH = "data.db"
BASE_PATH = os.path.join("static", "imgs")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

sqlalchemy_db = SQLAlchemy(app)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# Flask admin setup
admin = Admin(app, name="The Royal Highlanders", template_mode="bootstrap4")


class EventView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()

    form_extra_fields = {
        "img": FileUploadField(
            "Image",
            base_path=BASE_PATH,
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
        ),
    }


class GalleryView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id", "event_id"] + self.scaffold_list_columns()

    with app.app_context():
        form_extra_fields = {
            "img": FileUploadField(
                "Image",
                base_path=BASE_PATH,
                allowed_extensions=["png", "jpg", "jpeg", "webp"],
            ),
            "event_id": Select2Field(
                "Event",
                choices=[
                    (event.id, event.title)
                    for event in sqlalchemy_db.session.query(Event).all()
                ],
            ),
        }


class RatingView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id", "event_id"] + self.scaffold_list_columns()


class AdminUsersView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


with app.app_context():
    # Configure the sqlite3 db
    # Create the events table if it doesn't exist
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, description TEXT, img BLOB, suggested BOOLEAN, rating INTEGER)"
    # )
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS gallery (id INTEGER PRIMARY KEY, img BLOB, event INTEGER, FOREIGN KEY(event) REFERENCES events(id))"
    # )
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS ratings (id INTEGER PRIMARY KEY, username TEXT, score INTEGER, event INTEGER, FOREIGN KEY(event) REFERENCES events(id))"
    # )
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
    # )
    # Create the tables if they don't exist
    Base.metadata.create_all(sqlalchemy_db.engine)
    # Create the admin user if it doesn't exist
    if not sqlalchemy_db.session.query(AdminUsers).first():
        admin_user = AdminUsers(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        sqlalchemy_db.session.add(admin_user)
        sqlalchemy_db.session.commit()
    admin.add_view(EventView(Event, sqlalchemy_db.session))
    # Generic model view for genres, forms, and artists
    admin.add_view(GalleryView(Gallery, sqlalchemy_db.session))
    admin.add_view(RatingView(Rating, sqlalchemy_db.session))
    admin.add_view(AdminUsersView(AdminUsers, sqlalchemy_db.session))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    counter = 0
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        print(admin_username)
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        print(admin_password)

        if username == admin_username and password == admin_password:
            session["username"] = username
            session["password"] = password
            print("Redirecting to admin")
            return redirect("/admin")
        else:
            counter += 1
            if counter == 3:
                return redirect("/")
            return render_template("admin_login.html")
    elif request.method == "GET":
        return render_template("admin_login.html")


@app.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
    session.pop("username", None)
    session.pop("password", None)
    return redirect("/")


# Configure session
@app.before_request
def make_session_permanent():
    session.permanent = True
    # Make the session last for a year
    app.permanent_session_lifetime = timedelta(days=365)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    # Royal Highlanders logo in background
    # Upcoming event
    # Gallery Carousel
    # About us (every member of MCUT hall club)
    # Contacts in footer
    return render_template("index.html")


@app.route("/events")
def events():
    return render_template("events.html")


@app.route("/events/<int:event_id>")
def event(event_id):
    return render_template("event.html", id=event_id)


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/election")
def election():
    # Candidates
    return render_template("election.html")


@app.route("/declare_candidacy")
def election():
    # Candidates
    return render_template("election.html")


@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


if __name__ == "__main__":
    app.run(debug=True)
