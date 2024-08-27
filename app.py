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
    render_template,
    request,
    url_for,
    g,
    session,
)
from flask_htmx import HTMX

from models.models import Event, Gallery, Role, User, Vote, Feedback
from datetime import timedelta
from dotenv import load_dotenv
import random
from db import DATABASE_URL, db
from jinjax import Catalog

# if not load_dotenv(os.path.join(os.getcwd(), ".env")):
#     print("No .env file found")
#     exit()
load_dotenv()

app = Flask(__name__)
htmx = HTMX(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
COMPONENTS_DIR = "components"
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"
catalog = Catalog(jinja_env=app.jinja_env)
catalog.add_folder(COMPONENTS_DIR)
catalog.add_folder(TEMPLATES_DIR)
app.jinja_env.globals["catalog"] = catalog
app.wsgi_app = catalog.get_middleware(
    app.wsgi_app,
    autorefresh=app.debug,
)

# Flask admin setup
admin = Admin(app, name="The Royal Highlanders", template_mode="bootstrap4")


def check_all_leadership_roles(names):
    if (
        "ra" in names
        or "president" in names
        or "vice_president" in names
        or "treasurer" in names
        or "secretary" in names
        or "grand_prix_rep" in names
        or "resident_satisfaction_committee_head" in names
        or "purchasing_committee_head" in names
        or "event_committee_head" in names
        or "hall_club_representation_committee_head" in names
    ):
        return True
    return False


def initialize_db():
    db.create_all()
    Role.create(name="ra", is_electable=False)
    Role.create(name="president", is_electable=True)
    Role.create(name="vice_president", is_electable=True)
    Role.create(name="treasurer", is_electable=True)
    Role.create(name="secretary", is_electable=True)
    Role.create(name="grand_prix_rep", is_electable=True)
    Role.create(name="resident_satisfaction_committee_head", is_electable=True)
    Role.create(name="purchasing_committee_head", is_electable=True)
    Role.create(name="event_committee_head", is_electable=True)
    Role.create(name="hall_club_representation_committee_head", is_electable=True)
    Role.create(name="resident_satisfaction_committee", is_electable=False)
    Role.create(name="purchasing_committee", is_electable=False)
    Role.create(name="event_committee", is_electable=False)
    Role.create(name="hall_club_representation_committee", is_electable=False)
    Role.create(name="member", is_electable=False)


class EventView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(email=session.get("email"), password=session.get("password"))
            .first()
        )
        if user is None:
            return False
        user = user[0]
        names = [role.name for role in user.roles]
        if (
            "ra" in names
            or "president" in names
            or "event_committee_head" in names
            or "secretary" in names
            or "vice_president" in names
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()

    form_extra_fields = {
        "img": FileUploadField(
            "Image",
            base_path=os.path.join(STATIC_DIR, "uploads", "images"),
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
        ),
    }


class GalleryView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(email=session.get("email"), password=session.get("password"))
            .first()
        )
        if user is None:
            return False
        user = user[0]
        names = [role.name for role in user.roles]
        if check_all_leadership_roles(names):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()

    form_extra_fields = {
        "img": FileUploadField(
            "Image",
            base_path=os.path.join(STATIC_DIR, "uploads", "images"),
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
        ),
    }


class FeedbackView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(email=session.get("email"), password=session.get("password"))
            .first()
        )
        if user is None:
            return False
        user = user[0]
        names = [role.name for role in user.roles]
        if (
            "ra" in names
            or "president" in names
            or "vice_president" in names
            or "secretary" in names
            or "resident_satisfaction_committee_head" in names
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


class RoleView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(email=session.get("email"), password=session.get("password"))
            .first()
        )
        if user is None:
            return False
        user = user[0]
        names = [role.name for role in user.roles]
        if "ra" in names or "president" in names or "secretary" in names:
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


class UserView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(email=session.get("email"), password=session.get("password"))
            .first()
        )
        if user is None:
            return False
        user = user[0]
        names = [role.name for role in user.roles]
        if (
            "ra" in names
            or "president" in names
            or "resident_satisfaction_committee_head" in names
            or "secretary" in names
            or "vice_president" in names
        ):
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


class VoteView(ModelView):
    def is_accessible(self):
        user = (
            User.query()
            .filter(email=session.get("email"), password=session.get("password"))
            .first()
        )
        if user is None:
            return False
        user = user[0]
        names = [role.name for role in user.roles]
        if "ra" in names:
            return True
        return False

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


with app.app_context():
    admin.add_view(EventView(Event, db.session))
    admin.add_view(GalleryView(Gallery, db.session))
    admin.add_view(FeedbackView(Feedback, db.session))
    admin.add_view(RoleView(Role, db.session))
    admin.add_view(UserView(User, db.session))
    admin.add_view(VoteView(Vote, db.session))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    counter = 0
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter(email=email, password=password).first()

        names = [role.name for role in user.roles]

        if check_all_leadership_roles(names):
            session["email"] = email
            session["password"] = password
            print("Redirecting to admin")
            return redirect("/admin")
        else:
            counter += 1
            if counter == 3:
                return redirect("/")
            return catalog.render("admin_login")
    elif request.method == "GET":
        return catalog.render("admin_login")


@app.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
    session.pop("email", None)
    session.pop("password", None)
    return redirect("/")


# Configure session
@app.before_request
def make_session_permanent():
    session.permanent = True


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    gallery_imgs = Gallery.query(Gallery.img).all()
    users = User.query()
    execs = []
    for user in users:
        names = [role.name for role in user.roles]
        if check_all_leadership_roles(names):
            execs.append(user)
    # return catalog.render("index", gallery_imgs=gallery_imgs, execs=execs)


@app.route("/events")
def events():
    return catalog.render("events")


@app.route("/events/<int:event_id>")
def event(event_id):
    return catalog.render("event", id=event_id)


@app.route("/sharktank")
def sharktank():
    return catalog.render("sharktank")


@app.route("/gallery")
def gallery():
    return catalog.render("gallery")


@app.route("/election")
def election():
    return catalog.render("election")


@app.route("/declare_candidacy", methods=["GET", "POST"])
def declare_candidacy():
    return catalog.render("declare_candidacy")


@app.route("/vote", methods=["GET", "POST"])
def vote():
    return catalog.render("vote")


@app.route("/feedback")
def feedback():
    return catalog.render("feedback")


if __name__ == "__main__":
    try:
        initialize_db()
    except Exception as e:
        print(e)
        pass
    app.run(debug=True)
